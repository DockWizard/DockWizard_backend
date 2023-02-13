from fastapi.testclient import TestClient
from utils.auth_helpers import get_password_hash
from app import app
import pytest
from tests.conftest import mongo_mock

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_user(mongo_mock):
    await mongo_mock
    response = client.get("/user/test_user")
    assert response.status_code == 200
    assert response.json()["_id"] == ""
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "test@test.com"
    assert response.json()["first_name"] == "test"
    assert response.json()["last_name"] == "testesen"
    assert response.json()["servers"] == []
    assert response.json()["_hashed_password"] == get_password_hash("password")






