# import pytest
# import app as app_module

# from app import app
# from fastapi.testclient import TestClient
# from mongomock_motor import AsyncMongoMockClient


# @pytest.fixture
# def client():
#     from app import app
#     with TestClient(app) as test_client:
#         yield test_client

# @pytest.mark.asyncio
# async def test_cleanup_db_data(client, monkeypatch):

#     db_data_collection = AsyncMongoMockClient()["data"]["data_collection"]
#     monkeypatch.setattr(app_module, "db_data", {"db_data_collection": db_data_collection})
    
#     sample_data = [
#         {
#             "key": "value1"
#         },
#         {
#             "key": "value2"
#         }
#     ]
#     await db_data_collection.insert_many(sample_data)
    
        
#     response = client.delete("/database/data")
#     assert response.status_code == 200
#     assert response.json() == sample_data


# @pytest.fixture
# def mock_async_mongo_client():
#     async def _mock_async_mongo_client():
#         return AsyncMongoMockClient()
#     return _mock_async_mongo_client

# @pytest.mark.asyncio
# async def test_cleanup_db_users(client, mock_async_mongo_client):
    