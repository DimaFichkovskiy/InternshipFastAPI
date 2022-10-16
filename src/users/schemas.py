from typing import Union

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr


class Users(BaseModel):
    page: int
    users: list[User]


class UserUpdate(BaseModel):
    full_name: Union[str, None] = None
    email: Union[str, None] = None
