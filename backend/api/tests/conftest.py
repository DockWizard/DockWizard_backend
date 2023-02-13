from fastapi.testclient import TestClient
import pytest
from models.user import User
from utils.auth_helpers import get_password_hash
from mongomock_motor import AsyncMongoMockClient



@pytest.fixture()
async def mongo_mock(monkeypatch):
    client = AsyncMongoMockClient()
    db = client.get_database("user_db")
    col = db.get_collection("users")
    user_data: User = {
        "username": "test_user",
        "email": "test@test.com",
        "first_name": "test",
        "last_name": "testesen",
        "servers": [],
        "_hashed_password": get_password_hash("password")
    }

    await col.insert_one(user_data)

    # x = col.fetch_one({"username": "test_user"})
    # print(x)

    def fake_db():
        return db

    monkeypatch.setattr("database.get_db_users", fake_db)
    yield db