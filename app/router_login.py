
from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security import HTTPBearer
from database import local_session
from schemas import *
from datetime import datetime
from datetime import timedelta,timezone
from jose import jwt
from sqlalchemy.orm import Session
from models import users,boxes

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()
auth2_bearer = HTTPBearer()
token_key = "the secret key:)"

class decode_token:
    def name(token=Depends(auth2_bearer)):
        decode = jwt.decode(token.credentials,token_key,algorithms=["HS256"])
        return decode.get("name")

    def password(token=Depends(auth2_bearer)):
        decode = jwt.decode(token.credentials,token_key,algorithms=["HS256"])
        return decode.get("password")

def create_token(user_name,password):
    encode = {"name":user_name,"password":password}
    expire = datetime.now(timezone.utc) + timedelta(weeks=4)
    encode.update({"exp":expire})
    return jwt.encode(encode,token_key,algorithm="HS256")

@router.post("/signup",tags=["login methods"])
def signup(data:signup_schemas,db:Session=Depends(get_db)):
    global token_key
    query = db.query(users)
    result = query.where(data.name==users.user_name).one_or_none()
    if result == None:
        expired_token = datetime.now(timezone.utc) + timedelta(weeks=4)
        token = create_token(data.name,data.password)
        user_obj = users(user_name=data.name,password=data.password,token=token,token_time=expired_token)
        db.add(user_obj)
        db.commit()
        return {"status":status.HTTP_201_CREATED,"detail":"user created"}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="duplicate name")

@router.post("/login",tags=["login methods"])
def login(data:login_schemas,db:Session=Depends(get_db)):
    global token_key
    query = db.query(users)
    result = query.where(data.name==users.user_name).one_or_none()
    if result:
        result = query.where(data.name==users.user_name,
                             data.password==users.password).one_or_none()
        if result:
            if datetime.fromisoformat(result.token_time) >= datetime.now(timezone.utc):
                return {"status code":status.HTTP_200_OK,
                        "detail":"login successfully",
                        "id":result.id,
                        "user name":result.user_name,
                        "token":result.token}
            else:
                token_result = create_token(result.user_name,result.password,token_key)
                result.token == token_result
                result.token_time == datetime.now(timezone.utc) + timedelta(weeks=4)
                db.commit()
                return {"status code":status.HTTP_200_OK,
                        "detail":"login successfully",
                        "id":result.id,
                        "user name":result.user_name,
                        "new token":result.token_time}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wrong password")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

@router.put("/rename",tags=["login methods"])
def rename(data:rename_schemas,db:Session=Depends(get_db)):
    query = db.query(users)
    result = query.where(users.user_name==data.name).one_or_none()
    if result:
        result = query.where(users.user_name==data.name,
                             users.password==data.password).one_or_none()
        if result:
            if result.user_name != data.new_name:
                result.user_name = data.new_name
                db.commit()
                db.refresh(result)
                return {"status":status.HTTP_200_OK,"detail":"name changed"}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="name and new name can't be the same")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wrong password")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

@router.put("/change_password",tags=["login methods"])
def change_password(data:change_password_schemas,db:Session=Depends(get_db)):
    query = db.query(users)
    result = query.where(users.user_name==data.name).one_or_none()
    if result:
        result = query.where(users.user_name==data.name,
                             users.password==data.password).one_or_none()
        if result:
            if result.password != data.new_password:
                result.password = data.new_password
                db.commit()
                db.refresh(result)
                return {"status":status.HTTP_200_OK,"detail":"password changed"}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="password and new password can't be the same")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wrong password")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")

@router.delete("/delete_user",tags=["login methods"])
def delete_user(data:login_schemas,db:Session=Depends(get_db)):
    query = db.query(users)
    check_name = query.where(users.user_name==data.name).one_or_none()
    if check_name:
        check_password = query.where(users.user_name==data.name,users.password==data.password).one_or_none()
        if check_password:
            db.delete(check_password)
            db.commit()
            db.query(boxes).where(boxes.user==data.name).delete()
            db.commit()
            return {"status code":status.HTTP_204_NO_CONTENT,"detail":"user deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="wrong password")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="name not found")