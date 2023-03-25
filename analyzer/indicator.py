import pandas as pd
import numpy as np

def sma(df_price, timeperiod=5, limit=1, column='close'):
    se_sma = df_price.loc[:, column].rolling(timeperiod).mean()
    return se_sma


def ema(df_price, timeperiod=5, limit=1, column='close'):
    se_ema = df_price.loc[:, column].ewm(span=timeperiod).mean()
    return se_ema


def ema1(df_price, timeperiod=5, column='close', limit=1):
    '''指数平滑移動平均の計算(修正版)'''
    sma = df_price.loc[:, column].rolling(timeperiod).mean()[:timeperiod]
    se_ema = pd.concat([sma, df_price.loc[:, column][timeperiod:]]).ewm(span=timeperiod, adjust=False).mean()
    return se_ema

def bb(df_candle, timeperiod=20):
    c = df_candle.close
    ma = c.rolling(window=timeperiod, min_periods=timeperiod - 1).mean()
    vol = c.rolling(window=timeperiod, min_periods=timeperiod - 1).std()

    #1シグマ
    bol1_p = pd.DataFrame(index=ma.index)
    bol1_p = ma + vol
    bol1_m = pd.DataFrame(index=ma.index)
    bol1_m = ma - vol

    #2シグマ
    bol2_p = pd.DataFrame(index=ma.index)
    bol2_p = ma + (vol * 2)
    bol2_m = pd.DataFrame(index=ma.index)
    bol2_m = ma - (vol * 2)

    #3シグマ
    bol3_p = pd.DataFrame(index=ma.index)
    bol3_p = ma + (vol * 3)
    bol3_m = pd.DataFrame(index=ma.index)
    bol3_m = ma - (vol * 3)

    df_candle.loc[:, 'mid'] = ma #ma
    df_candle.loc[:, 'bb1p'] = bol1_p #1シグマ+
    df_candle.loc[:, 'bb1m'] = bol1_m #1シグマ-
    df_candle.loc[:, 'bb2p'] = bol2_p #2シグマ+
    df_candle.loc[:, 'bb2m'] = bol2_m #2シグマ-
    df_candle.loc[:, 'bb3p'] = bol3_p #3シグマ+
    df_candle.loc[:, 'bb3m'] = bol3_m #3シグマ-

    return df_candle


def rsi(df_candle, timeperiod=14):
    # 確認: df_candle は pandas DataFrame で、'close' 列が存在する
    if not isinstance(df_candle, pd.DataFrame) or 'close' not in df_candle.columns:
        raise ValueError("df_candle must be a pandas DataFrame with a 'close' column")

    c = df_candle['close']
    diff = c.diff()

    up = diff.clip(lower=0)
    down = -diff.clip(upper=0)

    up_sma = up.rolling(window=timeperiod, center=False).mean()
    down_sma = down.rolling(window=timeperiod, center=False).mean()

    RS = up_sma / down_sma
    RSI = 100.0 - (100.0 / (1.0 + RS))

    # 最初の行にNaNを挿入し、インデックスを整理
    RSI.iloc[0] = np.nan

    return RSI


def get_macd(df_candle, slow=26, fast=12, smooth=9):
    '''
    macd を得る
    col:macd, signal, hist
        macd:macdライン、slow(長期EMA)とfast(短期EMA)の指数移動平均の差
        signal:macdシグナル、MACDのEMA
        hist:macdラインと、macdシグナルの差
    ゴールデンクロス：買い：signalをmacdがクロスして、macdが下から上に抜ける
    デッドデンクロス：売り：signalをmacdがクロスして、macdが上から下に抜ける
    追従買い：ゴールデンクロスの後、macdがマイナスからプラスに転換
    追従売り：デッドクロスの後、macdがプラスからマイナスに転換
    :param df_candle:
    :param slow:
    :param fast:
    :param smooth:
    :return:
    '''
    price = df_candle.close
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=smooth, adjust=False).mean()
    hist = macd - signal
    df = pd.concat([macd, signal, hist], axis=1)
    df.columns = ['macd', 'signal', 'hist']
    return df

def macd_dw(df_candle, slow=26, fast=12, smooth=9, limitv=None):
    if 'macd' not in df_candle.columns:
        df_macd = get_macd(df_candle, slow=slow, fast=fast, smooth=smooth)
    else:
        df_macd = df_candle
    df_up = df_macd[df_macd.signal < df_macd.macd]
    last_up = df_up.index[-1]
    df_dw = df_macd.loc[last_up:]
    if 4 > len(df_dw) > 1:
        df_dw = df_dw.iloc[1:]
        if (df_dw.signal > df_dw.macd).all():
            if limitv is None or (df_candle.iloc[-1*smooth:].high.max() - df_candle.iloc[-1].close) < limitv:
                print("MACD DW")
                return True
    return False

def macd_up(df_candle, slow=26, fast=12, smooth=9, limitv=None):
    if 'macd' not in df_candle.columns:
        df_macd = get_macd(df_candle, slow=slow, fast=fast, smooth=smooth)
    else:
        df_macd = df_candle
    df_dw = df_macd[df_macd.signal > df_macd.macd]
    last_dw = df_dw.index[-1]
    df_up = df_macd.loc[last_dw:]
    if 4 > len(df_up) > 1:
        df_up = df_up.iloc[1:]
        if (df_up.signal < df_up.macd).all():
            if limitv is None or (df_candle.iloc[-1].close - df_candle.iloc[-1*smooth:].low.min()) < limitv:
                print("MACD UP")
                return True
    return False
