from mongomock_motor import AsyncMongoMockClient
import pytest
from utils.auth_helpers import get_password_hash, verify_password
from app import app

from fastapi.testclient import TestClient
client2 = TestClient(app)
# conftest.py


@pytest.fixture()
def mongo_mock(monkeypatch):
    client = AsyncMongoMockClient()
    collection = client["users"]
    # app.db = client
    # db = client.get_database("users")
    # col = db.get_collection("user_data")
    # user = {
    #     "first_name": "Finn",
    #     "surname": "Sagen",
    #     "username": "finn",
    #     "email": "fsa028@uit.no",
    #     "servers": [],
    #     "_password": get_password_hash("password"),
    # }

    # col.insert_one(user)

    async def fake_client():
        return await client

    monkeypatch.setattr("database.create_db_client", fake_client)


@pytest.mark.asyncio
def test_login():
    response = client2.post(
        "/auth/login",
        json={"username": "finn", "password": "password"},
    )
    assert response.status_code == 200
