from sqlmodel import Session, select, create_engine
from models.Strategy import Strategy

engine = create_engine("postgresql://postgres:postgresPass@localhost:5432/PropFirmDb")

def get_session():
    with Session(engine) as session:
        return session

def get_strategy_by_name(strategy_name : str, user_id : int):
    session = get_session()
    statement = select(Strategy).where(Strategy.strategyname == strategy_name, Strategy.userid == user_id)
    results = session.exec(statement)
    strategy = results.first()
    session.close()
    return strategy

def create_strategy(strategy_name : str, classname : str, user_id : int):
    session = get_session()
    strategy = Strategy(strategyname=strategy_name, classname=classname, userid=user_id)
    session.add(strategy)
    session.commit()
    session.close()