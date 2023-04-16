import pytest
import app as app_module

from app import app
from fastapi.testclient import TestClient
from tests.utils import add_test_user
from models.agent import AgentConfig, AgentTSObjectList, AgentTSObjetc
from mongomock_motor import AsyncMongoMockClient
from models.user import User
import uuid
import datetime


@pytest.fixture
def client():
    from app import app
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_insert_data(client, monkeypatch):

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

    test_agent = AgentConfig(
        id=uuid.uuid4().hex,
        alias="test_agent",
        collection_id="test_data_collection",
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

    async def mock_get_agent(request):
        return test_agent

    monkeypatch.setattr(app_module, "agent_scheme", mock_get_agent)

    # create a test data collection
    test_data_collection = AsyncMongoMockClient(
    )["data"]["test_data_collection"]
    monkeypatch.setattr(
        app_module.app, "db_data",
        {"test_data_collection": test_data_collection}
    )

    # create a test data object
    test_data = [
        {
            "metadata":
                {
                    "container_id": "1234",
                    "container_name": "test_container",
                    "container_image": "test_image",
                    "container_state": "unknown"
                },
            "timestamp": datetime.datetime.now().timestamp(),
            "data":
                {
                    "cpu": 0.5,
                    "memory_perc": 50,
                    "memory_tot": 1024,
                    "total_rx": 100,
                    "total_tx": 100,
                    "io_read": 50,
                    "io_write": 50,
                    "healthcheck": True
                }
        }
    ]

    response = client.post(
        "/agent/send_data",
        headers={"Authorization": "Bearer test_api_key"},
        json={"data": test_data}
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"201": "Created"}

    # check if the data was inserted
    inserted_data = await test_data_collection.find().to_list(length=None)
    assert len(inserted_data) == len(test_data)

    for data_item, test_data_item in zip(inserted_data, test_data):
        assert data_item["metadata"] == test_data_item["metadata"]
        assert data_item["data"] == test_data_item["data"]