from fastapi import APIRouter
from .schemas import SignUp, SignIn

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/login")
def sign_in(sign_in_model: SignIn):
    pass


@router.post("/register")
def sign_up(sign_up_model: SignUp):
    pass
