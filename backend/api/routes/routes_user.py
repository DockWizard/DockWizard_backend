from fastapi import APIRouter, Request, Depends, HTTPException, Response
from models.user import User, EditUser
from utils.auth_helpers import get_password_hash
from database import get_db_users
from utils.auth_helpers import user_scheme

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.get("/")
async def get_user(username: str, request: Request):
    db = get_db_users(request)
    user = db.find_one({"username": username})
    if not user:
        raise HTTPException(404, "User could not be found")
    return User(**user)


@router.get("/me", response_model=User)
async def get_me(user: User = Depends(user_scheme)):
    return user


@router.put("/edit")
async def edit_user(
    payload: EditUser, request: Request, user: User = Depends(user_scheme)
):
    update_user: User = User(**user.dict())
    db = get_db_users(request)
    if payload.password:
        if not payload.password == payload.confirm_password:
            raise HTTPException(400, "Passwords do not match")
        update_user._hashed_password = get_password_hash(payload.password)

    if payload.email:
        check_email = await db.find_one({"email": payload.email})
        if check_email:
            raise HTTPException(400, "Email already in use")
        update_user.email = payload.email
    if payload.username:
        check_username = await db.find_one({"username": payload.username})
        if check_username:
            raise HTTPException(400, "Username already in use")
        update_user.username = payload.username

    if payload.first_name:
        update_user.first_name = payload.first_name
    if payload.surname:
        update_user.surname = payload.surname
    update_user_dict = update_user.dict()
    retval = await db.find_one_and_update(
        {"username": user.username}, {"$set": update_user_dict}
    )

    if not retval:
        raise HTTPException(400, "Could not update user")
    return Response(status_code=200)