
from database import local_session,Base
from sqlalchemy import Column,String,Integer,DateTime

# Create a database session that can be used when working with the models.
session = local_session()

# Database model for storing registered users and their authentication data.
class users(Base):
    __tablename__ = "users"
    # Automatically generated unique ID for each user.
    id = Column(Integer,primary_key=True,autoincrement=True)
    # Username used to identify the user during login.
    user_name = Column(String)
    # Password associated with the user account.
    password = Column(String)
    # JWT token used for authentication.
    token = Column(String)
    # Time when the current authentication token expires.
    token_time = Column(Integer)

# Database model for storing the user's flashcards and Leitner box information.
class boxes(Base):
    __tablename__ = "boxes"
    # Automatically generated unique ID for each card.
    id = Column(Integer,primary_key=True,autoincrement=True)
    # Username of the person who owns the card.
    user = Column(String)
    # Leitner box number that determines the review interval.
    box_number = Column(Integer)
    # Word or question stored on the flashcard.
    card_name = Column(String)
    # Description or answer associated with the card.
    description = Column(String)
    # Date and time when the card should be reviewed again.
    review_time = Column(DateTime)