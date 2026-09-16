
from fastapi import APIRouter
from datetime import datetime,timedelta
from sqlalchemy.orm import Session
from fastapi import Depends
from router_login import get_db
from models import boxes

# Router used for the Leitner box-related functions.
router = APIRouter()

# Box 1 contains cards that should normally be reviewed every day.
def box1(name,db:Session=Depends(get_db)): # box 1 ==> every day
    # Get all cards belonging to the user that are currently in box 1.
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==1).all()
    # Return an empty list when the user has no cards in this box.
    if not words:
        return []
    words_list = []
    # Only return the cards for review when their review time has arrived.
    if datetime.now() >= words[0].review_time:
        # Build a simple response containing the word and its description.
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    # If the cards are not ready yet, return the next review time.
    return {"review time":words[0].review_time}

# Box 2 contains cards that should normally be reviewed every 2 days.
def box2(name,db:Session=Depends(get_db)): # box 2 ==> every 2 days
    # Get all cards belonging to the user that are currently in box 2.
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==2).all()
    # Return an empty list when there are no cards in this box.
    if not words:
        return []
    words_list = []
    # Check whether the scheduled review time has been reached.
    if datetime.now() >= words[0].review_time:
        # Add each card that is ready to the response list.
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    # Tell the user when the cards will become available for review.
    return {"review time":words[0].review_time}

# Box 3 contains cards that should normally be reviewed every 4 days.
def box3(name,db:Session=Depends(get_db)): # box 3 ==> every 4 days
    # Find all cards for this user that are currently in box 3.
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==3).all()
    # No cards in the box means there is nothing to review.
    if not words:
        return []
    words_list = []
    # Return the cards only when their review time has arrived.
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    # Otherwise, return the scheduled review time.
    return {"review time":words[0].review_time}

# Box 4 contains cards that should normally be reviewed every week.
def box4(name,db:Session=Depends(get_db)): # box 4 ==> every week
    # Get all cards belonging to the user that are in box 4.
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==4).all()
    # Return an empty list if this box has no cards.
    if not words:
        return []
    words_list = []
    # Check if the cards are due for their scheduled review.
    if datetime.now() >= words[0].review_time:
        # Prepare the cards for the API response.
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    # Cards that are not due yet return their next review time.
    return {"review time":words[0].review_time}

# Box 5 contains cards that should normally be reviewed every 2 weeks.
def box5(name,db:Session=Depends(get_db)): # box 5 ==> every 2 week
    # Get all cards belonging to the user that are currently in box 5.
    words = db.query(boxes).where(boxes.user==name,boxes.box_number==5).all()
    # Return an empty list when there are no cards in this box.
    if not words:
        return []
    words_list = []
    # If the review time has arrived, return all cards that are ready.
    if datetime.now() >= words[0].review_time:
        for i in words:
            words_list.append({"word":i.card_name,"description":i.description})
        return words_list
    # Otherwise, return the next scheduled review time.
    return {"review time":words[0].review_time}