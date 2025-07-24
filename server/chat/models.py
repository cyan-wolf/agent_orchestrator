from pydantic import BaseModel
from ai.models import SerializedAgentManager


class CreateNewChat(BaseModel):
    name: str    


class Chat(BaseModel):
    chat_id: str
    name: str


class ChatInDB(Chat):
    agent_manager_serialization: SerializedAgentManager | None = None