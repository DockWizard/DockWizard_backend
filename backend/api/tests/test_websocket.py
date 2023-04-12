# import datetime
# import json
# import pytest
# import app as app_module

# from mongomock_motor import AsyncMongoMockClient
# from tests.utils import add_test_user, remove_test_user
# from fastapi.testclient import TestClient

# @pytest.fixture(autouse=True,scope="module")
# async def test_user():
#     await add_test_user()
#     yield
#     await remove_test_user()

# @pytest.mark.asyncio
# async def test_get_container_data():

#     client = TestClient(app_module.app)
#     with client.websocket_connect("/ws/") as websocket:

#         message = {
#             "type": "get_container_data",
#             "agent_id": "test",
#             "container_id": "test",
#             "time_start": datetime.datetime.now().isoformat(),
#             "time_span_minutes": 30
#         }
#         await websocket.send_json(message)

#         response = await websocket.receive_text()
#         data = json.loads(response)

#         assert "data" in data
#         assert "next_time_start" in data