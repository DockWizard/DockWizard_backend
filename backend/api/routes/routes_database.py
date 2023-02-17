from pymongo import MongoClient
from fastapi import Request, APIRouter
from models.agent import AgentTSObjetc, AgentConfig
from models.user import User, CreateNewAgentConfig
from models.auth import CreateUserRequest
import random
from datetime import datetime, timedelta
from database import get_db_data, get_db_users
from settings import settings
import uuid
from routes.routes_auth import get_password_hash

router = APIRouter(
    prefix="/database",
    tags=["database"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.delete("/data")
async def cleanup_db_data():
    db = MongoClient(settings.MONGO_URI)
    db.drop_database("data")
    return {200: "Deleted DATA database"}


@router.delete("/users")
async def cleanup_db_client():
    db = MongoClient(settings.MONGO_URI)
    db.drop_database("users")
    return {200: "Deleted USERS database"}


@router.get("/seed_john")
# Deletes whole user collection and creates a new server for 'john'.
# Also creates a new collection for the new server, seeding it with 100 Agent Time Series objects.
async def seed_john(request: Request):
    db = get_db_users(request)

    data = {
        "first_name": "john",
        "surname": "nordmann",
        "username": "john",
        "email": "john@email.com",
        "password": "password",
        "confirm_password": "password"
    }
    create_request = CreateUserRequest(**data)
    password_hash = get_password_hash(create_request.password)
    user_dict = create_request.dict(exclude={"password", "confirm_password"})
    new_user = User(**user_dict)
    new_user_dict = new_user.dict()
    additional_fields = {
        "_hashed_password": password_hash,
        "servers": [],
    }

    new_user_dict.update(additional_fields)

    count = await db.count_documents({})
    if count != 0:
        print("Found john", count)
        db.delete_many({})
    await db.insert_one(new_user_dict)

    # Update user with new server config

    await add_server("REST api's", request)
    await add_server("Microservices", request)
    await add_server("Talos Cluster", request)
    await add_server("Utanix node", request)
    await add_server("Rocky", request)

    return {200: "Seeded John"}


async def add_server(alias: str, request: Request):
    db_data = get_db_data(request)
    db = get_db_users(request)

    config = {"alias": alias}
    payload = CreateNewAgentConfig(**config)

    new_server = {
        "collection_id": uuid.uuid4().hex,
        "alias": payload.alias,
        "api_key": uuid.uuid4().hex,
        "update_frequency": 5,
        "containers": []
    }
    new_server = AgentConfig(**new_server)
    print(new_server)
    await db.find_one_and_update(
        {"username": "john"},
        {"$push": {
            "servers": new_server.dict()
        }}
    )
    # Create new collection for new agent
    await db_data.create_collection(
        new_server.collection_id,
        timeseries={
            "timeField": "timestamp",
            "metaField": "metadata",
            "granularity": "seconds"
        }
    )
    await db_data[
        new_server.collection_id].create_index([("metadata.container_id", 1)])

    data: AgentTSObjetc = {
        "metadata":
            {
                "container_id": uuid.uuid4().hex,
                "container_name": "john api container",
                "container_image": "john/api:latest",
            },
        "timestamp": "2023-01-20T09:48:19.655Z",
        "data":
            {
                "cpu": random.randint(1, 100),
                "memory_perc": 66,
                "memory_tot": 55,
                "total_rx": 23,
                "total_tx": 65,
                "io_read": 65,
                "io_write": 65,
            }
    }
    agent_data = AgentTSObjetc(**data)

    date = datetime.now()

    for i in range(100):
        agent_data.timestamp = date + timedelta(seconds=i)
        agent_data.metadata.container_id = uuid.uuid4().hex
        await db_data[new_server.collection_id].insert_one(agent_data.dict())
        print(agent_data.metadata.container_id)
