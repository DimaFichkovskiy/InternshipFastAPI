from fastapi import APIRouter

from .schemas import User, Users, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/")
def get_all_list_users(users: Users):
    pass


@router.get("/{user_id}")
def get_user(user: User):
    pass


@router.put("/{user_id}")
def update_user(user_update: UserUpdate):
    pass
