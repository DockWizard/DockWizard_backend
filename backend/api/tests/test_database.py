
###############
# Does not work
###############




# import pytest
# from fastapi.testclient import TestClient


# from pymongo import MongoClient
# from settings import settings




# @pytest.mark.asyncio
# async def test_cleanup_db_data():
#     from app import app
#     client = TestClient(app)

#     # Insert a test document into the "data" database to ensure it gets deleted
#     mongo_client = MongoClient(settings.MONGO_URI)
#     data_db = mongo_client["data"]
#     test_collection = data_db["test_collection"]
#     test_doc = {"test_key": "test_value"}
#     test_collection.insert_one(test_doc)

#     # Make the DELETE request to the endpoint
#     response = client.delete("/database/data")
#     assert response.status_code == 200
#     assert response.json() == {"200": "Deleted DATA database"}

#     # Ensure that the "data" database no longer exists
#     assert "data" not in mongo_client.list_database_names()