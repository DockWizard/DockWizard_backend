import pytest
from fastapi.testclient import TestClient
from utils.auth_helpers import user_scheme
from tests.utils import add_test_user, patch_db_users
from models.user import User

@pytest.mark.asyncio
async def test_get_user():
    from app import app

    collection = await add_test_user()
    patch_db_users(collection, app)

    client = TestClient(app)

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
async def test_get_me():
    from app import app
    
    
    collection = await add_test_user()
    patch_db_users(collection, app)

    client = TestClient(app)

    test_user = User(**{
        "username": "test_user",
        "email": "test@test.com",
        "first_name": "test",
        "surname": "testesen",
        "servers": []
    })
    async def get_fake_user_shceme():
        return test_user

    app.dependency_overrides[user_scheme] = get_fake_user_shceme
    

    response = client.get("/user/me")
    res_json = response.json()
    print(res_json)
    assert res_json["username"] == "test_user"
    assert res_json["email"] == "test@testesen.com"
    assert res_json["first_name"] == "test"
    assert res_json["surname"] == "testesen"
    assert res_json["servers"] == []
    assert "_hashed_password" not in res_json
    assert "_id" not in res_json

    app.dependency_overrides = {}
