from datetime import datetime
from database import get_db_tokens, get_db_users
from fastapi import Request
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext

from bson.objectid import ObjectId
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def user_scheme(request: Request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(401, "No authorization header")
    bearer_token = auth_header.removeprefix("Bearer ")
    token_db = get_db_tokens(request)
    token = await token_db.find_one({"bearer_token": bearer_token})
    if not token:
        raise HTTPException(401, "Invalid token")

    # Check token not expired by seeing if expires_at has passed
    if token.get("expires_at") < datetime.now():
        raise HTTPException(401, "Token has expired")

    user_db = get_db_users(request)
    user = await user_db.find_one({"_id": ObjectId(token.get("user_id"))})
    if not user:
        raise HTTPException(401, "User could not be found")

    return User(**user)


# Bearer token holding API key and key is valid for this collection?
async def agent_scheme(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(401, "No authorization header")
    bearer_token = auth_header.removeprefix("Bearer ")
    user_db = get_db_users(request)
    agent_config = await user_db.find_one(
        {"agent_config.bearer_token": bearer_token}
    )

    return True
    # How to validate the agent?
    # Need to to see who is posting, and if the collection they are trying to post to is theirs
