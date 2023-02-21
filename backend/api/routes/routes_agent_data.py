from uuid import uuid4, UUID
from fastapi import APIRouter, Request, HTTPException
from models.agent import AgentConfig, AgentTSObjetc
from models.user import User, CreateNewAgentConfig
import secrets
from database import get_db_data, get_db_users
from utils.auth_helpers import user_scheme
from typing import List

router = APIRouter(
    prefix="/agent_data",
    tags=["agent_data"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.get("/data/{collection_id}")
# Will return all documents in a collection(server with collection id)
async def get_agent_data(request: Request, collection_id: str):
    db = get_db_data(request)
    user: User = await user_scheme(request)
    for server in user.servers:
        if server.collection_id != collection_id:
            raise HTTPException(404, "No agent configured with that id")
    cursor = db[UUID(collection_id).hex].find({})
    return [
        AgentTSObjetc.parse_obj(doc)
        for doc in await cursor.to_list(length=None)
    ]


@router.get(
    "/data/{collection_id}/containers", response_model=List[AgentTSObjetc]
)
# Will return all containers as the first agentTSobject instance that match.
async def get_agent_containers(request: Request, collection_id: str):
    db = get_db_data(request)
    user: User = await user_scheme(request)
    for server in user.servers:
        if server.collection_id == collection_id:
            print("CONTAINERS", server.collection_id, collection_id)
            cursor = db[UUID(collection_id).hex
                       ].distinct("metadata.container_id")

            if cursor is None:
                raise HTTPException(404, "No containers found")

            containers = [doc for doc in await cursor]

            container_list = []
            for container in containers:
                cursor = db[UUID(collection_id).hex].find_one(
                    {"metadata.container_id": container}
                )
                container_list.append(AgentTSObjetc.parse_obj(await cursor))
            return container_list

    raise HTTPException(404, "No agent configured with that id")


@router.get("/data/{collection_id}/containers/{container_id}")
# Will return all documents in a collection(server with collection id)
async def get_container_data(
    request: Request, collection_id: str, container_name: str
):
    db = get_db_data(request)
    user: User = await user_scheme(request)
    for server in user.servers:
        if server.collection_id != collection_id:
            raise HTTPException(404, "No agent configured with that id")
    cursor = db[UUID(collection_id).hex].find(
        {"metadata.container_name": container_name}
    )
    return [
        AgentTSObjetc.parse_obj(doc)
        for doc in await cursor.to_list(length=None)
    ]


@router.post("/config_new_agent")
async def config_new_agent(request: Request, payload: CreateNewAgentConfig):
    db_data = get_db_data(request)
    db_users = get_db_users(request)
    user: User = await user_scheme(request)

    if not user:
        raise HTTPException(404, "User could not be found")
    for server in user.servers:
        print(server.alias, payload.alias, "\n\n")
        if server.alias == payload.alias:
            raise HTTPException(400, "Alias already exists")
    try:
        # Update user with new server config
        api_token = secrets.token_urlsafe(32)

        new_server = {
            "collection_id": uuid4().hex,
            "alias": payload.alias,
            "api_key": api_token,
            "update_frequency": 5,
            "containers": []
        }
        new_server = AgentConfig(**new_server)
        print(new_server)
        await db_users.find_one_and_update(
            {"username": user.username},
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
        await db_data[new_server.collection_id].create_index(
            [("metadata.container_id", 1)]
        )

        return {201: "Created", "collection_id": new_server}
    except Exception as exc:
        return {400: "Bad request", "error": str(exc)}


@router.get("/agents")
async def get_agents(request: Request):
    user: User = await user_scheme(request)
    if not user:
        raise HTTPException(404, "User could not be found")

    return [AgentConfig.parse_obj(i) for i in user.servers]


@router.get("/agents/{agent_id}")
async def get_agent(request: Request, agent_id: str):
    db = get_db_users(request)
    user: User = await user_scheme(request)
    if not user:
        raise HTTPException(404, "User could not be found")

    for server in user.servers:
        if server.collection_id == agent_id:
            return AgentConfig.parse_obj(server)

    raise HTTPException(404, "No agent configured with that id")


# Needs fix! should not be able to change collection_id
@router.put("/config/{agent_id}")
async def update_agent(request: Request, agent_id: str, payload: AgentConfig):
    db_users = get_db_users(request)
    user: User = await user_scheme(request)
    if not user:
        raise HTTPException(404, "User could not be found")

    for server in user.servers:
        if server.collection_id == agent_id:
            await db_users.find_one_and_update(
                {
                    "username": user.username,
                    "servers.collection_id": agent_id
                }, {
                    "$set":
                        {
                            "servers.$.update_frequency":
                                payload.update_frequency,
                            "servers.$.alias":
                                payload.alias
                        }
                }
            )
            return {200: "OK"}
    raise HTTPException(404, "Agent could not be found")


@router.delete("/config/{agent_id}")
async def delete_agent(request: Request, agent_id: str):
    db_users = get_db_users(request)
    db_data = get_db_data(request)
    user: User = await user_scheme(request)
    if not user:
        raise HTTPException(404, "User could not be found")

    try:
        for server in user.servers:
            if server.collection_id == agent_id:
                # Try drop the collection before reference(config) is deleted
                await db_data.drop_collection(agent_id)
                await db_users.find_one_and_update(
                    {"username": user.username},
                    {"$pull": {
                        "servers": server.dict()
                    }}
                )

                return {200: "OK"}
    except Exception as exc:
        raise HTTPException(404, "Something went wrong", str(exc))
    raise HTTPException(404, "Agent could not be found")
