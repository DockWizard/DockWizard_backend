import pytest
from fastapi.testclient import TestClient
from utils.auth_helpers import user_scheme
from tests.utils import add_test_user
from models.user import User
import app as app_module

@pytest.fixture()
def client():
    from app import app
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.asyncio
async def test_get_user(client, monkeypatch):
    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    response = client.get("/user/test_user")
    res_json = response.json()
    assert res_json["username"] == "test_user"
    assert res_json["email"] == "test@test.com"
    assert res_json["first_name"] == "test"
    assert res_json["surname"] == "testesen"
    assert res_json["servers"] == []
    assert "_hashed_password" not in res_json
    assert "_id" not in res_json

@pytest.mark.asyncio
async def test_get_me(client):
    test_user = User(**{
        "username": "test_user",
        "email": "test@test.com",
        "first_name": "test",
        "surname": "testesen",
        "servers": []
    })
    client.app.dependency_overrides[user_scheme] = lambda: test_user

    response = client.get("/user/me")
    res_json = response.json()
    print(res_json)
    assert res_json["username"] == "test_user"
    assert res_json["email"] == "test@test.com"
    assert res_json["first_name"] == "test"
    assert res_json["surname"] == "testesen"
    assert res_json["servers"] == []
    assert "_hashed_password" not in res_json
    assert "_id" not in res_json
