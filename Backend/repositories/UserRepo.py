from sqlmodel import Session, select, create_engine
from models.User import User
import dotenv
import os

dotenv.load_dotenv()
conn_string = os.getenv("DB_CONN", "postgresql://postgres:postgresPass@localhost:5432/PropFirmDb")

engine = create_engine(conn_string)

def get_session():
    with Session(engine) as session:
        return session
    
def get_user(username : str):
    session = get_session()
    statement = select(User).where(User.username == username)
    results = session.exec(statement)
    user = results.first()
    session.close()
    return user