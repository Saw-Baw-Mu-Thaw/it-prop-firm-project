import datetime
from fastapi import Depends, FastAPI, HTTPException
import dotenv
import os
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta, datetime
from repositories import UserRepo, BrokerRepo, StrategyRepo
from models.InputModels import BackTestInput, BrokerInput, Token, StrategyCreateInput
import importlib
import custom_metatrader as mt5
from custom_backtesting import CustomBacktest
import textwrap

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Prop Trading Firm API", version="1.0")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def root():
    return {"message" : "You've reached the digital prop trading firm"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserRepo.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")   
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires) 
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/connect")
async def connect(input : BrokerInput, token: str = Depends(oauth2_scheme)):
    if mt5.initialize(login=input.login, password=input.password):
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        user = UserRepo.get_user(username)
        BrokerRepo.add_broker(user_id=user.userid, login=input.login, password=input.password)
        return {"message" : "Connection to broker successful"}
    else:
        raise HTTPException(status_code=400, detail="Failed to connect to broker. Check credentials and try again.")

@app.post("/backtest")
async def backtest(input : BackTestInput, token: str = Depends(oauth2_scheme)):
    username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    user = UserRepo.get_user(username)
    brokerAcc = BrokerRepo.get_broker(user.userid)
    
    if mt5.initialize(login=brokerAcc.brokerLogin, password=brokerAcc.brokerPassword):
        # perform backtest using input parameters
        timeframe = mt5.timeframe_value(input.timeframe)
        from_date = datetime.strptime(input.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(input.to_date, "%Y-%m-%d")
        history = mt5.get_rates_frame_range(input.symbol, timeframe, from_date, to_date)
        
    strategy_module = importlib.import_module(f"strategy.{input.strategy}")
    strategy_class = getattr(strategy_module, input.strategy)
    config = {
        "testing" : True
    }
    
    runner = CustomBacktest(history, strategy_class, config=config, cash=input.cash, hedging=input.hedging, spread=input.spread,
                            commission=input.commission, trade_on_close=input.trade_on_close, exclusive_orders=input.exclusive_orders)
    
    results = runner.run()
    return results.to_json()
        
template = '''
from ..custom_backtesting import CustomStrategy 
from talib import *

class {}(CustomStrategy):
    def init(self):
        {}
        
    def next(self):
        {}
        
    def calc_indicators(self):
        {}
'''

def indent_code(code):
    lines = code.split('\n')
    for i in range(1, len(lines)):
        lines[i] = '    ' + '    ' + lines[i]
    return '\n'.join(lines)

@app.post("/strategy")
async def create_strategy(input : StrategyCreateInput, token: str = Depends(oauth2_scheme)):

    username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    user = UserRepo.get_user(username)
    StrategyRepo.create_strategy(strategy_name=input.name, classname=input.name,
                                 user_id=user.userId)
    
    with open(f"strategy/{input.name}.py", "w") as f:
        init_code = indent_code(input.init)
        next_code = indent_code(input.next)
        calc_indicators_code = indent_code(input.calc_indicators)
        text = template.format(input.name, init_code, next_code, calc_indicators_code)
        f.write(text)
        
    return {"message" : "Strategy created successfully"}

@app.get("/strategy")
async def get_strategies(token: str = Depends(oauth2_scheme)):
    username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    user = UserRepo.get_user(username)
    strategies = StrategyRepo.get_strategies_by_user_id(user.userId)
    return strategies