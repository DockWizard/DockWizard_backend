from motor.core import AgnosticDatabase, Collection
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
from settings import settings
from mongomock_motor import AsyncMongoMockClient


def create_db_client():
    return AsyncIOMotorClient(settings.MONGO_URI)
    # return AsyncMongoMockClient()


def startup_db_client(app):
    # db = AsyncIOMotorClient(settings.MONGO_URI)
    db = create_db_client()
    app.db_data = db.data
    app.db_users = db['users']
    app.db_tokens = db.tokens


def get_db_data(request: Request) -> AgnosticDatabase:
    return request.app.db_data


def get_db_users(request: Request) -> Collection:
    return request.app.db_users["user_data"]


def get_db_tokens(request: Request) -> Collection:
    return request.app.db_tokens["token_data"]
