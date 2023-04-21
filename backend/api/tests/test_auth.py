import pytest
import app as app_module

from fastapi.testclient import TestClient
from tests.utils import add_test_user
from mongomock_motor import AsyncMongoMockClient




@pytest.fixture()
def client():
    from app import app
    with TestClient(app) as test_client:
        yield test_client

@pytest.mark.asyncio
async def test_login(client, monkeypatch):
   
    # add test user 
    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})

    # login
    response = client.post("/auth/login",
                            json={"username": "test_user", 
                                  "password": "password"})
    res_json = response.json()

    # check response contains the correct data
    assert response.status_code == 200
    assert "bearer_token" in res_json
    assert "expires_at" in res_json
    assert "user_id" in res_json




@pytest.mark.asyncio
async def test_logout(client, monkeypatch):

    # add test user
    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})

    #login
    response = client.post("/auth/login", json={"username": "test_user", "password": "password"})
    res_json = response.json()
    token = res_json["bearer_token"]

    #logout
    response = client.post("/auth/logout")
    assert response.status_code == 400

    response = client.post("/auth/logout",
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    



@pytest.mark.asyncio
async def test_register_user(client, monkeypatch):
    # add test user
    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    # test user with not matching passwords
    test_user_password = { 
        "first_name": "test",
        "surname": "testesen",
        "username": "username",
        "email": "user@name.com",
        "password": "password",
        "confirm_password": "not_matching_password"
        }
    # Test case: Passwords do not match
    response = client.post("/auth/register", json=test_user_password)
    assert response.status_code == 400
    assert response.json() == {"detail": "Passwords do not match"}


    # test user with existing email
    test_user_email = {
        "first_name": "existing",
        "surname": "user",
        "username": "test",
        "email": "test@test.com",
        "password": "password",
        "confirm_password": "password"
    }
    # Test case: Email already exists
    response = client.post("/auth/register", json=test_user_email)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already exists"}


    # test user with existing username
    test_user_username = {"first_name": "existing",
        "surname": "user",
        "username": "test_user",
        "email": "existing_user@example.com",
        "password": "password",
        "confirm_password": "password"
    }
    # Test case: Username already exists
    response = client.post("/auth/register", json=test_user_username)
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already exists"}


    # test user with valid data
    test_user_success = {  "username": "new_user",
        "email": "new@user.com",
        "first_name": "new",
        "surname": "user",
        "password": "password",
        "confirm_password": "password"
    }
    # Test case: User created successfully
    response = client.post("/auth/register", json=test_user_success)
    assert response.status_code == 200
    assert response.json() == {"message": 
                                "User created successfully!", 
                                "data": {
                                "username": "new_user", 
                                "email": "new@user.com",
                                "first_name": "new",
                                "surname": "user",
                                "servers": []
                                }}

    