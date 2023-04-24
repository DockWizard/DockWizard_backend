import datetime
from json import JSONDecodeError
from uuid import UUID
from fastapi import APIRouter, WebSocket, Depends
from models.agent import AgentTSObjetc
from models.user import User
from database import get_db_data
from utils.auth_helpers import user_scheme_websocket
from typing import Optional
from pydantic import BaseModel

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
    responses={404: {
        "description": "Not found"
    }},
)

# 5 minutes, 30 minutes, 1 hour, 6 hours, 1 day, 1 week, 1 month, 3 months
valid_time_spans = [5, 30, 60, 60 * 6, 60 * 24, 60 * 24 * 7, 60 * 24 * 7 * 4,
                    60 * 24 * 7 * 4 * 3]


class GetAgentSummaryMessage(BaseModel):
    agent_id: Optional[str]


class GetContainerDataMessage(BaseModel):
    agent_id: Optional[str]
    container_id: Optional[str]
    time_start: Optional[datetime.datetime]
    time_span_minutes: Optional[int]


async def get_agent_summary(
    websocket: WebSocket,
    user: User,
    msg: GetAgentSummaryMessage,
):
    agent_id = msg.agent_id
    if not agent_id:
        await websocket.send_json({"error": "invalid_agent_id"})
        return

    interval = 60  # minutes
    pipeline = [
        {
            "$match":
                {
                    "$expr":
                        {
                            "$gt":
                                [
                                    "$timestamp", {
                                    "$dateSubtract":
                                        {
                                            "startDate": "$$NOW",
                                            "unit": "minute",
                                            "amount": interval
                                        }
                                }
                                ]
                        },
                },
        },
    ]

    db = get_db_data(websocket)
    found_agent = False
    for server in user.servers:
        if server.collection_id == agent_id:
            agent_uuid = None
            try:
                agent_uuid = UUID(agent_id)
            except ValueError:
                await websocket.send_json({"error": "invalid_agent_id"})
                return
            cursor = db[agent_uuid.hex].aggregate(pipeline)

            content = "{\"data\": ["
            for doc in await cursor.to_list(length=100):
                content += AgentTSObjetc.parse_obj(doc).json() + ","
            if content[-1] == ",":
                content = content[:-1]
            content += "]}"
            await websocket.send({"type": "websocket.send", "text": content})
            found_agent = True

    if not found_agent:
        await websocket.send_json({"error": "agent_not_found"})


async def get_container_data(
    websocket: WebSocket,
    user: User,
    msg: GetContainerDataMessage,
):
    agent_id = msg.agent_id
    if not agent_id:
        await websocket.send_json({"error": "invalid_agent_id"})
        return
    container_id = msg.container_id
    if not container_id:
        await websocket.send_json({"error": "invalid_container_id"})
        return

    time_span_minutes = msg.time_span_minutes
    if not time_span_minutes or time_span_minutes not in valid_time_spans:
        await websocket.send_json({"error": "invalid_time_span_minutes"})
        return

    # If empty time_start, set to now
    if not msg.time_start:
        msg.time_start = datetime.datetime.now()

    time_span = msg.time_start - datetime.timedelta(minutes=time_span_minutes)

    # Fetch data
    hop_interval = 3600
    if time_span_minutes == 5:
        hop_interval = 0.1
    elif time_span_minutes == 30:
        hop_interval = 0.6
    elif time_span_minutes == 60:
        hop_interval = 1.2
    elif time_span_minutes == 60 * 6:
        hop_interval = 7.2
    elif time_span_minutes == 60 * 24:
        hop_interval = 15
    elif time_span_minutes == 60 * 24 * 7:
        hop_interval = 201.6
    elif time_span_minutes == 60 * 24 * 7 * 4:
        hop_interval = 806.4
    elif time_span_minutes == 60 * 24 * 7 * 4 * 3:
        hop_interval = 2419.2

    # Create a pipeline that matches timestamp greater than
    # time_span and container_id.
    # Each data should only take data from 5 second intervals
    # and take the average of each interval.
    pipeline = [
        {
            "$match":
                {
                    "$expr": {
                        "$gt": ["$timestamp", time_span]
                    },
                    "metadata.container_id": container_id
                },
        },
        {
            "$group":
                {
                    "_id":
                        {
                            "$toDate":
                                {
                                    "$subtract":
                                        [
                                            {
                                                "$toLong": {
                                                    "$toDate": "$_id"
                                                }
                                            }, {
                                            "$mod":
                                                [
                                                    {
                                                        "$toLong":
                                                            {
                                                                "$toDate":
                                                                    "$_id"
                                                            }
                                                    },
                                                    1000 * 60 * hop_interval
                                                ]
                                        }
                                        ]
                                }
                        },
                    "metadata": {
                        "$first": "$metadata"
                    },
                    "timestamp": {
                        "$last": "$timestamp"
                    },
                    # Accumulate all data in the data field and take the average
                    "cpu": {
                        "$avg": "$data.cpu"
                    },
                    "memory_perc": {
                        "$avg": "$data.memory_perc"
                    },
                    "memory_tot": {
                        "$avg": "$data.memory_tot"
                    },
                    "total_rx": {
                        "$avg": "$data.total_rx"
                    },
                    "total_tx": {
                        "$avg": "$data.total_tx"
                    },
                    "io_read": {
                        "$avg": "$data.io_read"
                    },
                    "io_write": {
                        "$avg": "$data.io_write"
                    },
                },
        },
        {
            "$sort": {
                "timestamp": 1
            }
        },
        {
            # Then reduce the data into the "data" field
            "$addFields":
                {
                    "data.cpu": "$cpu",
                    "data.memory_perc": "$memory_perc",
                    "data.memory_tot": "$memory_tot",
                    "data.total_rx": "$total_rx",
                    "data.total_tx": "$total_tx",
                    "data.io_read": "$io_read",
                    "data.io_write": "$io_write",
                }
        },
        {
            "$project": {
                "_id": 0,
                "metadata": 1,
                "timestamp": 1,
                "data": 1,
            },
        }
    ]
    next_time_span = datetime.datetime.now()

    db = get_db_data(websocket)
    found_agent = False
    for server in user.servers:
        if server.collection_id == agent_id:
            agent_uuid = None
            try:
                agent_uuid = UUID(agent_id)
            except ValueError:
                await websocket.send_json({"error": "invalid_agent_id"})
                return
            cursor = db[agent_uuid.hex].aggregate(pipeline)

            content = "{\"data\": ["
            for doc in await cursor.to_list(length=100):
                content += AgentTSObjetc.parse_obj(doc).json() + ","
            if content[-1] == ",":
                content = content[:-1]
            content += f"], \"next_time_start\": \"{next_time_span.isoformat()}\"" + "}"
            await websocket.send({"type": "websocket.send", "text": content})
            found_agent = True

    if not found_agent:
        await websocket.send_json({"error": "agent_not_found"})


@router.websocket("/")
async def ws(websocket: WebSocket, user: User = Depends(user_scheme_websocket)):
    await websocket.accept()

    while True:
        # Get message and check if it matches a function
        try:
            msg = await websocket.receive_json()
            match msg.get("type"):
                case "get_container_data":
                    await get_container_data(websocket, user,
                                             GetContainerDataMessage(**msg))
                case "get_agent_summary":
                    await get_agent_summary(websocket, user,
                                            GetAgentSummaryMessage(**msg))
                case _:
                    await websocket.send_json({"error": "invalid_message_type"})
        except JSONDecodeError:
            await websocket.send_json({"error": "invalid_json"})
