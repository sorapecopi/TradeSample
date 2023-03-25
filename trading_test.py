import datetime
import pandas as pd
from mt5.mt5_terminal import Mt5Terminal
from analyzer.indicator import macd_dw, macd_up
from utils import get_one_pips
from strategy.simple_macd import SimpleMacd
from strategy.macd_bb_rsi import MacdBbRsi

def main():
    instrument = 'USDJPY'
    onepips = get_one_pips(instrument)
    mt5 = Mt5Terminal()
    # stratgy = SimpleMacd()
    stratgy = MacdBbRsi()
    last_idx = None
    mergin_count = 0
    order = None
    trade_history = []
    for past_idx in range(28800, -1, -1):
        if last_idx is None:
            df_candle = mt5.get_candle_from(
                        instrument,
                        'M1',
                        count=2000,
                        past_idx=past_idx)
            last_idx = df_candle.index[-1]
            # print(df_candle.index[-1])
            current_time = last_idx + datetime.timedelta(minutes=1)
        else:
            df_candle_tmp = mt5.get_candle_from(
                        instrument,
                        'M1',
                        count=1,
                        past_idx=past_idx+mergin_count)
            # print(df_candle_tmp.index[-1], last_idx, past_idx+mergin_count)
            if last_idx + datetime.timedelta(minutes=1) < df_candle_tmp.index[-1] and last_idx + datetime.timedelta(hours=1) > df_candle_tmp.index[-1]:
                # データかけ
                print(f"set pre data {last_idx} to {last_idx + datetime.timedelta(minutes=1)}")
                mergin_count += 1
                df_candle.loc[last_idx + datetime.timedelta(minutes=1)] = df_candle.loc[last_idx]
            else:
                df_candle = df_candle.combine_first(df_candle_tmp)
            if len(df_candle) > 2000:
                df_candle = df_candle.iloc[-2000:]
            last_idx = df_candle.index[-1]
            current_time = last_idx + datetime.timedelta(minutes=1)
        

        if order is None:
            # if current_time.day == 7 and \
            #     current_time.hour == 14 and \
            #     current_time.minute == 20:
            #     print("check!!")
            if stratgy.is_sell(df_candle):
                ticks = mt5.get_ticks_from(instrument, current_time, 10)
                print(f"SELL:time:{current_time} price:{ticks.iloc[0].bid}")
                order = {
                    'start_time': current_time,
                    'start_price': ticks.iloc[0].bid,
                    'action': 'SELL'
                }
            elif stratgy.is_buy(df_candle):
                ticks = mt5.get_ticks_from(instrument, current_time, 10)
                print(f"BUY:time:{current_time} price:{ticks.iloc[0].ask}")
                order = {
                    'start_time': current_time,
                    'start_price': ticks.iloc[0].ask,
                    'action': 'BUY'
                }
        else:
            ticks = mt5.get_ticks_from_to(instrument, order['start_time'], current_time)
            getpips = 30
            losspips = 15
            get_r = False
            loss_r = False
            end_time = None
            end_price = None
            if order['action'] == 'BUY':
                if any(ticks.bid > order['start_price'] + onepips*getpips):
                    get_r = True
                    end_time = ticks[ticks.bid > order['start_price'] + onepips*getpips].index[0]
                    end_price = ticks[ticks.bid > order['start_price'] + onepips*getpips].bid.iloc[0]
                if any(ticks.bid < order['start_price'] - onepips*losspips):
                    loss_r = True
                    end_time = ticks[ticks.bid < order['start_price'] - onepips*losspips].index[0]
                    end_price = ticks[ticks.bid < order['start_price'] - onepips*losspips].bid.iloc[0]
                if get_r and loss_r:
                    if ticks[ticks.bid > order['start_price'] + onepips*getpips].index[0] < ticks[ticks.bid < order['start_price'] - onepips*losspips].index[0]:
                        loss_r = False
                        end_time = ticks[ticks.bid < order['start_price'] - onepips*getpips].index[0]
                        end_price = ticks[ticks.bid < order['start_price'] - onepips*getpips].bid.iloc[0]
                    else:
                        get_r = False
                        end_time = ticks[ticks.bid > order['start_price'] + onepips*losspips].index[0]
                        end_price = ticks[ticks.bid > order['start_price'] + onepips*losspips].bid.iloc[0]
                
                if get_r:
                    print(f"GET {getpips}pips time:{current_time}")
                    order['result'] = 'GET'
                    order['end_time'] = end_time
                    order['end_price'] = end_price
                    trade_history.append(order)
                    order = None
                elif loss_r:
                    print(f"LOSS {losspips}pips time:{current_time}")
                    order['result'] = 'LOSS'
                    order['end_time'] = end_time
                    order['end_price'] = end_price
                    trade_history.append(order)
                    order = None
            elif order['action'] == 'SELL':
                end_time = None
                end_price = None
                if any(ticks.ask < order['start_price'] - onepips*getpips):
                    get_r = True
                    end_time = ticks[ticks.ask < order['start_price'] - onepips*getpips].index[0]
                    end_price = ticks[ticks.ask < order['start_price'] - onepips*getpips].ask.iloc[0]
                if any(ticks.ask > order['start_price'] + onepips*losspips):
                    loss_r = True
                    end_time = ticks[ticks.ask > order['start_price'] + onepips*losspips].index[0]
                    end_price = ticks[ticks.ask > order['start_price'] + onepips*losspips].ask.iloc[0]
                if get_r and loss_r:
                    if ticks[ticks.ask < order['start_price'] - onepips*getpips].index[0] < ticks[ticks.ask > order['price'] + onepips*losspips].index[0]:
                        loss_r = False
                        end_time = ticks[ticks.ask < order['start_price'] - onepips*getpips].index[0]
                        end_price = ticks[ticks.ask < order['start_price'] - onepips*getpips].ask.iloc[0]
                    else:
                        get_r = False
                        end_time = ticks[ticks.ask > order['start_price'] + onepips*losspips].index[0]
                        end_price = ticks[ticks.ask > order['start_price'] + onepips*losspips].ask.iloc[0]

                if get_r:
                    print(f"GET {getpips}pips time:{current_time}")
                    order['result'] = 'GET'
                    # order['end_time']: current_time
                    order['end_time'] = end_time
                    order['end_price'] = end_price
                    trade_history.append(order)
                    order = None
                elif loss_r:
                    print(f"LOSS {losspips}pips time:{current_time}")
                    order['result'] = 'LOSS'
                    # order['end_time']: current_time
                    order['end_time'] = end_time
                    order['end_price'] = end_price
                    trade_history.append(order)
                    order = None
    # print(trade_history)
    df_result = pd.DataFrame(trade_history)
    print(f"GET {len(df_result[df_result.result == 'GET'])*30} pips count:", len(df_result[df_result.result == 'GET']))
    print(f"LOSS {len(df_result[df_result.result == 'LOSS'])*15} pips count:", len(df_result[df_result.result == 'LOSS']))
    df_result.to_csv('data/test_macd.csv')



if __name__ == '__main__':
    main()
