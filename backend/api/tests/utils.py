from mongomock_motor import AsyncMongoMockClient

from utils.auth_helpers import get_password_hash

async def add_test_user():
    collection = AsyncMongoMockClient()["users"]["user_data"]
    user_data = {
        "username": "test_user",
        "email": "test@test.com",
        "first_name": "test",
        "surname": "testesen",
        "servers": [],
        "_hashed_password": get_password_hash("password")
    }
    await collection.insert_one(user_data)

    return collection

async def remove_test_user():
    collection = AsyncMongoMockClient()["users"]["user_data"]
    await collection.delete_one({"username": "test_user"})

    
def read_text_file(file_path):
    with open(file_path, "rb") as file:
        file_contents = file.read()
    return file_contents