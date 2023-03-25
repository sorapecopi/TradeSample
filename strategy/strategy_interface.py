import abc


class StrategyInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_buy(self, df_candle):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def is_sell(self, df_candle):
        raise NotImplementedError()
