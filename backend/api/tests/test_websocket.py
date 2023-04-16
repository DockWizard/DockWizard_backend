import datetime
import json
import pytest
import app as app_module
import uuid

from models.user import User
from models.agent import AgentConfig, AgentTSObjetc
from mongomock_motor import AsyncMongoMockClient
from tests.utils import add_test_user, remove_test_user
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True, scope="module")
async def test_user():
    await add_test_user()
    yield
    await remove_test_user()


@pytest.fixture
def client():
    from app import app
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_get_container_data(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    #login and get token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    id = uuid.uuid4().hex
    test_agent = AgentConfig(
        id=uuid.uuid4().hex,
        alias="test_agent",
        collection_id=id,
        api_key="test_api_key",
        update_frequency=10,
        containers=[]
    )

    user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
    user_obj = User(**user)
    user_obj.servers.append(test_agent)
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, user_obj.dict(by_alias=True)
    )

    test_data_collection = AsyncMongoMockClient()["data"][id]
    monkeypatch.setattr(app_module.app, "db_data", {id: test_data_collection})

    client.headers = {"Authorization": f"Bearer {token}"}
    with client.websocket_connect("/ws/") as websocket:

        message = {
            "type": "get_container_data",
            "agent_id": id,
            "container_id": "test",
            "time_start": datetime.datetime.now().isoformat(),
            "time_span_minutes": 30
        }
        websocket.send_json(message)

        response = websocket.receive_text()
        data = json.loads(response)

        assert "data" in data
        assert "next_time_start" in data


async def test_get_agent_summary(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # Login and get token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    id = uuid.uuid4().hex
    test_agent = AgentConfig(
        id=uuid.uuid4().hex,
        alias="test_agent",
        collection_id=id,
        api_key="test_api_key",
        update_frequency=10,
        containers=[]
    )

    user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
    user_obj = User(**user)
    user_obj.servers.append(test_agent)
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, user_obj.dict(by_alias=True)
    )

    test_data_collection = AsyncMongoMockClient()["data"][id]
    monkeypatch.setattr(app_module.app, "db_data", {id: test_data_collection})

    client.headers = {"Authorization": f"Bearer {token}"}
    with client.websocket_connect("/ws/") as websocket:

        message = {
            "type": "get_agent_summary",
            "agent_id": id,
        }
        websocket.send_json(message)

        response = websocket.receive_text()
        data = json.loads(response)

        assert "data" not in data
        assert "error" in data
        assert data["error"] == "invalid_agent_id"


@pytest.mark.asyncio
async def test_ws_invalid_message_type(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # Login and get token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    id = uuid.uuid4().hex
    test_agent = AgentConfig(
        id=uuid.uuid4().hex,
        alias="test_agent",
        collection_id=id,
        api_key="test_api_key",
        update_frequency=10,
        containers=[]
    )

    user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
    user_obj = User(**user)
    user_obj.servers.append(test_agent)
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, user_obj.dict(by_alias=True)
    )

    test_data_collection = AsyncMongoMockClient()["data"][id]
    monkeypatch.setattr(app_module.app, "db_data", {id: test_data_collection})

    client.headers = {"Authorization": f"Bearer {token}"}
    with client.websocket_connect("/ws/") as websocket:

        message = {"type": "invalid_message_type"}
        websocket.send_json(message)

        response = websocket.receive_text()
        data = json.loads(response)

        assert "error" in data
        assert data["error"] == "invalid_message_type"