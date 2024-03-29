from fastapi import APIRouter, Request
from models.agent import AgentTSObjectList
from utils.auth_helpers import agent_scheme

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    responses={404: {
        "description": "Not found"
    }},
)


@router.post("/send_data")
async def insert_data(request: Request, agent_object: AgentTSObjectList):
    agent = await agent_scheme(request)
    data = [obj.dict() for obj in agent_object.data]
    await agent.data.insert_many(data)

    return {201: "Created"}
