from fastapi.testclient import TestClient
from app import app
from tests.utils import read_text_file

client = TestClient(app)

def test_get_agent_binary():
    response = client.get("/assets/agent")
    file = read_text_file("assets/agent.txt")
    assert response.status_code == 200
    assert response.content == file
    assert response.headers["content-type"] == "application/octet-stream"