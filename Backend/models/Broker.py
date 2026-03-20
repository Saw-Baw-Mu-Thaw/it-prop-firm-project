from sqlmodel import SQLModel, Field

class BrokerAcc(SQLModel, table=True):
    __tablename__ = "broker"
    brokerId : int = Field(default=None, primary_key=True)
    userId : int = Field(default=None, foreign_key="users.userid")
    brokerLogin : str = Field(default=None)
    brokerPassword : str = Field(default=None)
    brokerName : str = Field(default='MetaQuotes')