import pytest
import app as app_module

from app import app
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings
from fastapi import Request
from database import get_db_data, get_db_users


@pytest.fixture
def client():
    from app import app
    with TestClient(app) as test_client:
        yield test_client


# @pytest.mark.asyncio
# async def test_cleanup_db_data(client, monkeypatch):

#     mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
#     db = mongo_client["data"]

#     # add some sample data to the database
#     test_data = {
#         "metadata":
#             {
#                 "container_id": "1234",
#                 "container_name": "test_container",
#                 "container_image": "test_image"
#             },
#         "timestamp": "2023-03-20T12:00:00Z",
#         "data":
#             {
#                 "cpu": 0.5,
#                 "memory_perc": 50,
#                 "memory_tot": 1024,
#                 "total_rx": 100,
#                 "total_tx": 100,
#                 "io_read": 50,
#                 "io_write": 50,
#                 "healthcheck": True
#             }
#     }
#     await db["test_collection"].insert_one(test_data)

#     # check that the data is in the database
#     assert "data" in await mongo_client.list_database_names()
#     assert await db["test_collection"].count_documents({}) > 0

#     #mock the mongoclient with test database
#     async def mock_get_mongo_client(request: Request):
#         return mongo_client

#     monkeypatch.setattr(app_module.app, "get_db_data", mock_get_mongo_client)

#     response = await mongo_client.delete("/database/data")
#     assert response.status_code == 200
#     assert response.json() == {200: "Deleted DATA database"}

#     # check that the DATA database is deleted
#     assert "data" not in await mongo_client.list_database_names()

# @pytest.mark.asyncio
# async def test_cleanup_db_client(client, monkeypatch):

#     client = AsyncIOMotorClient(settings.MONGO_URI)
#     db = client["users"]

#     # add some sample data to the database
#     test_data = {
#         "username": "test_user",
#         "email": "test@test.com",
#         "hashed_password": "test_password",
#         "servers": []
#     }
#     await db["user_data"].insert_one(test_data)

#     # check that the data is in the database
#     assert "users" in await client.list_database_names()
#     assert await db["user_data"].count_documents({}) > 0

#     #mock the mongoclient with test database
#     async def mock_get_mongo_client(request: Request):
#         return db

#     monkeypatch.setattr(app_module.app, "get_db_users", mock_get_mongo_client)

#     response = await client.delete("/database/users")
#     assert response.status_code == 200
#     assert response.json() == {200: "Deleted CLIENT database"}

#     # check that the CLIENT database is deleted
#     assert "users" not in await client.list_database_names()