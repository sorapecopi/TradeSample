import datetime
import unittest
# import sys
# print(sys.path)
from mt5.mt5_terminal import Mt5Terminal
from utils import JST

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mt5 = Mt5Terminal()

    @unittest.skip('skip test...')
    def test_get_candle_from(self):
        df_ret = self.mt5.get_candle_from(
            'USDJPY',
            'M5',
            count=100,
            past_idx=0)
        print(df_ret)
        self.assertEqual(True, not df_ret.empty)


    # @unittest.skip('skip test...')
    def test_get_candle_from_to(self):
        to_time = datetime.datetime.now(tz=JST)
        from_time = to_time - datetime.timedelta(days=2)
        df_ret = self.mt5.get_candle_from_to(
            'USDJPY',
            'M5',
            from_time,
            to_time)
        print(df_ret)
        self.assertEqual(True, not df_ret.empty)


    @unittest.skip('skip test...')
    def test_get_ticks_from(self):
        from_time = datetime.datetime(2023, 12, 11, tzinfo=JST)
        df_tick = self.mt5.get_ticks_from(
            'USDJPY',
            from_time,
            count=100)
        print(df_tick)
        self.assertEqual(True, not df_tick.empty)

    @unittest.skip('skip test...')
    def test_get_ticks_from(self):
        from_time = datetime.datetime(2023, 12, 11, tzinfo=JST)
        to_time = datetime.datetime(2023, 12, 12, tzinfo=JST)
        df_tick = self.mt5.get_ticks_from_to(
            'USDJPY',
            from_time,
            to_time)
        print(len(df_tick))
        print(df_tick.index[0], '～', df_tick.index[-1])
        self.assertEqual(True, not df_tick.empty)

if __name__ == '__main__':
    unittest.main()
