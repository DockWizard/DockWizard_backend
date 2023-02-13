from fastapi.testclient import TestClient
from app import app
from tests.conftest import mongo_mock
client = TestClient(app)


def test_login(mongo_mock):
    response = client.post(
        "/auth/login",
        json={"username": "finn", "password": "password"},
    )
    assert response.status_code == 200
