import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from typing import List
from enum import Enum


class ContainerState(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class AgentMetaData(BaseModel):
    # server_id: str
    container_id: str
    container_name: str
    container_image: str
    container_state: str = "unknown"


class AgentData(BaseModel):
    cpu: float
    memory_perc: float
    memory_tot: int
    total_rx: int
    total_tx: int
    io_read: int
    io_write: int
    healthcheck: Optional[bool] = None


class AgentTSObjetc(BaseModel):
    metadata: AgentMetaData
    timestamp: datetime
    data: AgentData


class AgentTSObjectList(BaseModel):
    data: List[AgentTSObjetc]


class AgentContainerConfig(BaseModel):
    # container: uuid.UUID
    container_id: str
    update_frequency: int
    # If !None pipe the healthcheck to the container
    healthcheck: Optional[str] = None


class AgentConfig(BaseModel):
    _id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="id")
    alias: str
    collection_id: str
    api_key: str
    update_frequency: int
    containers: List[AgentContainerConfig]


# class ContainerCollectionView(BaseModel):

# db
# -----collection(Finns ServerID)
# --------- document(ServiceTSObject<container<1>)
# ----------------CPU: 10%
# ----------------MEM: 12%
# ----------------I/O: 800mb
# ----------------HS:  True

# --------- document(ServiceTSObject<container<2>)
# --------- document(ServiceTSObject<container<3>)
# --------- document(ServiceTSObject<container<4>)

# ----------document(ServiceTSObject<container<1>)
# ----------document(ServiceTSObject<container<2>)
# ----------document(ServiceTSObject<container<3>)
# ----------document(ServiceTSObject<container<4>)

# ----------document(ServiceTSObject<container<1>)
# ----------document(ServiceTSObject<container<2>)
# ----------document(ServiceTSObject<container<3>)
# ----------document(ServiceTSObject<container<4>)

# ----------document(ServiceTSObject<container<1>)
# ----------document(ServiceTSObject<container<2>)
# ----------document(ServiceTSObject<container<3>)
# ----------document(ServiceTSObject<container<4>)
