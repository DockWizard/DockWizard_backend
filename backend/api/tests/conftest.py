from starlette.testclient import TestClient

from app import app

client = TestClient(app)


def test_readsdsd():
    response = client.get("/")
    assert response.json() == {"msg": "Hello World"}
