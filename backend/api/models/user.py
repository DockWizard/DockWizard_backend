from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from models.agent import AgentConfig


class User(BaseModel):
    _id: uuid.UUID = Field(default_factory=uuid.uuid4, alias="id")
    username: str
    email: str
    first_name: str
    surname: str
    servers: List[AgentConfig] = []  # Config for all servers currently added
    _hashed_password: Optional[str]


class CreateNewAgentConfig(BaseModel):
    alias: str


# Auth
# -----Register                             X
# -----Login                                X
# -----Logout                               X

# User[user_scheme]
# -----Get_user                             X
# -----Change_user

# Agent[<agent_scheme>]
# -----Post_agentTSObjects                  X

# Agent_data[<user_scheme]
# -----Get_agents                           X
# -----Get_agent/<id>/data                  X
# -----Get_agent/<id>/data/<container_id>
# -----Create_new_agent_config              X
# -----Update_agent_config                  X
# -----Delete_agent_config                  X

# Assets
# -----Get_agent                            X
