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


class EditUser(BaseModel):
    username: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    surname: Optional[str]
    password: Optional[str]
    confirm_password: Optional[str]
