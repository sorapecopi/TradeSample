import datetime
import unittest
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# import sys
# print(sys.path)
from mt5.mt5_terminal import Mt5Terminal
from utils import JST
from analyzer.indicator import *

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mt5 = Mt5Terminal()

    @unittest.skip('skip test...')
    def test_sma(self):
        df_ret = self.mt5.get_candle_from(
            'USDJPY',
            'M5',
            count=1000,
            past_idx=0)
        ret = sma(df_ret)
        print(ret)
        self.assertEqual(True, not df_ret.empty)


    @unittest.skip('skip test...')
    def test_get_macd(self):
        from_time = datetime.datetime(2023, 12, 4, 7)
        to_time = datetime.datetime(2023, 12, 12, 9)
        df_candle = self.mt5.get_candle_from_to(
            'USDJPY',
            'M1', from_time, to_time)
        df_ret = get_macd(df_candle)
        fig = go.Figure(data=[
            go.Candlestick(x=df_candle.index,
                           open=df_candle.open,
                           high=df_candle.high,
                           low=df_candle.low,
                           close=df_candle.close,
                           yaxis='y1'),
            go.Scatter(x=df_ret.index, y=df_ret.macd, name="macd", line=dict(color='blue', width=1), yaxis='y2'),
            go.Scatter(x=df_ret.index, y=df_ret.signal, name="signal", line=dict(color='red', width=1), yaxis='y2'),
        ],
        layout = go.Layout(
                yaxis = dict(title='y1', side='left', showgrid=False, range=[df_candle.low.min(), df_candle.high.max()]), 
                yaxis2 = dict(title='y2', side='right', overlaying='y', range=[min(df_ret.signal.min(), df_ret.macd.min()), max(df_ret.macd.max(), df_ret.signal.max())])
        ))
        fig.show()

        print(df_ret)
        self.assertEqual(True, not df_ret.empty)
        

    # @unittest.skip('skip test...')
    def test_get_macd2(self):
        from_time = datetime.datetime(2023, 12, 4, 7)
        to_time = datetime.datetime(2023, 12, 12, 9)
        df_candle = self.mt5.get_candle_from_to(
            'USDJPY',
            'M1', from_time, to_time)
        df_ret = get_macd(df_candle,slow=50, fast=20, smooth=7)
        fig = go.Figure(data=[
            go.Candlestick(x=df_candle.index,
                           open=df_candle.open,
                           high=df_candle.high,
                           low=df_candle.low,
                           close=df_candle.close,
                           yaxis='y1'),
            go.Scatter(x=df_ret.index, y=df_ret.macd, name="macd", line=dict(color='blue', width=1), yaxis='y2'),
            go.Scatter(x=df_ret.index, y=df_ret.signal, name="signal", line=dict(color='red', width=1), yaxis='y2'),
        ],
        layout = go.Layout(
                yaxis = dict(title='y1', side='left', showgrid=False, range=[df_candle.low.min(), df_candle.high.max()]), 
                yaxis2 = dict(title='y2', side='right', overlaying='y', range=[min(df_ret.signal.min(), df_ret.macd.min()), max(df_ret.macd.max(), df_ret.signal.max())])
        ))
        fig.show()

        print(df_ret)
        self.assertEqual(True, not df_ret.empty)


    @unittest.skip('skip test...')
    def test_rsi(self):
        from_time = datetime.datetime(2023, 12, 4, 7)
        to_time = datetime.datetime(2023, 12, 12, 9)
        df_candle = self.mt5.get_candle_from_to(
            'USDJPY',
            'M1', from_time, to_time)
        rsi14 = rsi(df_candle)
        rsixx = rsi(df_candle, timeperiod=60*2)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.2, 0.7], x_title="Date")
        fig.add_trace(go.Candlestick(x=df_candle.index,
                           open=df_candle.open,
                           high=df_candle.high,
                           low=df_candle.low,
                           close=df_candle.close,),
                        row=1, col=1)

        fig.add_trace(go.Scatter(x=rsi14.index ,y=rsi14, name= 'RSI14'), row=2, col=1)
        fig.add_trace(go.Scatter(x=rsi14.index ,y=rsixx, name= 'RSIxx'), row=3, col=1)
        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.show()

        print(rsi14)
        self.assertEqual(True, not rsi14.empty)

    @unittest.skip('skip test...')
    def test_bb(self):
        from_time = datetime.datetime(2023, 12, 4, 7)
        to_time = datetime.datetime(2023, 12, 12, 9)
        df_candle = self.mt5.get_candle_from_to(
            'USDJPY',
            'M1', from_time, to_time)
        df_ret = bb(df_candle)
        fig = go.Figure(data=[
            go.Candlestick(x=df_candle.index,
                           open=df_candle.open,
                           high=df_candle.high,
                           low=df_candle.low,
                           close=df_candle.close,),
            go.Scatter(x=df_ret.index, y=df_ret.mid, name="ma", line=dict(color='black', width=1)),
            go.Scatter(x=df_ret.index, y=df_ret.bb1m, name="-1", line=dict(color='blue', width=1)),
            go.Scatter(x=df_ret.index, y=df_ret.bb1p, name="+1", line=dict(color='blue', width=1)),
            go.Scatter(x=df_ret.index, y=df_ret.bb2m, name="-2", line=dict(color='red', width=1)),
            go.Scatter(x=df_ret.index, y=df_ret.bb2p, name="+2", line=dict(color='red', width=1)),
        ])
        fig.show()
        

if __name__ == '__main__':
    unittest.main()
