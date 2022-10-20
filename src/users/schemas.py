from typing import Union

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True


class Users(BaseModel):
    users: list[User] = []

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

    class Config:
        orm_mode = True
