
from typing import Sequence
from pydantic import BaseModel

from ai.models import SerializedAgentManager

class Chat(BaseModel):
    chat_id: str


class ChatInDB(Chat):
    agent_manager_serialization: SerializedAgentManager | None = None