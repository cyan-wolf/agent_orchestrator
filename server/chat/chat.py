import base64
from typing import Sequence
import uuid
from pydantic import BaseModel

from ai.agent_manager import AgentManager
from chat.models import Chat
from db.models import ChatTempDB


# chat ID -> AgentManager
FAKE_AGENT_MANAGER_DB: dict[str, AgentManager] = {}

def initialize_agent_manager_for_chat(chat_id: str):
    FAKE_AGENT_MANAGER_DB[chat_id] = AgentManager()


def gen_chat_id():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')


def get_user_chat_list(username: str, db: ChatTempDB) -> Sequence[Chat]:
    return db.chats.setdefault(username, [])


def get_chat_by_id(username: str, chat_id: str, db: ChatTempDB) -> Chat | None:
    for chat in db.chats.setdefault(username, []):
        if chat_id == chat.chat_id:
            return chat
        
    return None


def initialize_chat(username: str, db: ChatTempDB) -> Chat:
    chat_id = gen_chat_id()
    new_chat = Chat(chat_id=chat_id)
    initialize_agent_manager_for_chat(chat_id)

    db.chats.setdefault(username, []).append(new_chat)

    return new_chat


def delete_chat(username: str, chat_id: str, db: ChatTempDB) -> bool:
    curr_chat = get_chat_by_id(username, chat_id, db)

    if curr_chat is not None:
        db.chats[username].remove(curr_chat)
        del FAKE_AGENT_MANAGER_DB[chat_id]
        return True
    
    return False

def get_agent_manager_for_chat(chat_id: str) -> AgentManager:
    if chat_id in FAKE_AGENT_MANAGER_DB:
        return FAKE_AGENT_MANAGER_DB[chat_id]
    
    else:
        # This should be impossible since every chat has 1 agent manager.
        raise Exception("chat does not have an agent manager")