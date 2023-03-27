import pytest
import app as app_module

from app import app
from fastapi.testclient import TestClient
from tests.utils import add_test_user
from models.agent import AgentTSObjetc, AgentConfig, AgentContainerConfig
from mongomock_motor import AsyncMongoMockClient
from models.user import User, CreateNewAgentConfig
import uuid
import datetime



@pytest.fixture
def client():
    from app import app
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_get_agent_data(client, monkeypatch):
    # Add test user
    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})


    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})


    #login and get the bearer token
    response = client.post("/auth/login", json={"username": "test_user", "password": "password"})
    res_json = response.json()
    token = res_json["bearer_token"]

    agent_data = [AgentTSObjetc(
        metadata={
            "container_id": "1234",
            "container_name": "test_container",
            "container_image": "test_image"
        },
        timestamp=datetime.datetime(2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc),
        data={
            "cpu": 0.5,
            "memory_perc": 50,
            "memory_tot": 1024,
            "total_rx": 100,
            "total_tx": 100,
            "io_read": 50,
            "io_write": 50,
            "healthcheck": True
        })
    ]
    find_obj = [obj.dict() for obj in agent_data]
    collection_id = uuid.uuid4().hex
    data_collection = AsyncMongoMockClient()["data"][collection_id]
    await data_collection.insert_many(find_obj)

    monkeypatch.setattr(app_module.app, "db_data", {collection_id: data_collection})


    # Update the test user's server list to include the new collection_id
    test_user = await app_module.app.db_users["user_data"].find_one({"username": "test_user"})
    test_user_obj = User(**test_user)
    if len(test_user_obj.servers) > 0:
        test_user_obj.servers[0].collection_id = collection_id
    else:
        new_server = AgentConfig(
            id=uuid.uuid4().hex,
            alias="test_server",
            collection_id=collection_id,
            api_key="test_api_key",
            update_frequency=5,
            containers=[]
        )
        test_user_obj.servers.append(new_server)
    await app_module.app.db_users["user_data"].replace_one({"username": "test_user"}, test_user_obj.dict(by_alias=True))


    response = client.get(
        f"/agent_data/data/{collection_id}", 
        headers={"Authorization": f"Bearer {token}"})
    expedted = [{'metadata': {'container_id': '1234', 'container_name': 'test_container', 'container_image': 'test_image'}, 'timestamp': '2023-03-20T12:00:00', 'data': {'cpu': 0.5, 'memory_perc': 50.0, 'memory_tot': 1024, 'total_rx': 100, 'total_tx': 100, 'io_read': 50, 'io_write': 50, 'healthcheck': True}}]
    
    assert response.status_code == 200
    assert response.json() == expedted



### status code wrong??
@pytest.mark.asyncio
async def test_config_new_agent(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})

    #login and get the bearer token
    response = client.post("/auth/login",
                            json={"username": "test_user", "password": "password"})
    res_json = response.json()
    token = res_json["bearer_token"]

    # Create a new agent config
    new_agent_config = CreateNewAgentConfig(alias="test_alias")

    response = client.post(
        "/agent_data/config_new_agent",
        json=new_agent_config.dict(),
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    print(f"sssss\n\n\n{response.json()}")
    # assert response.json() == 

    # Check that the new agent config was added to the user's server list
    test_user = await app_module.app.db_users["user_data"].find_one({"username": "test_user"})
    test_user_obj = User(**test_user)
    assert len(test_user_obj.servers) == 1
    assert test_user_obj.servers[0].alias == "test_alias"
    assert test_user_obj.servers[0].api_key is not None
    assert test_user_obj.servers[0].update_frequency is not None
    assert len(test_user_obj.servers[0].containers) == 0



# fails
# @pytest.mark.asyncio
# async def test_get_agents(client, monkeypatch):

#     test_user = User(
#         username="test_user",
#         password="password",
#         email="test@test.com",
#         first_name="test",
#         surname="testesen",
#         servers=[AgentConfig(
#             id="test_server",
#             alias="test_server",
#             collection_id="test_collection",
#             api_key="test_api_key",
#             update_frequency=5,
#             containers=[]
#         )],
#     )
#     collection = AsyncMongoMockClient()["users"]["user_data"]
#     await collection.insert_one(test_user.dict(by_alias=True))
#     monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

#     token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
#     monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})

#     response = client.post("/auth/login",
#                            json={"username": "test_user", 
#                                 "password": "password"})
#     res_json = response.json()
#     token = res_json["bearer_token"]


#     response = client.get("/agent_data/get_agents",
#                           headers={"Authorization": f"Bearer {token}"}
#                           )
#     assert response.status_code == 200
#     assert len(response.json()) == 1  



## fails
# @pytest.mark.asyncio
# async def test_get_agent(client, monkeypatch):

#     test_user = User(
#         username="test_user",
#         password="password",
#         email="test@test.com",
#         first_name="test",
#         surname="testesen",
#         servers=[AgentConfig(
#             id="test_server",
#             alias="test_alias",
#             collection_id="test_collection",
#             api_key="test_api_key",
#             update_frequency=5,
#             containers=[]
#         )],
#     )

#     collection = AsyncMongoMockClient()["users"]["user_data"]
#     await collection.insert_one(test_user.dict(by_alias=True))
#     monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

#     token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
#     monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})

#     response = client.post("/auth/login",
#                            json={"username": "test_user",
#                                  "password": "password"})
#     res_json = response.json()
#     token = res_json["bearer_token"]

#     # get the test server id
#     server_id = test_user.servers[0].collection_id

#     response = client.get(f"/agent_data/get_agent/{server_id}",
#                           headers={"Authorization": f"Bearer {token}"}
#                             )
#     assert response.status_code == 200

#     server = response.json()
#     assert server["id"] == "test_server"
#     assert server["alias"] == "test_alias"
#     assert server["collection_id"] == "test_collection"
#     assert server["api_key"] == "test_api_key"
#     assert server["update_frequency"] == 5
#     assert server["containers"] == []

#     # test for failure
#     response = client.get(f"/agent_data/get_agent/1234",
#                           headers={"Authorization": f"Bearer {token}"}
#                             )
#     assert response.status_code == 404

    

# @pytest.mark.asyncio
# async def test_update_agent(client, monkeypatch):
