
from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import HTTPBearer
from database import local_session
from sqlalchemy.orm import Session
from models import boxes,users
from router_login import decode_token
from router_login import auth2_bearer
from datetime import date

router = APIRouter()

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

# box 1 ==> rule: add in this box first - every day
# box 2 ==> rule: every 2 days
# box 3 ==> rule: every 4 days
# box 4 ==> rule: every week
# box 5 ==> rule: every 2 week

@router.post("/create cards",tags=["box methods"])
def create_cart(word:str,description:str,db:Session=Depends(get_db),token=Depends(auth2_bearer)):
    query = db.query(users)
    user_name = decode_token.name(token)
    result = query.where(users.user_name==user_name).one_or_none()
    if result:
        query = db.query(boxes)
        result = query.where(boxes.card_name==word,boxes.user==user_name).one_or_none()
        if result==None:
            box_obj = boxes(user=user_name,box_number=1,card_name=word,description=description)
            db.add(box_obj)
            db.commit()
            db.refresh(box_obj)
            return box_obj
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate card name")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

def get_card(user_id:str,name:str,db:Session=Depends(get_db)):
    query = db.query(users)
    result = query.where(users.id==user_id).one_or_none()
    if result:
        query = db.query(boxes)
        result = query.where(boxes.card_name==name).one_or_none()
        if result:
            return result
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="card not found")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

def change_word(user_id:str,name:str,db:Session=Depends(get_db)):
    pass

def change_description():
    pass

def delete_card():
    pass