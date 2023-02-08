from fastapi import APIRouter, Request, HTTPException
from models.agent import AgentTSObjetcList
from database import get_db_data

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.post("/{collection_id}")
async def insert_data(request: Request, agent_object: AgentTSObjetcList):
    db = get_db_data(request)
    mapped = map(lambda x: x.dict(), agent_object.data)
    collection_id = agent_object.agent_id

    # Check if collection exists. Is not implicit it exists when config says so.
    collection_list = await db.list_collection_names()
    if collection_id in collection_list:
        await db[collection_id].insert_many(mapped)
    else:
        raise HTTPException(404, "Collection not found")
    return {201: "Created"}
