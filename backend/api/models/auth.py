from pydantic import BaseModel
from typing import Union
from datetime import datetime
from models.user import User


class Token(BaseModel):
    bearer_token: str
    expires_at: datetime
    user_id: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    first_name: str
    surname: str
    username: str
    email: str
    password: str
    confirm_password: str


class CreateUserResponse(BaseModel):
    message: str
    data: User
