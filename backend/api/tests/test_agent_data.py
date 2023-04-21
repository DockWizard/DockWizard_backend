import pytest
import app as app_module

from app import app
from fastapi.testclient import TestClient
from tests.utils import add_test_user
from models.agent import AgentTSObjetc, AgentConfig, AgentContainerConfig
from mongomock_motor import AsyncMongoMockClient
from models.user import User, CreateNewAgentConfig
from routes import routes_agent_data
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
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    #login and get the bearer token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    agent_data = [
        AgentTSObjetc(
            metadata={
                "container_id": "1234",
                "container_name": "test_container",
                "container_image": "test_image"
            },
            timestamp=datetime.datetime(
                2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc
            ),
            data={
                "cpu": 0.5,
                "memory_perc": 50,
                "memory_tot": 1024,
                "total_rx": 100,
                "total_tx": 100,
                "io_read": 50,
                "io_write": 50,
                "healthcheck": True
            }
        )
    ]
    find_obj = [obj.dict() for obj in agent_data]
    collection_id = uuid.uuid4().hex
    data_collection = AsyncMongoMockClient()["data"][collection_id]
    await data_collection.insert_many(find_obj)

    monkeypatch.setattr(
        app_module.app, "db_data", {collection_id: data_collection}
    )

    # Update the test user's server list to include the new collection_id
    test_user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
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
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, test_user_obj.dict(by_alias=True)
    )

    response = client.get(
        f"/agent_data/data/{collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())
    expedted = [
        {
            'metadata':
                {
                    'container_id': '1234',
                    'container_name': 'test_container',
                    'container_image': 'test_image',
                    'container_state': 'unknown'
                },
            'timestamp': '2023-03-20T12:00:00',
            'data':
                {
                    'cpu': 0.5,
                    'memory_perc': 50.0,
                    'memory_tot': 1024,
                    'total_rx': 100,
                    'total_tx': 100,
                    'io_read': 50,
                    'io_write': 50,
                    'healthcheck': True
                }
        }
    ]

    assert response.status_code == 200
    assert response.json() == expedted


@pytest.mark.asyncio
async def test_get_agent_containers(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    #login and get the bearer token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    #add test data
    agent_data = [
        AgentTSObjetc(
            metadata={
                "container_id": "1234",
                "container_name": "test_container",
                "container_image": "test_image"
            },
            timestamp=datetime.datetime(
                2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc
            ),
            data={
                "cpu": 0.5,
                "memory_perc": 50,
                "memory_tot": 1024,
                "total_rx": 100,
                "total_tx": 100,
                "io_read": 50,
                "io_write": 50,
                "healthcheck": True
            }
        ),
        AgentTSObjetc(
            metadata={
                "container_id": "5678",
                "container_name": "test_container2",
                "container_image": "test_image2"
            },
            timestamp=datetime.datetime(
                2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc
            ),
            data={
                "cpu": 0.7,
                "memory_perc": 70,
                "memory_tot": 1024,
                "total_rx": 70,
                "total_tx": 70,
                "io_read": 70,
                "io_write": 70,
                "healthcheck": True
            }
        )
    ]
    find_obj = [obj.dict() for obj in agent_data]
    collection_id = uuid.uuid4().hex
    data_collection = AsyncMongoMockClient()["data"][collection_id]
    await data_collection.insert_many(find_obj)
    monkeypatch.setattr(
        app_module.app, "db_data", {collection_id: data_collection}
    )

    # Update the test user's server list to include the new collection_id
    test_user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
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
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, test_user_obj.dict(by_alias=True)
    )

    response = client.get(
        f"/agent_data/data/{uuid.uuid4().hex}/containers",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

    response = client.get(
        f"/agent_data/data/{collection_id}/containers",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_container_data(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    #login and get the bearer token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]  #add test data
    agent_data = [
        AgentTSObjetc(
            metadata={
                "container_id": "1234",
                "container_name": "test_container",
                "container_image": "test_image"
            },
            timestamp=datetime.datetime(
                2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc
            ),
            data={
                "cpu": 0.5,
                "memory_perc": 50,
                "memory_tot": 1024,
                "total_rx": 100,
                "total_tx": 100,
                "io_read": 50,
                "io_write": 50,
                "healthcheck": True
            }
        )
    ]
    find_obj = [obj.dict() for obj in agent_data]
    collection_id = uuid.uuid4().hex
    data_collection = AsyncMongoMockClient()["data"][collection_id]
    await data_collection.insert_many(find_obj)
    monkeypatch.setattr(
        app_module.app, "db_data", {collection_id: data_collection}
    )

    # Update the test user's server list to include the new collection_id
    test_user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
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
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, test_user_obj.dict(by_alias=True)
    )

    # define test data
    container_id = "1234"
    time_span_minutes = 10

    response = client.get(
        f"/agent_data/data/{collection_id}/containers/{container_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"time_span_minutes": time_span_minutes}
    )
    print(response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_agent_summary(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    #login and get the bearer token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    #add test data
    agent_data = [
        AgentTSObjetc(
            metadata={
                "container_id": "1234",
                "container_name": "test_container",
                "container_image": "test_image"
            },
            timestamp=datetime.datetime(
                2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc
            ),
            data={
                "cpu": 0.5,
                "memory_perc": 50,
                "memory_tot": 1024,
                "total_rx": 100,
                "total_tx": 100,
                "io_read": 50,
                "io_write": 50,
                "healthcheck": True
            }
        )
    ]
    find_obj = [obj.dict() for obj in agent_data]
    collection_id = uuid.uuid4().hex
    data_collection = AsyncMongoMockClient()["data"][collection_id]
    await data_collection.insert_many(find_obj)
    monkeypatch.setattr(
        app_module.app, "db_data", {collection_id: data_collection}
    )

    # Update the test user's server list to include the new collection_id
    test_user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
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
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, test_user_obj.dict(by_alias=True)
    )

    # define test data
    time_span_minutes = 180

    response = client.get(
        f"/agent_data/data/{collection_id}/containers/summary/{time_span_minutes}",
        headers={"Authorization": f"Bearer {token}"},
        params={"time_span_minutes": time_span_minutes}
    )
    print(f"print response {response.json()}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_container_data(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    #login and get the bearer token
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    #add test data
    agent_data = [
        AgentTSObjetc(
            metadata={
                "container_id": "1234",
                "container_name": "test_container",
                "container_image": "test_image"
            },
            timestamp=datetime.datetime(
                2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc
            ),
            data={
                "cpu": 0.5,
                "memory_perc": 50,
                "memory_tot": 1024,
                "total_rx": 100,
                "total_tx": 100,
                "io_read": 50,
                "io_write": 50,
                "healthcheck": True
            }
        )
    ]
    find_obj = [obj.dict() for obj in agent_data]
    collection_id = uuid.uuid4().hex
    data_collection = AsyncMongoMockClient()["data"][collection_id]
    await data_collection.insert_many(find_obj)
    monkeypatch.setattr(
        app_module.app, "db_data", {collection_id: data_collection}
    )

    # Update the test user's server list to include the new collection_id
    test_user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
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
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, test_user_obj.dict(by_alias=True)
    )

    # delete container data
    response = client.delete(
        f"/agent_data/data/{collection_id}/containers/1234",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # check if data is deleted
    remaining_data = await data_collection.find(
        {
            "metadata.container_id": 1234
        }
    ).to_list(length=100)
    assert len(remaining_data) == 0


# fails
@pytest.mark.asyncio
async def test_config_new_agent(client, monkeypatch):
    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # login
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )

    res_json = response.json()
    token = res_json["bearer_token"]

    data_collection = AsyncMongoMockClient()["data"]

    monkeypatch.setattr(app_module.app, "db_data", data_collection)

    routes_agent_data.should_use_timeseries_options = False

    # configure a new agent
    new_agent_alias = "new_test_agent"
    response = client.post(
        "/agent_data/config_new_agent",
        headers={"Authorization": f"Bearer {token}"},
        json={"alias": new_agent_alias}
    )

    print(f"print response {response.json()}")
    assert response.status_code == 200

    # check if the new agent is added to the user's server list
    test_user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
    test_user_obj = User(**test_user)
    new_agent_found = False
    for server in test_user_obj.servers:
        if server.alias == new_agent_alias:
            new_agent_found = True
            break
    assert new_agent_found


@pytest.mark.asyncio
async def test_get_agents(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # login
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    # add test agent to the user
    test_agent = AgentConfig(
        id=uuid.uuid4().hex,
        alias="test_agent",
        collection_id=uuid.uuid4().hex,
        api_key="test_api_key",
        update_frequency=5,
        containers=[]
    )
    await app_module.app.db_users["user_data"].find_one_and_update(
        {"username": "test_user"},
        {"$push": {
            "servers": test_agent.dict(by_alias=True)
        }}
    )

    # get agents
    response = client.get(
        "/agent_data/agents", headers={"Authorization": f"Bearer {token}"}
    )
    print(f"print response {response.json()}")
    assert response.status_code == 200
    agents = response.json()

    # check if the test agent is in the list
    test_agent_found = False
    for agent in agents:
        if agent["alias"] == test_agent.alias:
            test_agent_found = True
            break
    assert test_agent_found


@pytest.mark.asyncio
async def test_get_agent(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # login
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    # add test agent to the user
    test_agent = AgentConfig(
        id=uuid.uuid4().hex,
        alias="test_agent",
        collection_id=uuid.uuid4().hex,
        api_key="test_api_key",
        update_frequency=5,
        containers=[]
    )
    await app_module.app.db_users["user_data"].find_one_and_update(
        {"username": "test_user"},
        {"$push": {
            "servers": test_agent.dict(by_alias=True)
        }}
    )

    # get agent by agent id
    response = client.get(
        f"/agent_data/agents/{test_agent.collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"print response {response.json()}")
    assert response.status_code == 200
    agent = AgentConfig(**response.json())

    # check if the test agent is in the list
    assert agent.alias == test_agent.alias
    assert agent.collection_id == test_agent.collection_id
    assert agent.api_key == test_agent.api_key
    assert agent.update_frequency == test_agent.update_frequency
    assert agent.containers == test_agent.containers


@pytest.mark.asyncio
async def test_update_agent(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # login
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    # add test agent to the user
    test_agent = AgentConfig(
        alias="test_agent",
        collection_id=uuid.uuid4().hex,
        api_key="test_api_key",
        update_frequency=5,
        containers=[]
    )
    await app_module.app.db_users["user_data"].find_one_and_update(
        {"username": "test_user"},
        {"$push": {
            "servers": test_agent.dict(by_alias=True)
        }}
    )

    # update agent
    updated_agent_config = AgentConfig(
        alias="updated_test_agent",
        collection_id=test_agent.collection_id,
        api_key=test_agent.api_key,
        update_frequency=10,
        containers=test_agent.containers
    )
    response = client.put(
        f"/agent_data/config/{test_agent.collection_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=updated_agent_config.dict(by_alias=True)
    )
    assert response.status_code == 200

    # get updated agent
    response = client.get(
        f"/agent_data/agents/{test_agent.collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    updated_agent = AgentConfig(**response.json())
    assert updated_agent.alias == updated_agent_config.alias
    assert updated_agent.collection_id == updated_agent_config.collection_id
    assert updated_agent.api_key == updated_agent_config.api_key
    assert updated_agent.update_frequency == updated_agent_config.update_frequency
    assert updated_agent.containers == updated_agent_config.containers


# fails
@pytest.mark.asyncio
async def test_delete_agent(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # login
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    data_collection = AsyncMongoMockClient()["data"]

    monkeypatch.setattr(app_module.app, "db_data", data_collection)

    # add test agent to the user
    test_agent = AgentConfig(
        alias="test_agent",
        collection_id=uuid.uuid4().hex,
        api_key="test_api_key",
        update_frequency=5,
        containers=[]
    )
    await app_module.app.db_users["user_data"].find_one_and_update(
        {"username": "test_user"},
        {"$push": {
            "servers": test_agent.dict(by_alias=True)
        }}
    )

    # delete agent
    response = client.delete(
        f"/agent_data/config/{test_agent.collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # get agent list
    response = client.get(
        "/agent_data/agents", headers={"Authorization": f"Bearer {token}"}
    )
    agents = [AgentConfig(**agent) for agent in response.json()]
    assert test_agent not in agents


@pytest.mark.asyncio
async def test_regenerate_api_key(client, monkeypatch):

    collection = await add_test_user()
    monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

    token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
    monkeypatch.setattr(
        app_module.app, "db_tokens", {"token_data": token_collection}
    )

    # login
    response = client.post(
        "/auth/login", json={
            "username": "test_user",
            "password": "password"
        }
    )
    res_json = response.json()
    token = res_json["bearer_token"]

    # add test agent to the user
    test_agent = AgentConfig(
        alias="test_agent",
        collection_id=uuid.uuid4().hex,
        api_key="old_api_key",
        update_frequency=5,
        containers=[]
    )
    await app_module.app.db_users["user_data"].find_one_and_update(
        {"username": "test_user"},
        {"$push": {
            "servers": test_agent.dict(by_alias=True)
        }}
    )

    # get users info
    user = await app_module.app.db_users["user_data"].find_one(
        {"username": "test_user"}
    )
    user_obj = User(**user)

    # find the agent to update and change its api key
    for server in user_obj.servers:
        if server.collection_id == test_agent.collection_id:
            server.api_key = "new_api_key"
            break

    # update users server list
    await app_module.app.db_users["user_data"].replace_one(
        {"username": "test_user"}, user_obj.dict(by_alias=True)
    )

    # regenerate api key for agent
    response = client.get(
        f"/agent_data/config/regenerate_api_key/{test_agent.collection_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # check if regenerated api key is different from original one
    regenerated_agent = AgentConfig(**response.json())
    assert regenerated_agent.api_key != test_agent.api_key
