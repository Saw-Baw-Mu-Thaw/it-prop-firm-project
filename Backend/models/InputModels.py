from pydantic import BaseModel

class BackTestInput(BaseModel):
    strategy : str
    symbol : str
    timeframe : str
    from_date : str
    to_date : str
    cash : float
    hedging : bool
    spread : int
    commission : float
    trade_on_close : bool
    exclusive_orders : bool
    
class BrokerInput(BaseModel):
    login : str
    password : str
    
class Token(BaseModel):
    access_token : str
    token_type : str
    
class StrategyCreateInput(BaseModel):
    name : str
    init : str
    next : str
    calc_indicators : str
    