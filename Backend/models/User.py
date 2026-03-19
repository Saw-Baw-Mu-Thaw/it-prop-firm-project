from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    userid : int = Field(default=None, primary_key=True)
    username : str = Field(default=None)
    password : str = Field(default=None)   
    