from pymongo import MongoClient
from fastapi import Request, APIRouter
from models.agent import AgentTSObjetc, AgentConfig
from models.user import User, CreateNewAgentConfig
from models.auth import CreateUserRequest
import random
from datetime import datetime, timedelta
from database import get_db_data
from settings import settings
import uuid
from routes.routes_auth import get_password_hash
from database import get_db_users

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


@router.post("/seed")
async def seed_db(request: Request):
    print("seeding")

    db = get_db_data(request)

    agent_id = uuid.uuid4().hex
    agent_list = await db.list_collection_names()
    if agent_id in agent_list:
        await db[agent_id].drop()

    await db.create_collection(
        agent_id,
        timeseries={
            "timeField": "timestamp",
            "metaField": "metadata",
            "granularity": "seconds"
        }
    )
    await db[agent_id].create_index([("metadata.container_id", 1)])

    containers = [
        ("api", "101"),
        ("db", "102"),
        ("web", "103"),
        ("nginx", "104"),
        ("redis", "105"),
    ]

    date = datetime.now()
    insert_many_list = []

    for i in range(500):
        data: AgentTSObjetc = {
            "timestamp": "2023-01-20T09:48:19.655Z",
            "metadata":
                {
                    "container_id": containers[i % 5][1],
                    "container_name": containers[i % 5][0],
                },
            "data":
                {
                    "cpu": str(random.randint(0, 100)),
                    "memory_perc": str(random.randint(0, 100)),
                    "memory_tot": str(random.randint(0, 4000)),
                    "net_io": str(random.randint(0, 100000)),
                    "block_io": str(random.randint(0, 4000)),
                    "healthcheck": str(random.choice([True, False]))
                }
        }
        servicedata = AgentTSObjetc(**data)
        servicedata.timestamp = date + timedelta(seconds=i * 10)
        insert_many_list.append(servicedata.dict())

    await db[agent_id].insert_many(insert_many_list)

    return {200: f"Seeded collection {agent_id}"}


@router.get("/seed_ola")
# Deletes whoel user collection and creates a new server for 'ola'.
# Also creates a new collection for the new server, seeding it with 100 Agent Time Series objects.
async def seed_ola(request: Request):
    db = get_db_users(request)
    db_data = get_db_data(request)

    data = {
        "first_name": "ola",
        "surname": "nordmann",
        "username": "ola",
        "email": "ola@email.com",
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
        print("Found Ola", count)
        db.delete_many({})
    await db.insert_one(new_user_dict)

    alias = {"alias": "Ola's server"}
    payload = CreateNewAgentConfig(**alias)
    # Update user with new server config
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
        {"username": create_request.username},
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
                "container_name": "Olas api container",
                "type": "mem"
            },
        "timestamp": "2023-01-20T09:48:19.655Z",
        "data":
            {
                "cpu": random.randint(1, 100),
                "memory_perc": 66,
                "memory_tot": 55,
                "net_io": 33,
                "block_io": 33
            }
    }
    agent_data = AgentTSObjetc(**data)

    date = datetime.now()

    for i in range(100):
        agent_data.timestamp = date + timedelta(seconds=i)
        agent_data.metadata.container_id = uuid.uuid4().hex
        await db_data[new_server.collection_id].insert_one(agent_data.dict())
        print(agent_data.metadata.container_id)

    return {200: "Seeded Ola"}
