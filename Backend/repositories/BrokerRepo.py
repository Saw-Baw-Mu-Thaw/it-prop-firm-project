from sqlmodel import Session, select, create_engine
from models.Broker import BrokerAcc
import dotenv
import os

dotenv.load_dotenv()
conn_string = os.getenv("DB_CONN", "postgresql://postgres:postgresPass@localhost:5432/PropFirmDb")

engine = create_engine(conn_string)

def get_session():
    with Session(engine) as session:
        return session
    
def add_broker(user_id : int, login : str, password : str, broker_name : str = 'MetaQuotes'):
    session = get_session()
    broker = BrokerAcc(userId=user_id, brokerLogin=login, brokerPassword=password, brokerName=broker_name)
    session.add(broker)
    session.commit()
    session.close()
    
def get_broker(user_id : int):
    session = get_session()
    statement = select(BrokerAcc).where(BrokerAcc.userId == user_id)
    results = session.exec(statement)
    broker = results.first()
    session.close()
    return broker