import base64
from typing import Sequence
import uuid

from ai.agent_manager_interface import IAgentManager
from ai.agent_manager import RuntimeAgentManager
from ai.schemas import SerializedAgentManager
from chat.schemas import Chat, ChatInDB
from db.placeholder_db import TempDB

from sqlalchemy.orm import Session


def initialize_runtime_agent_manager_for_new_chat(chat: Chat, db: Session, temp_db: TempDB, username: str):
    # Initialize an empty agent manager, since this is a new chat.
    am = RuntimeAgentManager(serialized_version=SerializedAgentManager(
        history=[],
        chat_summaries={},
    ), 
        chat_id=chat.chat_id,
        owner_username=username,
        db=db,
    )
    
    temp_db.runtime_agent_managers[chat.chat_id] = am
    return am


def gen_chat_id():
    # return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')
    return str(uuid.uuid4())


def get_user_chat_list(username: str, db: TempDB) -> Sequence[Chat]:
    return db.chat_db.chats.setdefault(username, [])


def get_chat_by_id(username: str, chat_id: str, db: TempDB) -> ChatInDB | None:
    for chat in db.chat_db.chats.setdefault(username, []):
        if chat_id == chat.chat_id:
            return chat
        
    return None


def initialize_new_chat(username: str, db: Session, temp_db: TempDB, chat_name: str) -> Chat:
    chat_id = gen_chat_id()
    # Create a new chat.
    new_chat = ChatInDB(chat_id=chat_id, name=chat_name)

    # Initalize a runtime agent manager for the chat.
    am = initialize_runtime_agent_manager_for_new_chat(new_chat, db, temp_db, username)

    # Store the newly created agent manager in the chat.
    new_chat.agent_manager_serialization = am.to_serialized()

    # Add the chat to the database.
    temp_db.chat_db.chats.setdefault(username, []).append(new_chat)

    return new_chat


def delete_chat(username: str, chat_id: str, db: TempDB) -> bool:
    curr_chat = get_chat_by_id(username, chat_id, db)

    if curr_chat is not None:
        db.chat_db.chats[username].remove(curr_chat)
        del db.runtime_agent_managers[chat_id]
        return True
    
    return False

def get_agent_manager_for_chat(chat: ChatInDB, db: Session, temp_db: TempDB, username: str) -> IAgentManager:
    # Existing chat's runtime agent manager has already been initialized.
    if chat.chat_id in temp_db.runtime_agent_managers:
        return temp_db.runtime_agent_managers[chat.chat_id]

    # The runtime agent manager has still not been initalized.
    # Build a runtime agent manager using the serialized data in the chat.
    else:
        assert chat.agent_manager_serialization

        am = RuntimeAgentManager(chat.agent_manager_serialization, chat_id=chat.chat_id, owner_username=username, db=db)
        # Store the retrieved AM in the runtime database so
        # that it isn't re-created after every message.
        temp_db.runtime_agent_managers[chat.chat_id] = am

        return am