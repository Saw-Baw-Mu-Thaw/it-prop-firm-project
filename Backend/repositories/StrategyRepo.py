from sqlmodel import Session, select, create_engine
from models.Strategy import Strategy
import dotenv
import os

dotenv.load_dotenv()
conn_string = os.getenv("DB_CONN", "postgresql://postgres:postgresPass@localhost:5432/PropFirmDb")

engine = create_engine(conn_string)

def get_session():
    with Session(engine) as session:
        return session

def get_strategy_by_name(strategy_name : str, user_id : int):
    session = get_session()
    statement = select(Strategy).where(Strategy.strategyName == strategy_name, Strategy.userId == user_id)
    results = session.exec(statement)
    strategy = results.first()
    session.close()
    return strategy

def create_strategy(strategy_name : str, classname : str, user_id : int):
    session = get_session()
    strategy = Strategy(strategyName=strategy_name, classname=classname, userId=user_id)
    session.add(strategy)
    session.commit()
    session.close()
    
def get_strategies_by_user_id(user_id : int):
    session = get_session()
    statement = select(Strategy).where(Strategy.userId == user_id)
    results = session.exec(statement)
    strategies = results.all()
    session.close()
    return strategies