import uuid

from ai.agent_manager import RuntimeAgentManager
from ai.agent_manager_interface import IAgentManager
from ai.tracing import Tracer
from chat.tables import ChatTable
from chat.schemas import Chat
from auth.tables import UserTable
from auth.auth import get_user_by_username
from ai.agent_manager_store import AgentMangerInMemoryStore

from sqlalchemy.orm import Session

from collections import defaultdict

def chat_schema_from_db(chat: ChatTable) -> Chat:
    return Chat(
        chat_id=chat.id,
        name=chat.name,
    )


def chat_belongs_to_user(chat: ChatTable, user: UserTable) -> bool:
    return chat.user.username == user.username


def get_chat_by_id_from_user(db: Session, user: UserTable, chat_id: uuid.UUID) -> ChatTable | None:
    chat = db.get(ChatTable, chat_id)

    # A user should not be able to view other user's chats.
    if not chat_belongs_to_user(chat, user):
        return None

    return chat


def get_chat_by_id_from_user_throwing(db: Session, user: UserTable, chat_id: uuid.UUID) -> ChatTable:
    chat = get_chat_by_id_from_user(db, user, chat_id)
    if chat is None:
        raise ValueError("invalid chat ID")
    
    return chat


def _create_agent_manager_from_chat(db: Session, chat: ChatTable) -> IAgentManager:
    return RuntimeAgentManager(
        db=db,
        chat_id=chat.id,
        owner_username=chat.user.username,
        # TODO: this should be obtained from the DB and loaded as a defaultdict (backrefereced with the chat table)
        chat_summaries=defaultdict(lambda: "This is a new chat. No summary available.", {}), 
        # TODO: this history should be obtained from the DB (backreferenced with the chat table)
        tracer=Tracer(history=[]), 
    )


def initialize_new_chat_for_user(db: Session,  manager_store: AgentMangerInMemoryStore, chat_name: str, username: str) -> ChatTable:
    user = get_user_by_username(db, username)
    assert user

    new_chat = ChatTable(
        name=chat_name,
        user_id=user.id,
    )
    db.add(new_chat)
    # This flushes the DB to generate the new chat's ID for use below.
    db.commit()

    # Initalize a runtime agent manager for the chat.
    manager = _create_agent_manager_from_chat(db, new_chat)
    manager_store.register_manager_for_chat(manager)

    return new_chat


def get_or_init_agent_manager_for_chat(db: Session, manager_store: AgentMangerInMemoryStore, owner: UserTable, chat: ChatTable) -> IAgentManager:
    manager = manager_store.get_manager_for_chat(chat.id)

    if manager is None:
        chat = get_chat_by_id_from_user(db, owner, chat.id)
        assert chat
        manager = _create_agent_manager_from_chat(db, chat)

    return manager


def _reset_agent_manager_for_chat(db: Session, manager_store: AgentMangerInMemoryStore, owner: UserTable, chat_id: uuid.UUID):
    chat = get_chat_by_id_from_user(db, owner, chat_id)
    assert chat
    new_manager = _create_agent_manager_from_chat(db, chat)
    manager_store.register_manager_for_chat(new_manager)

    print(f"LOG: resetted agent manager for chat '{chat.id}'")


def reset_all_agent_managers_for_user(db: Session, manager_store: AgentMangerInMemoryStore, user: UserTable):
    for chat in user.chats:
        _reset_agent_manager_for_chat(db, manager_store, user, chat.id)


def delete_chat(db: Session, manager_store: AgentMangerInMemoryStore, owner: UserTable, chat: ChatTable) -> bool:
    # A user should not be able to delete other user's chats.
    if not chat_belongs_to_user(chat, owner):
        return False

    db.delete(chat)
    db.commit()
    manager_store.delete_entry_with_chat_id(chat.id)
    return True

