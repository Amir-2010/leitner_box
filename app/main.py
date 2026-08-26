
from fastapi import FastAPI
from database import local_session
from sqlalchemy import Session

app = FastAPI()