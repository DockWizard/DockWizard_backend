from datetime import datetime
from database import get_db_tokens, get_db_users
from fastapi import Request
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
import uuid
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


async def agent_scheme(request: Request):
    # 1. Api token
    # 2. User id
    # 3. Collection id(in url)
    # Get user<id>
    # Get user<id>.servers WHERE servers.collection_id == collection_id
    # Check if api token == user<id>.server:collection_id.api_token
    auth_header = request.headers.get("Authorization")
    user_header = request.headers.get("user_id")
    collection_id = request.url.path.split("/")[-1]
    if not auth_header:
        raise HTTPException(401, "No authorization header")
    if not user_header:
        raise HTTPException(401, "No user id header")

    bearer_token = auth_header.removeprefix("Bearer ")

    user_db = get_db_users(request)

    agent_config = await user_db.find_one(
        {"_id.": uuid.UUID(user_header).hex,
         "servers.collection_id": collection_id}
    )
    if not agent_config:
        raise HTTPException(401, "Invalid agent config")

    if not agent_config.get("api_token") == bearer_token:
        raise HTTPException(401, "Invalid token")

    return True
