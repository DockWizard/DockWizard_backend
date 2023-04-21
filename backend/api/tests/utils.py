from mongomock_motor import AsyncMongoMockClient
from utils.auth_helpers import get_password_hash


# add test user function
async def add_test_user():

    # create a collection for the test user
    collection = AsyncMongoMockClient()["users"]["user_data"]
    # define what the test user should look like
    # is the same as the User model in models/user.py
    user_data = {
        "username": "test_user",
        "email": "test@test.com",
        "first_name": "test",
        "surname": "testesen",
        "servers": [],
        "_hashed_password": get_password_hash("password")
    }
    # insert the test user into the collection
    await collection.insert_one(user_data)

    return collection

# remove test user function
async def remove_test_user():
    collection = AsyncMongoMockClient()["users"]["user_data"]
    await collection.delete_one({"username": "test_user"})

# read binary file function
def read_text_file(file_path):
    with open(file_path, "rb") as file:
        file_contents = file.read()
    return file_contents