
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

# Create and manage a database session for each request.
# The session is automatically closed after the request is finished.
def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

# Create a new flashcard for the authenticated user.
# New cards always start in box 1 and are reviewed after one day.
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
        # Prevent a user from creating two cards with the same word.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate card name")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

# Change the word/name of an existing card.
# The new word must not already belong to another card owned by the user.
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
            # Do not allow duplicate card names for the same user.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate name")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="word not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

# Update the description/meaning of an existing card.
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

# Delete a card belonging to the authenticated user.
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
# Get the cards currently belonging to a specific Leitner box.
# Each box has its own review interval:
# Box 1 = 1 day, Box 2 = 2 days, Box 3 = 4 days,
# Box 4 = 7 days, and Box 5 = 14 days.
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
        # Return an error when the requested box number does not exist.
        return {"detail":"box not found"}

# Update a card's Leitner box after the user answers a question.
# A correct answer moves the card to the next box.
# An incorrect answer moves the card back to box 1.
@router.put("/change_box",tags=["boxes word"])
def change_box(card_id: int, correct: bool, db: Session = Depends(get_db), token=Depends(auth2_bearer)):
    user_name = decode_token.name(token)
    # Find the card only if it belongs to the authenticated user.
    card = db.query(boxes).where(boxes.id == card_id, boxes.user == user_name).first()
    if not card:
        raise HTTPException(status_code=404, detail="card not found")
    if correct:
        # A correct answer on box 5 completes the card and removes it.
        if card.box_number == 5:
            result = card.card_name
            db.delete(card)
            db.commit()
            return {"you pass": result}
        # Move the card to the next box after a correct answer.
        card.box_number += 1
    else:
        # A wrong answer sends the card back to the first box.
        card.box_number = 1
    # Define the number of days before the card should be reviewed again.
    review_days = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}
    # Calculate the next review date based on the card's new box.
    card.review_time = datetime.now() + timedelta(days=review_days[card.box_number])
    db.commit()
    db.refresh(card)
    # Return the updated card information to the client.
    return {"id": card.id, "word": card.card_name, "meaning": card.description, "box": card.box_number, "review_time": card.review_time, "correct": correct}