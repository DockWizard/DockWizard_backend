# import pytest
# import app as app_module

# from app import app
# from fastapi.testclient import TestClient
# from tests.utils import add_test_user
# from models.agent import AgentConfig, AgentTSObjectList, AgentTSObjetc
# from mongomock_motor import AsyncMongoMockClient
# from models.user import User
# import uuid
# import datetime




# @pytest.fixture
# def client():
#     from app import app
#     with TestClient(app) as test_client:
#         yield test_client

# @pytest.mark.asyncio
# async def test_insert_data(client, monkeypatch):

#     collection = await add_test_user()
#     monkeypatch.setattr(app_module.app, "db_users", {"user_data": collection})

#     token_collection = AsyncMongoMockClient()["tokens"]["token_data"]
#     monkeypatch.setattr(app_module.app, "db_tokens", {"token_data": token_collection})

#     response = client.post(
#         "/auth/login",
#         json={
#         "username": "test_user",
#         "password": "password",
#         })
#     res_json = response.json()
#     print(res_json)
#     token = res_json["bearer_token"]

#     # add a server to the user
#     new_server = AgentConfig(
#         id=uuid.uuid4().hex,
#         alias="test_server",
#         collection_id=uuid.uuid4().hex,
#         api_key="test_api_key",
#         update_frequency=10,
#         containers=[]
#     )

#     test_user = await app_module.app.db_users["user_data"].find_one({"username": "test_user"})
#     test_user_obj = User(**test_user)
#     test_user_obj.servers.append(new_server)
#     await app_module.app.db_users["user_data"].replace_one({"username": "test_user"}, test_user_obj.dict(by_alias=True))

#     agent_data = [AgentTSObjetc(
#         metadata={
#             "container_id": "1234",
#             "container_name": "test_container",
#             "container_image": "test_image"
#         },
#         timestamp=datetime.datetime(2023, 3, 20, 12, 0, tzinfo=datetime.timezone.utc),
#         data={
#             "cpu": 0.5,
#             "memory_perc": 50,
#             "memory_tot": 1024,
#             "total_rx": 100,
#             "total_tx": 100,
#             "io_read": 50,
#             "io_write": 50,
#             "healthcheck": True
#         })
#     ]
    

    

#     agent_data_list = AgentTSObjectList(data=agent_data)


#     response = client.post("/agent/send_data",
#                            headers={"Authorization": f"Bearer {token}"},
#                             json=agent_data_list.dict()
#                             )
    
#     assert response.status_code == 201
#     assert response.json() == {201: "Created"}

#     test_user = await app_module.app.db_users["user_data"].find_one({"username": "test_user"})
#     test_user_obj = User(**test_user)
#     collection_id = test_user_obj.servers[0].collection_id
#     data_collection = app_module.app.db_data[collection_id]
#     db_data = await data_collection.find_one()
#     db_data_list = db_data["data"]
#     assert db_data_list[0] == agent_data[0].dict()

    