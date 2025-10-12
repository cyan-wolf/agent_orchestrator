from typing import Annotated, Sequence
import uuid
from fastapi import Depends, Query
from fastapi.routing import APIRouter

from ai.tracing.schemas import Trace, TraceKind
from ai.agent_manager.agent_manager_store import AgentMangerInMemoryStore, get_manager_in_mem_store
from auth.tables import UserTable
from auth.auth import get_current_user
from chat.schemas import ChatModification, CreateNewChat, Chat, UserTextRequest
from chat import services

from sqlalchemy.orm import Session
from database.database import get_database

router = APIRouter()

@router.get("/api/chat/get-all-chats/", tags=["chat"])
async def get_all_chats(
    current_user: Annotated[UserTable, Depends(get_current_user)],
) -> Sequence[Chat]:
    return services.get_all_user_chat_schemas(current_user)


@router.get("/api/chat/{chat_id}/info/", tags=["chat"])
async def get_chat_info(
    chat_id: uuid.UUID, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
):
    return services.get_chat_info(db, current_user, chat_id)


@router.post("/api/chat/create/", tags=["chat"])
async def create_new_chat(
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
    new_chat_req_body: CreateNewChat,
) -> Chat:
    return services.create_and_return_new_chat_for_user(db, manager_store, new_chat_req_body, current_user)


@router.post("/api/chat/{chat_id}/delete/", tags=["chat"])
async def delete_chat_with_id(
    chat_id: uuid.UUID, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
):
    could_delete = services.try_delete_chat_for_user(db, manager_store, chat_id, current_user)

    if could_delete:
        return { "response": f"deleted chat {chat_id}" }
    
    else:
        return { "response": "could not delete chat" }


@router.patch("/api/chat/{chat_id}/modify/", tags=["chat"])
async def modify_chat(
    chat_id: uuid.UUID,
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    chat_modification: ChatModification,
):
    could_modify = services.try_modify_chat(db, chat_id, current_user, chat_modification)

    if could_modify:
        return { "response": f"modified chat {chat_id}" }
    
    else:
        return { "response": "could not modify chat" }


@router.get("/api/chat/{chat_id}/history/", tags=["chat"])
async def get_history(
    chat_id: uuid.UUID, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
 ) -> Sequence[Trace]:
    return services.get_full_trace_schema_history_for_user_chat(db, manager_store, chat_id, current_user)
    

@router.get("/api/chat/{chat_id}/get-latest-messages/{latest_timestamp}/", tags=["chat"])
async def get_latest_messages(
    chat_id: uuid.UUID, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
    latest_timestamp: float, 
    exclude_filters: list[TraceKind] | None = Query(None),
) -> Sequence[Trace]:
    return services.get_trace_schemas_after_timestamp_for_user_chat(
        db, 
        manager_store, 
        chat_id, 
        current_user, 
        latest_timestamp,
        exclude_filters or [],  # pass an empty list if no queries were provided
    )


@router.post("/api/chat/{chat_id}/send-message/", tags=["chat"])
async def recieve_user_input(
    chat_id: uuid.UUID, 
    user_req: UserTextRequest, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    manager_store: Annotated[AgentMangerInMemoryStore, Depends(get_manager_in_mem_store)],
):
    services.invoke_agent_manager_for_chat_with_text(db, manager_store, chat_id, current_user, user_req)
    return { "result": "finished processing" }