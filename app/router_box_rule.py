
from fastapi import APIRouter
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from fastapi import Depends
from router_login import get_db
from models import boxes

router = APIRouter()

def box1(name,db:Session=Depends(get_db)): # box 1 ==> every day
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==1).all()
    if not words:
        return []
    words_list = []
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    return {"review time":words[0].review_time}

def box2(name,db:Session=Depends(get_db)): # box 2 ==> every 2 days
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==2).all()
    if not words:
        return []
    words_list = []
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    return {"review time":words[0].review_time}

def box3(name,db:Session=Depends(get_db)): # box 3 ==> every 4 days
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==3).all()
    if not words:
        return []
    words_list = []
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    return {"review time":words[0].review_time}

def box4(name,db:Session=Depends(get_db)): # box 4 ==> every week
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==4).all()
    if not words:
        return []
    words_list = []
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    return {"review time":words[0].review_time}

def box5(name,db:Session=Depends(get_db)): # box 5 ==> every 2 week
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==5).all()
    if not words:
        return []
    words_list = []
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    return {"review time":words[0].review_time}