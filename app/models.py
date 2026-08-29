
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

class cards(Base):
    __tablename__ = "cards"
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    card_name = Column(String)
    description = Column(String)

class box1(Base):
    __tablename__ = "box1"
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    card_name = Column(String)
    description = Column(String)

class box2(Base):
    __tablename__ = "box2"
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    card_name = Column(String)
    description = Column(String)

class box3(Base):
    __tablename__ = "box3"
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    card_name = Column(String)
    description = Column(String)

class box4(Base):
    __tablename__ = "box4"
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    card_name = Column(String)
    description = Column(String)

class box5(Base):
    __tablename__ = "box5"
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True)
    card_name = Column(String)
    description = Column(String)