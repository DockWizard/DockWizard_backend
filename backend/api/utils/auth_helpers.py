from dataclasses import dataclass
from datetime import datetime
from database import get_db_tokens, get_db_users, get_db_data
from fastapi import WebSocket, Request, status
from fastapi.exceptions import HTTPException, WebSocketException
from passlib.context import CryptContext
from motor.core import Collection

from bson.objectid import ObjectId
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class AgentScheme:
    user: Collection
    data: Collection


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


async def user_scheme_websocket(websocket: WebSocket) -> User:
    auth_header = websocket.headers.get("Authorization")
    if not auth_header:
        raise WebSocketException(
            status.WS_1008_POLICY_VIOLATION, "No authorization header"
        )
    bearer_token = auth_header.removeprefix("Bearer ")
    token_db = get_db_tokens(websocket)
    token = await token_db.find_one({"bearer_token": bearer_token})
    if not token:
        raise WebSocketException(
            status.WS_1008_POLICY_VIOLATION, "Invalid token"
        )

    # Check token not expired by seeing if expires_at has passed
    if token.get("expires_at") < datetime.now():
        raise WebSocketException(
            status.WS_1008_POLICY_VIOLATION, "Token has expired"
        )

    user_db = get_db_users(websocket)
    user = await user_db.find_one({"_id": ObjectId(token.get("user_id"))})
    if not user:
        raise WebSocketException(
            status.WS_1008_POLICY_VIOLATION, "User could not be found"
        )

    return User(**user)


# Bearer token holding API key and key is valid for this collection?
async def agent_scheme(request: Request) -> AgentScheme:
    print("fek")
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(401, "No authorization header")
    bearer_token = auth_header.removeprefix("Bearer ")
    user_db = get_db_users(request)
    agent_config = await user_db.find_one(
        {"servers": {
            "$elemMatch": {
                "api_key": bearer_token
            }
        }},
    )
    if not agent_config:
        raise HTTPException(401, "Invalid token")

    data_collection_id = agent_config.get("servers")[0].get("collection_id")
    data_db = get_db_data(request)
    data_collection = data_db[data_collection_id]

    return AgentScheme(user=user_db, data=data_collection)
