
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

sql_address = "sqlite:///D:/real projects/leitner_box/app/database.db"
engine = create_engine(sql_address)
local_session = sessionmaker(autoflush=False,autocommit=False,bind=engine)

class Base(DeclarativeBase):
    pass