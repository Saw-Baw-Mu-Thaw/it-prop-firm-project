from sqlmodel import SQLModel, Field
from datetime import datetime

class Strategy(SQLModel, table=True):
    __tablename__ = "strategy"
    strategyid : int = Field(default=None, primary_key=True)
    userid : int = Field(foreign_key="users.userid")
    strategyname : str = Field(default=None)
    created : datetime = Field(default_factory=datetime.now)
    classname : str = Field(default=None)