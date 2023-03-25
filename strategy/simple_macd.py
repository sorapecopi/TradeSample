import pandas as pd
from mt5.mt5_terminal import Mt5Terminal
from analyzer.indicator import macd_dw, macd_up, get_macd
from utils import get_one_pips

from strategy.strategy_interface import StrategyInterface

class SimpleMacd(StrategyInterface):
    def is_buy(self, df_candle):
        df_macd = get_macd(df_candle, slow=26*5, fast=12*5, smooth=9*5)
        return macd_up(df_macd)
        

    def is_sell(self, df_candle):
        df_macd = get_macd(df_candle, slow=26*5, fast=12*5, smooth=9*5)
        return macd_dw(df_macd)
