from pydantic import BaseModel, EmailStr


class SignUp(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str


class SignIn(BaseModel):
    email: EmailStr
    password: str
