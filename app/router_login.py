from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import HTTPBearer
from fastapi import Response
from database import local_session
from schemas import *
from datetime import datetime
from datetime import timedelta,timezone
from jose import jwt
from sqlalchemy.orm import Session
from models import users,boxes

# Create and manage a database session for each request.
def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()
# HTTPBearer is used to receive and validate the Bearer token
# sent in the Authorization header.
auth2_bearer = HTTPBearer()
# Secret key used to sign and decode JWT authentication tokens.
token_key = "the secret key:)"

# Helper class for extracting information from the JWT token.
class decode_token:
    # Extract the username stored inside the token.
    def name(token=Depends(auth2_bearer)):
        decode = jwt.decode(token.credentials,token_key,algorithms=["HS256"])
        return decode.get("name")
    # Extract the password stored inside the token.
    def password(token=Depends(auth2_bearer)):
        decode = jwt.decode(token.credentials,token_key,algorithms=["HS256"])
        return decode.get("password")

# Create a JWT token containing the user's username and password.
# The token remains valid for four weeks.
def create_token(user_name,password):
    encode = {"name":user_name,"password":password}
    expire = datetime.now(timezone.utc) + timedelta(weeks=4)
    encode.update({"exp":expire})
    return jwt.encode(encode,token_key,algorithm="HS256")

# Register a new user.
# A username can only be used once.
@router.post("/signup",tags=["login methods"])
def signup(data:signup_schemas,response:Response,db:Session=Depends(get_db)):
    global token_key
    query = db.query(users)
    result = query.where(data.name==users.user_name).one_or_none()
    # Create the account only when the username does not already exist.
    if result == None:
        expired_token = datetime.now(timezone.utc) + timedelta(weeks=4)
        token = create_token(data.name,data.password)
        user_obj = users(user_name=data.name,password=data.password,token=token,token_time=expired_token)
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        # Store the authentication token in a cookie.
        response.set_cookie(key="token",value=user_obj.token)
        return {"status":status.HTTP_201_CREATED,"detail":"user created"}
    else:
        # Prevent multiple accounts from using the same username.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="duplicate name")

# Authenticate an existing user and return their token.
@router.post("/login",tags=["login methods"])
def login(data:login_schemas,response:Response,db:Session=Depends(get_db)):
    global token_key
    query = db.query(users)
    result = query.where(data.name==users.user_name).first()
    # First check whether the username exists.
    if result:
        # Then verify that the supplied password matches.
        result = query.where(data.name==users.user_name,
                             data.password==users.password).one_or_none()
        if result:
            # Return the existing token when it has not expired.
            if datetime.fromisoformat(result.token_time) >= datetime.now(timezone.utc):
                return {"status code":status.HTTP_200_OK,
                        "detail":"login successfully",
                        "id":result.id,
                        "user name":result.user_name,
                        "token":result.token}
            else:
                # Generate a new token when the previous token has expired.
                token_result = create_token(result.user_name,result.password,token_key)
                result.token = token_result
                result.token_time = datetime.now(timezone.utc) + timedelta(weeks=4)
                db.commit()
                response.set_cookie(token_key="token",value=result.token)
                return {"status code":status.HTTP_200_OK,
                        "detail":"login successfully",
                        "id":result.id,
                        "user name":result.user_name,
                        "new token":result.token_time}
        else:
            # Username exists, but the supplied password is incorrect.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wrong password")
    else:
        # The username does not exist in the database.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

# Change the username of the currently authenticated user.
@router.put("/rename",tags=["login methods"])
def rename(new_name:str,response:Response,token=Depends(auth2_bearer),db:Session=Depends(get_db)):
    try:
        # Do not allow the user to change to the same username.
        if new_name != decode_token.name(token):
            find_user = db.query(users).where(users.user_name==decode_token.name(token),
                                            users.password==decode_token.password(token)).first()
            # Update the username and create a new token containing the new name.
            find_user.user_name = new_name
            db.commit()
            db.refresh(find_user)
            find_user.token = create_token(new_name,find_user.password)
            db.commit()
            db.refresh(find_user)
            # Store the new token in the response cookie.
            response.set_cookie(key="token",value=find_user.token)
            return {"status":status.HTTP_200_OK,"detail":"name changed","new_token":find_user.token}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="duplicate name")
    # Handle errors that occur while changing the username.
    except:
        user = db.query(users).where(users.user_name==new_name,
                                    users.password==decode_token.password(token)).one_or_none()
        if user is not None and user.user_name == new_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="duplicate name")
        elif user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not found")
        else:
            return {"status_code": status.HTTP_404_NOT_FOUND,"detail": "change token","new token": user.token}

# Change the password of the currently authenticated user.
@router.put("/change_password",tags=["login methods"])
def change_password(new_password:str,response:Response,token=Depends(auth2_bearer),db:Session=Depends(get_db)):
    # Prevent the user from replacing the password with the same password.
    if new_password == decode_token.password(token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password and new password can't be the same")
    try:
        # Find the authenticated user using the username and current password.
        find_user = db.query(users).where(
            users.user_name == decode_token.name(token),
            users.password == decode_token.password(token)).first()
        if find_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found")
        # Save the new password in the database.
        find_user.password = new_password
        db.commit()
        db.refresh(find_user)
        # Create a new token because the password stored in the token has changed.
        user_data = db.query(users).where(
            users.user_name == decode_token.name(token),
            users.password == new_password).first()
        user_data.token = create_token(
            user_data.user_name,
            new_password)
        db.commit()
        response.set_cookie(key="token",value=user_data.token)
        db.refresh(user_data)
        # Return the newly generated authentication token.
        return {"status": status.HTTP_200_OK,"detail": "password changed","new token": user_data.token}
    # Handle errors while finding or updating the user.
    except:
        user = db.query(users).where(
            users.user_name == decode_token.name(token),
            users.password == new_password).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "change token","new token": user.token})
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="user not found")

# Delete the currently authenticated user and their cards.
@router.delete("/delete_user", tags=["login methods"])
def delete_user(response: Response,token=Depends(auth2_bearer),db: Session = Depends(get_db)):
    try:
        query = db.query(users)
        # Check whether the username from the token exists.
        check_name = query.where(users.user_name == decode_token.name(token)).first()
        if not check_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")
        # Verify that the password stored in the token matches the database.
        check_password = query.where(users.user_name == decode_token.name(token),users.password == decode_token.password(token)).one_or_none()
        if not check_password:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wrong password")
        # Delete the user account.
        db.delete(check_password)
        db.commit()
        # Delete all flashcards belonging to the deleted user.
        db.query(boxes).where(boxes.user == decode_token.name(token)).delete()
        # Clear the authentication cookie after account deletion.
        response.set_cookie(key="token",value="")
        db.commit()
        return {"status code": status.HTTP_204_NO_CONTENT,"detail": "user deleted"}
    # Handle errors that occur during account deletion.
    except:
        user = db.query(users).where(
            users.user_name == decode_token.name(token),
            users.password == decode_token.password(token)).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"detail": "change token","new token": user.token})
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found")