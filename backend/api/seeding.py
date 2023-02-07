from models.agent import AgentTSObjetc
from datetime import datetime, timedelta
from pymongo import MongoClient
import random
from pydantic import BaseModel, HttpUrl
from settings import settings
import uuid
from database import get_db_users, get_db_tokens
from fastapi import APIRouter, Request, HTTPException
from routes.routes_auth import get_password_hash


def seed_db():
    print("seeding")
    client = MongoClient(settings.MONGO_URI)

    db = client.data
    db_users = get_db_users(request=Request)
    db_users.insert_one(user)

    # agent_id = "27017"
    # agent_list = db.list_collection_names()
    # if id in agent_list:
    #     db[agent_id].drop()

    # db.create_collection(
    #     agent_id,
    #     timeseries={
    #         "timeField": "timestamp",
    #         "metaField": "metadata",
    #         "granularity": "seconds"
    #     }
    # )

    # data: AgentTSObjetc = {
    #     "metadata":
    #         {
    #             "container_id": id,
    #             "container_name": "phinns api container",
    #             "type": "mem"
    #         },
    #     "timestamp": "2023-01-20T09:48:19.655Z",
    #     "value": 99
    # }
    # agent_data = AgentTSObjetc(**data)

    # date = datetime.now()

    # for i in range(60):
    #     agent_data.timestamp = date + timedelta(seconds=i)
    #     agent_data.metadata.container_id = id
    #     agent_data.value = random.randint(1, 100)
    #     db[id].insert_one(agent_data.dict())
    #     print(agent_data.dict(), "\n")


if __name__ == "__main__":
    seed_db()
