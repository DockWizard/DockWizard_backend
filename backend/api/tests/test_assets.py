from fastapi.testclient import TestClient
import pytest
from app import app

client = TestClient(app)

# @pytest.mark.asyncio
# def test_get_agent_binary():
    # response = client.get("/assets/agent")
    # assert response.status_code == 200
    # assert response.headers["content-type"] == "application/octet-stream"
    # assert response.headers["content-disposition"] == "attachment; filename=agent.txt"
    # assert response.content == b"assets/agent.txt" 