import uuid
from fastapi import HTTPException
from ai.agent_manager.runtime_agent_manager import RuntimeAgentManager
from ai.agent_manager.agent_manager_interface import IAgentManager
from ai.tracing.trace_decorator import Tracer
from chat.tables import ChatTable
from chat.chat_summaries.tables import ChatSummaryTable
from chat.schemas import Chat
from auth.tables import UserTable
from auth.auth import get_user_by_username
from ai.agent_manager.agent_manager_store import AgentMangerInMemoryStore
from sqlalchemy.orm import Session
from collections import defaultdict

from chat.agent_factory_for_chat import agent_factory_for_chat

def chat_schema_from_db(chat: ChatTable) -> Chat:
    return Chat(
        id=chat.id,
        name=chat.name,
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
    _create_and_register_agent_manager_for_chat(db, new_chat, manager_store)

    return new_chat


def _create_and_register_agent_manager_for_chat(db: Session, chat: ChatTable, manager_store: AgentMangerInMemoryStore) -> IAgentManager:
    """
    Automatically creates and registers an Agent Manager for the given chat. Returns the registered manager.
    """

    manager = _create_agent_manager_from_chat(db, chat)
    manager_store.register_manager_for_chat(manager)
    return manager


def _create_agent_manager_from_chat(db: Session, chat: ChatTable) -> IAgentManager:
    """
    WARNING: This method creates a manager, but doesn't register it to the chat.
    Please call the `create_and_register_manager_for_chat` instead.
    """
    
    print(f"LOG: new AM for chat {chat.id}")

    am = RuntimeAgentManager(
        chat=chat,
        chat_summaries=_load_chat_summaries_as_default_dict(chat.summaries), 
        tracer=Tracer(chat.id), 
    )

    agents = agent_factory_for_chat(am.to_ctx(db), chat.user)
    am.initialize_agents(agents)

    return am


def _load_chat_summaries_as_default_dict(summaries: list[ChatSummaryTable]) -> defaultdict[str, str]:
    dict_ = defaultdict(lambda: "This is a new chat. No summary available.", {})
    
    for summary in summaries:
        dict_[summary.agent_name] = summary.content

    return dict_


def get_chat_by_id_from_user_throwing(db: Session, user: UserTable, chat_id: uuid.UUID) -> ChatTable:
    chat = _get_chat_by_id_from_user(db, user, chat_id)
    if chat is None:
        raise HTTPException(status_code=400, detail=f"Invalid chat ID '{chat_id}'")
    
    return chat


def _get_chat_by_id_from_user(db: Session, user: UserTable, chat_id: uuid.UUID) -> ChatTable | None:
    chat = db.get(ChatTable, chat_id)
    if chat is None:
        return None

    # A user should not be able to view other user's chats.
    if not _chat_belongs_to_user(chat, user):
        return None

    return chat


def _chat_belongs_to_user(chat: ChatTable, user: UserTable) -> bool:
    return chat.user.username == user.username


def get_or_init_agent_manager_for_chat(db: Session, manager_store: AgentMangerInMemoryStore, owner: UserTable, chat: ChatTable) -> IAgentManager:
    manager = manager_store.get_manager_for_chat(chat.id)

    if manager is None:
        chat = _get_chat_by_id_from_user(db, owner, chat.id)
        assert chat
        manager = _create_and_register_agent_manager_for_chat(db, chat, manager_store)

    return manager


def reset_all_agent_managers_for_user(db: Session, manager_store: AgentMangerInMemoryStore, user: UserTable):
    for chat in user.chats:
        _reset_agent_manager_for_chat(db, manager_store, user, chat.id)


def _reset_agent_manager_for_chat(db: Session, manager_store: AgentMangerInMemoryStore, owner: UserTable, chat_id: uuid.UUID):
    chat = _get_chat_by_id_from_user(db, owner, chat_id)
    assert chat
    # Replace the existing manager by just creating and registering a new one.
    _create_and_register_agent_manager_for_chat(db, chat, manager_store)

    print(f"LOG: agent manager for chat '{chat.id}' was reset")


def delete_chat(db: Session, manager_store: AgentMangerInMemoryStore, owner: UserTable, chat: ChatTable) -> bool:
    # A user should not be able to delete other user's chats.
    if not _chat_belongs_to_user(chat, owner):
        return False

    db.delete(chat)
    db.commit()
    manager_store.delete_entry_with_chat_id(chat.id)
    return True
