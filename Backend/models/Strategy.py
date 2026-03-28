from sqlmodel import SQLModel, Field
from datetime import datetime

class Strategy(SQLModel, table=True):
    __tablename__ = "strategy"
    strategyId : int = Field(default=None, primary_key=True)
    userId : int = Field(foreign_key="users.userId")
    strategyName : str = Field(default=None)
    created : datetime = Field(default_factory=datetime.now)
    classname : str = Field(default=None)