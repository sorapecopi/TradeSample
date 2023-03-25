import datetime
import pandas as pd
from mt5.mt5_terminal import Mt5Terminal
from analyzer.indicator import macd_dw, macd_up, get_macd, bb, rsi
from utils import get_one_pips

from strategy.strategy_interface import StrategyInterface

class MacdBbRsi(StrategyInterface):
    def is_buy(self, df_candle):
        buy = False
        df_candle = bb(df_candle, timeperiod=60*6)
        last_row = df_candle.iloc[-1]
        if last_row.bb2p < last_row.low:
            rsi_value = rsi(df_candle, timeperiod=60*3)
            if rsi_value.values[-1] < 70 and macd_up(df_candle, slow=50, fast=20, smooth=7, limitv=10*0.01):
                buy = True
        return buy


    def is_sell(self, df_candle):
        sell = False
        df_candle = bb(df_candle, timeperiod=60*6)
        last_row = df_candle.iloc[-1]
        if last_row.bb2m > last_row.high:
            rsi_value = rsi(df_candle, timeperiod=60*3)
            if rsi_value.values[-1] > 30 and macd_dw(df_candle, slow=50, fast=20, smooth=7, limitv=10*0.01):
                sell = True
        return sell
