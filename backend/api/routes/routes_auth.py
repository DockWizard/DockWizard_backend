import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException
from models.user import User
from models.auth import Token, CreateUserRequest, CreateUserResponse, LoginRequest
from database import get_db_users, get_db_tokens
from utils.auth_helpers import get_password_hash, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.post("/login", response_model=Token)
async def login(request: Request, login_request: LoginRequest):
    db = get_db_users(request)
    user = await db.find_one({"username": login_request.username})
    if not user:
        raise HTTPException(
            404,
            "User could not be found",
        )

    if not verify_password(
        login_request.password, user.get("_hashed_password")
    ):
        raise HTTPException(
            404, "Username or password is incorrect: " +
            get_password_hash(login_request.password)
        )
    token_db = get_db_tokens(request)
    generated_token = secrets.token_urlsafe(32)
    new_token = Token(
        bearer_token=generated_token,
        expires_at=datetime.now() + timedelta(hours=12),
        user_id=str(user.get("_id"))
    )
    await token_db.insert_one(new_token.dict())
    return new_token


@router.post("/register", response_model=CreateUserResponse)
async def register_user(create_request: CreateUserRequest, request: Request):
    if create_request.password != create_request.confirm_password:
        raise HTTPException(400, "Passwords do not match")

    db = get_db_users(request)
    existing_user = await db.find_one(
        {
            "$or":
                [
                    {
                        "email": create_request.email
                    }, {
                        "username": create_request.username
                    }
                ]
        }
    )

    if existing_user:
        if existing_user.get("email") == create_request.email:
            raise HTTPException(400, "Email already exists")
        if existing_user.get("username") == create_request.username:
            raise HTTPException(400, "Username already exists")

    password_hash = get_password_hash(create_request.password)
    user_dict = create_request.dict(exclude={"password", "confirm_password"})

    new_user = User(**user_dict)
    new_user_dict = new_user.dict()
    additional_fields = {
        "_hashed_password": password_hash,
        "servers": [],
    }

    new_user_dict.update(additional_fields)
    print(new_user_dict)
    await db.insert_one(new_user_dict)
    return CreateUserResponse(
        message="User created successfully!", data=new_user
    )
