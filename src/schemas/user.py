from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True
