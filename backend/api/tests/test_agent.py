from starlette.testclient import TestClient
import pytest
from uuid import uuid4
from utils.auth_helpers import get_password_hash


from app import app

client = TestClient(app)

def test_read():
    response = client.get("/")
    assert response.status_code == 200


# @pytest.mark.asyncio
# def test_get_collection_by_path():

#     collection_id = str(uuid4())
#     user_data = {
#         "username": "test_user",
#         "email": "test@test.com",
#         "first_name": "test",
#         "surname": "testesen",
#         "servers": [
#             {
#                 "alias": "test_server",
#                 "collection_id": collection_id,
#                 "api_key": "test_api_key",
#                 "update_frequency": 60,
#                 "container"
#             }
#         ],
#         "_hashed_password": get_password_hash("password")
#     }