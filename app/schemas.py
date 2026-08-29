
from pydantic import BaseModel

class signup_schemas(BaseModel):
    name: str
    password: str

class login_schemas(signup_schemas):
    pass

class rename_schemas(signup_schemas):
    new_name : str

class change_password_schemas(signup_schemas):
    new_password : str

class delete_user_schemas(BaseModel):
    name:str