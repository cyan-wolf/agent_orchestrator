import base64
from typing import Sequence
import uuid
from pydantic import BaseModel

from ai.agent_manager import AgentManager
from chat.models import Chat



# username -> list of chats
FAKE_CHAT_DB: dict[str, list[Chat]] = {}

# chat ID -> AgentManager
FAKE_AGENT_MANAGER_DB: dict[str, AgentManager] = {}

def initialize_agent_manager_for_chat(chat_id: str):
    FAKE_AGENT_MANAGER_DB[chat_id] = AgentManager()




def gen_chat_id():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')


def get_user_chat_list(username: str) -> Sequence[Chat]:
    return FAKE_CHAT_DB.setdefault(username, [])


def get_chat_by_id(username: str, chat_id: str) -> Chat | None:
    for chat in FAKE_CHAT_DB.setdefault(username, []):
        if chat_id == chat.chat_id:
            return chat
        
    return None


def initialize_chat(username: str) -> Chat:
    chat_id = gen_chat_id()
    new_chat = Chat(chat_id=chat_id)
    initialize_agent_manager_for_chat(chat_id)

    FAKE_CHAT_DB.setdefault(username, []).append(new_chat)

    return new_chat


def delete_chat(username: str, chat_id: str) -> bool:
    curr_chat = get_chat_by_id(username, chat_id)

    if curr_chat is not None:
        FAKE_CHAT_DB[username].remove(curr_chat)
        del FAKE_AGENT_MANAGER_DB[chat_id]
        return True
    
    return False

def get_agent_manager_for_chat(chat_id: str) -> AgentManager:
    if chat_id in FAKE_AGENT_MANAGER_DB:
        return FAKE_AGENT_MANAGER_DB[chat_id]
    
    else:
        # This should be impossible since every chat has 1 agent manager.
        raise Exception("chat does not have an agent manager")