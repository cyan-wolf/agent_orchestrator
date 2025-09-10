from typing import Annotated, Sequence
import uuid
from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from ai.tracing.schemas import Trace
from ai.agent_manager.agent_manager_store import AgentMangerInMemoryStore, get_manager_in_mem_store
from auth.tables import UserTable
from auth.auth import get_current_user
from chat.chat import chat_schema_from_db, initialize_new_chat_for_user, delete_chat, get_chat_by_id_from_user_throwing, get_or_init_agent_manager_for_chat
from chat.schemas import CreateNewChat, Chat

from sqlalchemy.orm import Session
from database.database import get_database

router = APIRouter()

@router.get("/api/chat/get-all-chats/", tags=["chat"])
async def get_all_chats(
    current_user: Annotated[UserTable, Depends(get_current_user)],
) -> Sequence[Chat]:
    return [chat_schema_from_db(chat) for chat in current_user.chats]


@router.post("/api/chat/create/", tags=["chat"])
async def create_new_chat(
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
    new_chat_req_body: CreateNewChat,
) -> Chat:
    new_chat_from_db = initialize_new_chat_for_user(
        db, 
        manager_store, 
        new_chat_req_body.name, 
        current_user.username
    )
    return chat_schema_from_db(new_chat_from_db)


@router.post("/api/chat/{chat_id}/delete/", tags=["chat"])
async def delete_chat_with_id(
    chat_id: uuid.UUID, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
):
    chat = get_chat_by_id_from_user_throwing(db, current_user, chat_id)
    could_delete = delete_chat(db, manager_store, current_user, chat)

    if could_delete:
        return { "response": f"deleted chat {chat_id}" }
    
    else:
        return { "response": "could not delete chat" }


@router.get("/api/chat/{chat_id}/history/", tags=["chat"])
async def get_history(
    chat_id: uuid.UUID, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
 ) -> Sequence[Trace]:
    
    chat = get_chat_by_id_from_user_throwing(db, current_user, chat_id)

    agent_manager = get_or_init_agent_manager_for_chat(db, manager_store, current_user, chat)
    hist = agent_manager.get_tracer().get_history()

    return hist


@router.get("/api/chat/{chat_id}/get-latest-messages/{latest_timestamp}/", tags=["chat"])
async def get_latest_messages(
    chat_id: uuid.UUID, 
    latest_timestamp: float, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
) -> Sequence[Trace]:
    
    chat = get_chat_by_id_from_user_throwing(db, current_user, chat_id)
    
    agent_manager = get_or_init_agent_manager_for_chat(db, manager_store, current_user, chat)
    hist = agent_manager.get_tracer().get_history()

    return [t for t in hist if t.timestamp > latest_timestamp]


class UserRequest(BaseModel):
    user_message: str

@router.post("/api/chat/{chat_id}/send-message/", tags=["chat"])
async def recieve_user_input(
    chat_id: uuid.UUID, 
    user_req: UserRequest, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
):
    chat = get_chat_by_id_from_user_throwing(db, current_user, chat_id)

    agent_manager = get_or_init_agent_manager_for_chat(db, manager_store, current_user, chat)

    _ = agent_manager.invoke_main_agent_with_text(current_user.username, user_req.user_message, db)

    # TODO: Store the latest traces from the manager after it has finished processing (OR STORE THEM SOMEWHERE ELSE (?)).
    # ...
    
    return { "result": "finished processing" }