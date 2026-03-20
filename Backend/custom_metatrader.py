from MetaTrader5 import *
import pandas as pd

_TIMEFRAME_MAPPING = {name.split('_')[1]: globals()[name] for name in dir() if name.startswith("TIMEFRAME_")}

def open_position(type, symbol, volume=0.0, price=None, *, sl_points=0, tp_points=0,
                  deviation=0, magic=0, comment=None, retries=10):
    
    if price is not None:
        request = _request(type, symbol, volume, price, sl_points=sl_points, tp_points=tp_points,
                           deviation=deviation, magic=magic, comment=comment)
        if request is None:
            print("Invalid order request")
            return None
       
        return order_send(request) 
    
    response = None
    for tries in range(retries):
        request = _request(type, symbol, volume, None, sl_points=sl_points, tp_points=tp_points, deviation=deviation, magic=magic, comment=comment)
        if request is None:
            continue
        
        response = order_send(request)
        if response is None:
            return None
        if response.retcode != TRADE_RETCODE_REQUOTE and response.retcode != TRADE_RETCODE_PRICE_OFF:
            return response
        
    return response

def get_position_count(*, symbol=None, type=None, magic=None):
    if symbol is None:
        positions = positions_get()
    else:
        positions = positions_get(symbol=symbol)
        
    if positions is None:
        return 0
    
    positions = [position for position in positions
                    if (type is None or position.type == type) and 
                    (magic is None or position.magic == magic)]
    
    return len(positions)

def get_rates_frame(symbol, timeframe, start=None, count=None):
    rates = copy_rates_from_pos(symbol, timeframe, start, count)
    if rates is None:
        print('No rates data retrieved')
        return None
    
    rates_frame = pd.DataFrame(rates)
    rates_frame.rename(columns={'time': 'Time', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    rates_frame['Time'] = pd.to_datetime(rates_frame['Time'], unit='s')
    
    return rates_frame

def get_rates_frame_range(symbol, timeframe, start_time, end_time):
    
    rates = copy_rates_range(symbol, timeframe, start_time, end_time)
    if rates is None:
        print('No rates data retrieved')
        return None
    
    rates_frame = pd.DataFrame(rates)
    rates_frame.rename(columns={'time': 'Time', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    rates_frame['Time'] = pd.to_datetime(rates_frame['Time'], unit='s')
    
    return rates_frame
        
def timeframe_value(name):
    return(_TIMEFRAME_MAPPING.get(name))
        
def _request(type, symbol, volume, price=None, *, sl_points=0, tp_points=0, 
             deviation=10, magic=0, comment=None):
    
    if price is None:
        price_info = symbol_info_tick(symbol)
        if price_info is None:
            print(f"Failed to get price for symbol {symbol}")
            return None
        
        if type == ORDER_TYPE_BUY:
            trade_price = price_info.ask
            sl = trade_price - (sl_points * 10 * symbol_info(symbol).point)
            tp = trade_price + (tp_points * 10 * symbol_info(symbol).point)
        else:
            trade_price = price_info.bid
            sl = trade_price + (sl_points * 10 * symbol_info(symbol).point)
            tp = trade_price - (tp_points * 10 * symbol_info(symbol).point)
            
    else:
        trade_price = price
        if type == ORDER_TYPE_BUY:
            sl = trade_price - (sl_points * 10 * symbol_info(symbol).point)
            tp = trade_price + (tp_points * 10 * symbol_info(symbol).point)
        else:
            sl = trade_price + (sl_points * 10 * symbol_info(symbol).point)
            tp = trade_price - (tp_points * 10 * symbol_info(symbol).point)
        
    request = {
        "action"  : TRADE_ACTION_DEAL,
        "symbol" : symbol,
        "volume" : volume,
        "type" : type,
        "price" : trade_price,
        "sl" : sl,
        "tp" : tp,
        "magic" : magic,
        "deviation" : deviation
    }
    
    if comment is not None:
        request["comment"] = comment
        
    return request