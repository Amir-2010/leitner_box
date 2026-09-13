
from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import HTTPBearer
from database import local_session
from sqlalchemy.orm import Session
from models import boxes,users
from router_login import decode_token
from router_login import auth2_bearer

router = APIRouter()

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/create_card",tags=["box methods"])
def create_card(word:str,description:str,db:Session=Depends(get_db),token=Depends(auth2_bearer)):
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
            return "card created"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate card name")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

@router.get("/get_cards",tags=["box methods"])
def get_cards(db:Session=Depends(get_db),token=Depends(auth2_bearer)):
    query = db.query(boxes)
    user_name = decode_token.name(token)
    result = query.where(boxes.user==user_name).all()
    if result:
        return HTTPException(status_code=status.HTTP_200_OK,detail=result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

@router.put("/change_word",tags=["box methods"])
def change_word(word:str,new_word:str,db:Session=Depends(get_db),token=Depends(auth2_bearer)):
    query = db.query(boxes)
    user_name = decode_token.name(token)
    result = query.where(boxes.user==user_name).all()
    if result:
        result = query.where(boxes.user==user_name,boxes.card_name==word).first()
        if result:
            result = query.where(boxes.user==user_name,boxes.card_name==new_word).one_or_none()
            if result == None:
                result = query.where(boxes.user==user_name,boxes.card_name==word).first()
                result.card_name = new_word
                db.commit()
                return {"detail":"word changed"}
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate name")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="word not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

@router.put("/change_description",tags=["box methods"])
def change_description(word:str,new_description:str,db:Session=Depends(get_db),token=Depends(auth2_bearer)):
    query = db.query(boxes)
    user_name = decode_token.name(token)
    result = query.where(boxes.user==user_name).all()
    if result:
        result = query.where(boxes.user==user_name,boxes.card_name==word).first()
        if result:
            result.description = new_description
            db.commit()
            return {"detail":"description changed"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="word not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

@router.delete("/delete_card",tags=["box methods"])
def delete_card(word:str,db:Session=Depends(get_db),token=Depends(auth2_bearer)):
    query = db.query(boxes)
    user_name = decode_token.name(token)
    result = query.where(boxes.user==user_name,boxes.card_name==word).first()
    if result:
        query.where(boxes.user==user_name,boxes.card_name==word).delete()
        db.commit()
        return {"detail":"word deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="word not found")