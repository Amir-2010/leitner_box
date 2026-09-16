
from fastapi import APIRouter,HTTPException,Depends,status
from fastapi.security import HTTPBearer
from database import local_session
from sqlalchemy.orm import Session
from models import boxes,users
from router_login import decode_token
from router_login import auth2_bearer
import router_box_rule as box_rule
from datetime import datetime,timedelta

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
            next_review = datetime.now() + timedelta(days=1)
            box_obj = boxes(user=user_name,box_number=1,card_name=word,description=description,review_time=next_review)
            db.add(box_obj)
            db.commit()
            db.refresh(box_obj)
            return "card created"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate card name")
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

# --------------- get words ---------------

@router.get("/get_box",tags=["boxes word"])
def get_box(box_number:int,db:Session=Depends(get_db),token=Depends(auth2_bearer)):
    if box_number == 1:
        user_name = decode_token.name(token)
        result = box_rule.box1(user_name,db)
        user_data = db.query(boxes).where(boxes.user==user_name,boxes.box_number==1).all()
        for i in user_data:
            i.review_time = datetime.now() + timedelta(days=1)
            db.commit()
        return result
    elif box_number == 2:
        user_name = decode_token.name(token)
        result = box_rule.box2(user_name,db)
        user_data = db.query(boxes).where(boxes.user==user_name,boxes.box_number==2).all()
        for i in user_data:
            i.review_time = datetime.now() + timedelta(days=2)
            db.commit()
        return result
    elif box_number == 3:
        user_name = decode_token.name(token)
        result = box_rule.box3(user_name,db)
        user_data = db.query(boxes).where(boxes.user==user_name,boxes.box_number==3).all()
        for i in user_data:
            i.review_time = datetime.now() + timedelta(days=4)
            db.commit()
        return result
    elif box_number == 4:
        user_name = decode_token.name(token)
        result = box_rule.box4(user_name,db)
        user_data = db.query(boxes).where(boxes.user==user_name,boxes.box_number==4).all()
        for i in user_data:
            i.review_time = datetime.now() + timedelta(days=7)
            db.commit()
        return result
    elif box_number == 5:
        user_name = decode_token.name(token)
        result = box_rule.box5(user_name,db)
        user_data = db.query(boxes).where(boxes.user==user_name,boxes.box_number==5).all()
        for i in user_data:
            i.review_time = datetime.now() + timedelta(days=14)
            db.commit()
        return result
    else:
        return {"detail":"box not found"}

@router.put("/change_box",tags=["boxes word"])
def answer_card(card_id: int, correct: bool, db: Session = Depends(get_db), token=Depends(auth2_bearer)):
    user_name = decode_token.name(token)
    card = db.query(boxes).where(boxes.id == card_id, boxes.user == user_name).first()
    if not card:
        raise HTTPException(status_code=404, detail="card not found")
    if not card:
        raise HTTPException(status_code=404, detail="card not found")
    if correct:
        if card.box_number == 5:
            result = card.card_name
            db.delete(card)
            db.commit()
            return {"you pass": result}
        card.box_number += 1
    else:
        card.box_number = 1
    review_days = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}
    card.review_time = datetime.now() + timedelta(days=review_days[card.box_number])
    db.commit()
    db.refresh(card)
    return {"id": card.id, "word": card.card_name, "meaning": card.description, "box": card.box_number, "review_time": card.review_time, "correct": correct}