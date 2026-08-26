
from fastapi import APIRouter
from database import local_session

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

# get user
# add user
# rename
# change password
# delete user

def login():
    pass

def signup():
    pass

def rename():
    pass

def change_password():
    pass

def delete_user():
    pass