from datetime import datetime, time
from typing import Optional
import pandas as pd

from backtesting import Strategy, Backtest
from backtesting._util import _Data
import custom_metatrader as mt5


class CustomStrategy(Strategy):
    
    def __init__(self):
        self.config = None # config is a dictionary
        self.is_calculated = False
        
        super().__init__()
        
    def buy(self, *,
            size: float = 1.0,
            limit: Optional[float] = None,
            sl: Optional[int] = None,
            tp: Optional[int] = None,
            tag: object = None):
        
        if self.config.testing:
            return super().buy(size=size, limit=limit, sl=sl, tp=tp, tag=tag)
        
        if sl is None:
            sl = 0
        if tp is None:
            tp = 0
            
        return mt5.open_position(mt5.ORDER_TYPE_BUY, self.symbol, size, sl_points=sl, tp_points=tp, magic=self.magic)
    
    def sell(self,*,
             size: float = 1.0,
             limit: Optional[float] = None,
             sl: Optional[int] = None,
             tp: Optional[int] = None,
             tag: object = None):
        
        if self.config.testing:
            return super().sell(size=size, limit=limit, sl=sl, tp=tp, tag=tag)
        
        if sl is None:
            sl = 0
        if tp is None:
            tp = 0
            
        return mt5.open_position(mt5.ORDER_TYPE_SELL, self.symbol, size, sl_points=sl, tp_points=tp, magic=self.magic)
    
    def get_ask(self):
        if self.config.testing:
            return self.data.Close
        
        tick = mt5.symbol_info_tick(self.config.symbol)
        return tick.ask
    
    def get_bid(self):
        if self.config.testing:
            return self.data.Close
        
        tick = mt5.symbol_info_tick(self.config.symbol)
        return tick.bid
    
    def get_position_count(self, type=None):
        open_trades = 0
        
        if self.config.testing:
            if type == mt5.ORDER_TYPE_BUY:
                open_trades = sum(1 for trade in self.trades if trade.is_long)
            elif type == mt5.ORDER_TYPE_SELL:
                open_trades = sum(1 for trade in self.trades if trade.is_short)
            return open_trades
        
        return mt5.get_position_count(symbol=self.config.symbol, type=type)
    
    def recalculate_indicators(self):
        if self.config.testing and self.is_calculated:
            return
        
        if not self.config.testing:
            data = mt5.get_rates_frame(self.config.symbol, self.config.timeframe, 0, self.config.depth)
            self._data = _Data(data.copy(deep=False))
            
        self.calculate_indicators()
        self.is_calculated = True

class CustomBacktest(Backtest):
    def __init__(self, data, strategy, *,
                 config = None, cash = 10000,
                 spread = 0, commission = 0, margin = 1,
                 trade_on_close=False, hedging=False,
                 exclusive_orders=False, finalize_trades=False):
        
        self.cycle = 10
        self.testing = True
        if config:
            for name in ['cycle', 'testing']:
                if hasattr(config, name):
                    setattr(self, name, getattr(config, name))
                    
        if data is None:
            columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            value = {col: [0] for col in columns}
            value['Time'] = [datetime.now()]
            data = pd.DataFrame(value)
            data.set_index('Time', inplace=True)
            
        super().__init__(data, strategy, cash=cash, spread=spread,
                         commission=commission, margin=margin, 
                         trade_on_close=trade_on_close, hedging=hedging, 
                         exclusive_orders=exclusive_orders, finalize_trades=finalize_trades)
        
        
    def run(self, **kwargs) -> pd.Series:
        
        if self.testing:
            return super().run(**kwargs)
        
        strategy: CustomStrategy = self._strategy(None, self._data, kwargs)
        
        if not mt5.symbol_select(strategy.config.symbol):
            print(f"Failed to select symbol {strategy.config.symbol}")
            return None
        
        strategy.init()
        
        while True: # replace true with whether the user still wants to run the live session
            strategy.recalculate_indicators()
            strategy.next()
            
            # TODO: calculate how much to sleep based on time frame
            # also do we want to check at first few seconds of time frame or 
            # after a timeframe amount of time has passed since first ran
            time.sleep(self.cycle)
            
        # code to close any open position
        
        return None