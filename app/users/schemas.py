from pydantic import (
    BaseModel,
    EmailStr, 
    SecretStr,
    validator,
    root_validator
    )

from .models import User
from . import auth

class UserLoginSchema(BaseModel):
    email : EmailStr
    password : SecretStr
    session_id : str = None

    @root_validator
    def validate_user(cls, values):
        err_msg = "Invalid credentials, Please try again!"
        email = values.get('email') or None
        password = values.get('password') or None
        if email is None or password is None:
            raise ValueError(err_msg)
        password = password.get_secret_value() #get_secret_value method to see the secret's content 
        user_obj = auth.authenticate(email, password)
        print(user_obj)
        if user_obj is None:
            raise ValueError(err_msg)
        token = auth.login(user_obj)
        return {"session_id" : token}

class UserSignupSchema(BaseModel):
    email : EmailStr
    password : SecretStr
    password_confirm : SecretStr
    
    @validator('email')
    def email_available(cls, v, values, **kwargs): #values = {email: ,password: ,password_confirm:} , v = @validator('***')
        q = User.objects.filter(email = v)
        if q.count() != 0:
            raise ValueError("Email is not available")
        return v
    
    @validator('password_confirm')
    def password_match(cls, v, values, **kwargs):
        password = values.get('password')
        password_confirm = v
        if password != password_confirm:
            raise ValueError('Password does not match')
        return v