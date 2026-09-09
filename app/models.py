
from database import local_session,Base
from sqlalchemy import Column,String,Integer,ForeignKey

session = local_session()

class users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_name = Column(String)
    password = Column(String)
    token = Column(String)
    token_time = Column(Integer)

class boxes(Base):
    __tablename__ = "boxes"
    id = Column(Integer,primary_key=True,autoincrement=True)
    user = Column(String)
    box_number = Column(Integer)
    card_name = Column(String)
    description = Column(String)

session.query(users).delete()
session.commit()