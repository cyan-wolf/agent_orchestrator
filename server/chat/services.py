from typing import Sequence
import uuid

from ai.tracing.schemas import Trace, TraceKind
from ai.agent_manager.agent_manager_store import AgentMangerInMemoryStore
from auth.tables import UserTable
from chat.chat import *
from chat.schemas import CreateNewChat, Chat, UserTextRequest

from sqlalchemy.orm import Session

def get_all_user_chat_schemas(user: UserTable) -> Sequence[Chat]:
    """
    Get all the chats belonging to the given user as a sequence of :py:class:`chat.schemas.Chat` chat schemas.
    """
    return [chat_schema_from_db(chat) for chat in user.chats]


def create_and_return_new_chat_for_user(db: Session, manager_store: AgentMangerInMemoryStore, new_chat_schema: CreateNewChat, user: UserTable) -> Chat:
    """
    Create a new chat using the provided chat creation data :py:attr:`new_chat_schema`. Returns the schema of the newly created chat.
    """
    new_chat_from_db = initialize_new_chat_for_user(
        db, 
        manager_store, 
        new_chat_schema.name, 
        user.username,
    )
    return chat_schema_from_db(new_chat_from_db)


def try_delete_chat_for_user(db: Session, manager_store: AgentMangerInMemoryStore, chat_id: uuid.UUID, user: UserTable) -> bool:
    """
    Tries deleting the chat with the given ID for the given user. Raises the :py:class:`fastapi.HTTPException` exception if 
    an issue occurs, such as the given ID not existing in the database or the chat not belonging to the given user.
    """
    chat = get_chat_by_id_from_user_throwing(db, user, chat_id)
    could_delete = delete_chat(db, manager_store, user, chat)
    return could_delete


def get_full_trace_schema_history_for_user_chat(
    db: Session, 
    manager_store: AgentMangerInMemoryStore, 
    chat_id: uuid.UUID, 
    user: UserTable
) -> Sequence[Trace]:
    """
    Returns the entire chat history for the given chat for the given user as a sequence of trace schemas. 
    Raises the :py:class:`fastapi.HTTPException` exception if an issue occurs.
    """
    chat = get_chat_by_id_from_user_throwing(db, user, chat_id)

    agent_manager = get_or_init_agent_manager_for_chat(db, manager_store, user, chat)
    return agent_manager.get_tracer().get_history(db)


def get_trace_schemas_after_timestamp_for_user_chat(
    db: Session, 
    manager_store: AgentMangerInMemoryStore, 
    chat_id: uuid.UUID, 
    user: UserTable, 
    timestamp: float,
    exclude_filters: list[TraceKind],
) -> Sequence[Trace]:
    """
    Similar to the :py:func:`chat.services.get_full_trace_schema_history_for_user_chat` service, except that 
    it only returns the traces created after the provided timestamp.
    """
    chat = get_chat_by_id_from_user_throwing(db, user, chat_id)
    
    agent_manager = get_or_init_agent_manager_for_chat(db, manager_store, user, chat)
    return agent_manager.get_tracer().get_traces_after_timestamp(db, timestamp, exclude_filters)


def invoke_agent_manager_for_chat_with_text(
    db: Session, 
    manager_store: AgentMangerInMemoryStore, 
    chat_id: uuid.UUID, 
    current_user: UserTable, 
    user_request: UserTextRequest,
) -> None:
    """
    Invokes the agent manager associated with the chat with the given ID for the given user. Uses the 
    contents of the provided :py:attr:`user_request` to generate traces from the agent manager.
    """
    chat = get_chat_by_id_from_user_throwing(db, current_user, chat_id)
    agent_manager = get_or_init_agent_manager_for_chat(db, manager_store, current_user, chat)
    _ = agent_manager.invoke_main_agent_with_text(current_user.username, user_request.user_message, db)