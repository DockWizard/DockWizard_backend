import pytest
from fastapi.testclient import TestClient

from tests.utils import add_test_user, patch_db_users

@pytest.mark.asyncio
async def test_get_user():
    from app import app

    collection = await add_test_user()
    patch_db_users(collection, app)

    client = TestClient(app)

    response = client.get("/user?username=test_user")
    res_json = response.json()
    assert res_json["username"] == "test_user"
    assert res_json["email"] == "test@test.com"
    assert res_json["first_name"] == "test"
    assert res_json["surname"] == "testesen"
    assert res_json["servers"] == []
    assert "_hashed_password" not in res_json
    assert "_id" not in res_json






