import datetime
import numpy as np
import pandas as pd
import time
import MetaTrader5 as mt5

from utils import is_summer_time, JST
UTC = datetime.timezone.utc

class Mt5Terminal:

    def __init__(self):
        ok = False
        for i in range(120):
            if mt5.initialize(path=r"C:\\Program Files\\OANDA MetaTrader 5\\terminal64.exe"):
                ok = True
                break
            else:
                print("initialize() failed, error code =", mt5.last_error())
                time.sleep(60)
        if not ok:
            raise Exception("initialize() failed, error code =", mt5.last_error())

    @property
    def zonemt5(self):
        #GMT+2（夏時間の場合はGMT+3）
        jst_time = datetime.datetime.now(tz=JST)
        # jst_time = datetime.datetime.now()
        if is_summer_time(jst_time):
            return datetime.timedelta(hours=3)
        else:
            return datetime.timedelta(hours=2)

    def _convert_timerate_granularity_to_mt5(self, granularity):
        ret_timerate = None
        if granularity == 'M1':
            ret_timerate = mt5.TIMEFRAME_M1
        elif granularity == 'M2':
            ret_timerate = mt5.TIMEFRAME_M2
        elif granularity == 'M3':
            ret_timerate = mt5.TIMEFRAME_M3
        elif granularity == 'M5':
            ret_timerate = mt5.TIMEFRAME_M5
        elif granularity == 'M15':
            ret_timerate = mt5.TIMEFRAME_M15
        elif granularity == 'M30':
            ret_timerate = mt5.TIMEFRAME_M30
        elif granularity == 'H1':
            ret_timerate = mt5.TIMEFRAME_H1
        elif granularity == 'H4':
            ret_timerate = mt5.TIMEFRAME_H4
        elif granularity == 'H6':
            ret_timerate = mt5.TIMEFRAME_H6
        elif granularity == 'D':
            ret_timerate = mt5.TIMEFRAME_D1
        elif granularity == 'W':
            ret_timerate = mt5.TIMEFRAME_W1
        elif granularity == 'M':
            ret_timerate = mt5.TIMEFRAME_MN1
        else:
            raise Exception("ERROR:unsupport:",granularity)
        return ret_timerate

    def get_candle_from(self, symbol, granularity, count=2000, past_idx=0):
        '''

        :param symbol: ドル円の場合"USDUPY"
        :param granularity: 五分足の場合"M5"
        :param count: 取得数
        :param past_idx: 取得開始index indexは現在から過去になるほど増える 現在が0
        :return:
        '''
        timerate = self._convert_timerate_granularity_to_mt5(granularity)
        rates = mt5.copy_rates_from_pos(symbol, timerate, past_idx, count)
        rates_frame = pd.DataFrame(rates)
        try:
            rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        except Exception as e:
            print("ERROR: get_candle_from", symbol, granularity, count, datetime.datetime.now())
            raise e
        rates_frame.loc[:, 'time'] = rates_frame.time - self.zonemt5 #mt5時間対応
        df = rates_frame.set_index('time')
        df = df.tz_localize(UTC).tz_convert(JST)
        if 'volume' not in df.columns:
            if 'tick_volume' in df.columns:
                df = df.rename(columns={'tick_volume': 'volume'})
        return df

    def _tz_del(self, tgt_time):
        if tgt_time is not None:
            if type(tgt_time) is datetime.datetime:
                if tgt_time.tzinfo == UTC:
                    pass
                elif tgt_time.tzinfo is None:
                    tgt_time = tgt_time.replace(tzinfo=UTC)
                elif str(tgt_time.tzinfo).startswith('UTC') or str(tgt_time.tzinfo).startswith('MT5'):
                    tgt_time = tgt_time.astimezone(UTC)
                elif tgt_time.tzinfo is not None and (tgt_time.tzinfo == JST or tgt_time.tzinfo.zone == 'Asia/Tokyo'):
                    tgt_time = tgt_time.astimezone(UTC)
                else:
                    raise Exception(tgt_time)
            elif type(tgt_time) is pd.Timestamp:
                if tgt_time.tzinfo == UTC:
                    pass
                else:
                    tgt_time = tgt_time.tz_convert(UTC)
                    tgt_time = tgt_time.to_pydatetime()
            elif type(tgt_time) is np.datetime64:
                tgt_time = pd.to_datetime(tgt_time, unit='s')
                tgt_time = tgt_time.tz_localize(UTC)
                tgt_time = tgt_time.to_pydatetime()
            else:
                print(type(tgt_time))
                raise Exception(tgt_time)
        return tgt_time

    def get_ticks_from(self, symbol, from_time, count=1000):
        '''

        @param symbol: EURUSDなど
        @param from_time: この日時以降のtickデータを取得 (from)
        @param count: 取得データ数
        @return:
        '''
        UTC = datetime.timezone.utc
        mt5_from = self._tz_del(from_time) + self.zonemt5
        ticks = mt5.copy_ticks_from(symbol, mt5_from.timestamp(), count, mt5.COPY_TICKS_ALL)
        # 取得したデータからDataFrameを作成する
        if ticks is None:
            raise Exception("get_ticks_from_to get fail sym:{} from:{} count:{}".format(
                symbol, from_time, count
            ))
        ticks_frame = pd.DataFrame(ticks)
        # 秒での時間をdatetime形式に変換する
        ticks_frame.loc[:, 'time_ms'] = pd.to_datetime(ticks_frame['time_msc'], unit='ms') - self.zonemt5
        try:
            ticks_frame.loc[:, 'time'] = pd.to_datetime(ticks_frame['time'], unit='s') - self.zonemt5
        except Exception as e:
            print("Exception '{}' in get_ticks".format(e))
            print(symbol, mt5_from, count, datetime.datetime.now())
            raise e
        ticks_frame.loc[:, 'time_tmp'] = ticks_frame.time_ms
        ticks_frame = ticks_frame.set_index('time_tmp')
        ticks_frame = ticks_frame.tz_localize(UTC).tz_convert(JST)
        ticks_frame['time'] = ticks_frame.index
        if not 'volume' in ticks_frame.columns and 'tick_volume' in ticks_frame.columns:
            ticks_frame.loc[:, 'volume'] = ticks_frame['tick_volume']
        return ticks_frame


    def get_candle_from_to(self, symbol, granularity, time_from, time_to):
        '''
        ローソク足をfromからtoまで取得
        :param symbol:
        :param granularity:
        :param time_from:
        :param time_to:
        :return:
        '''
        if time_to is None:
            time_to = datetime.datetime.now(tz=UTC)
        timerate = self._convert_timerate_granularity_to_mt5(granularity)
        mt5_from = self._tz_del(time_from) + self.zonemt5
        mt5_to = self._tz_del(time_to) + self.zonemt5
        rates = mt5.copy_rates_range(symbol, timerate, mt5_from, mt5_to)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s') - self.zonemt5
        rates_frame = rates_frame.copy()
        rates_frame['time'] = rates_frame.time
        df = rates_frame.set_index('time')
        df = df.tz_localize(UTC).tz_convert(JST)
        if 'volume' not in df.columns:
            if 'tick_volume' in df.columns:
                df = df.rename(columns={'tick_volume': 'volume'})
        return df

    
    def get_ticks_from_to(self, symbol, from_time, to_time):
        mt5_from = self._tz_del(from_time) + self.zonemt5
        mt5_to = self._tz_del(to_time) + self.zonemt5
        ticks = mt5.copy_ticks_range(symbol, mt5_from.timestamp(), mt5_to.timestamp(), mt5.COPY_TICKS_ALL)
        # 取得したデータからDataFrameを作成する
        if ticks is None:
            raise Exception("get_ticks_from_to get fail sym:{} from:{} to:{}".format(
                symbol, from_time, to_time
            ))
        ticks_frame = pd.DataFrame(ticks)
        # 秒での時間をdatetime形式に変換する
        ticks_frame.loc[:, 'time_ms'] = pd.to_datetime(ticks_frame['time_msc'], unit='ms') - self.zonemt5
        try:
            ticks_frame.loc[:, 'time'] = pd.to_datetime(ticks_frame['time'], unit='s') - self.zonemt5
        except Exception as e:
            print("Exception '{}' in get_ticks".format(e))
            print(symbol, mt5_from, to_time, datetime.datetime.now())
            raise e
        ticks_frame.loc[:, 'time_tmp'] = ticks_frame.time_ms
        ticks_frame = ticks_frame.set_index('time_tmp')
        ticks_frame = ticks_frame.tz_localize(UTC).tz_convert(JST)
        ticks_frame['time'] = ticks_frame.index
        if not 'volume' in ticks_frame.columns and 'tick_volume' in ticks_frame.columns:
            ticks_frame.loc[:, 'volume'] = ticks_frame['tick_volume']
        return ticks_frame
