from fastapi import APIRouter, Request, Depends, HTTPException
from models.user import User

from database import get_db_users
from utils.auth_helpers import user_scheme

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.get("/{username}")
async def get_user(username: str, request: Request):
    db = get_db_users(request)
    user = await db.find_one({"username": username})
    if not user:
        raise HTTPException(404, "User could not be found")
    return User(**user)


@router.get("/me", response_model=User)
async def get_me(user: User = Depends(user_scheme)):
    print(user)
    return user
