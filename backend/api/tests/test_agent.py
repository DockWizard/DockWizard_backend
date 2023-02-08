from starlette.testclient import TestClient

from app import app

client = TestClient(app)


def test_read():
    response = client.get("/")
    assert response.status_code == 200
