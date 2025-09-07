from typing import Annotated, Sequence
from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from ai.models import Trace
from auth.tables import UserTable
from auth.auth import get_current_user
from chat.chat import Chat, delete_chat, get_agent_manager_for_chat, get_chat_by_id, get_user_chat_list, initialize_new_chat
from chat.models import CreateNewChat
from db.placeholder_db import TempDB, get_temp_db

from sqlalchemy.orm import Session
from database.database import get_database

router = APIRouter()

@router.get("/api/chat/get-all-chats/", tags=["chat"])
async def get_all_chats(
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[TempDB, Depends(get_temp_db)],
) -> Sequence[Chat]:
    username = current_user.username
    return get_user_chat_list(username, db)


@router.post("/api/chat/create/", tags=["chat"])
async def create_new_chat(
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    temp_db: Annotated[TempDB, Depends(get_temp_db)],
    new_chat_req_body: CreateNewChat,
) -> Chat:
    username = current_user.username

    new_chat = initialize_new_chat(username, db, temp_db, new_chat_req_body.name)
    return new_chat


@router.post("/api/chat/{chat_id}/delete/", tags=["chat"])
async def delete_chat_with_id(
    chat_id: str, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[TempDB, Depends(get_temp_db)],
):
    could_delete = delete_chat(current_user.username, chat_id, db)

    if could_delete:
        return { "response": f"deleted chat {chat_id}" }
    
    else:
        return { "response": "could not delete chat" }


@router.get("/api/chat/{chat_id}/history/", tags=["chat"])
async def get_history(
    chat_id: str, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    temp_db: Annotated[TempDB, Depends(get_temp_db)],
 ) -> Sequence[Trace]:
    
    chat = get_chat_by_id(current_user.username, chat_id, temp_db)
    if chat is None:
        raise Exception("invalid chat ID")

    agent_manager = get_agent_manager_for_chat(chat, db, temp_db, current_user.username)
    hist = agent_manager.get_tracer().get_history()

    return hist


@router.get("/api/chat/{chat_id}/get-latest-messages/{latest_timestamp}/", tags=["chat"])
async def get_latest_messages(
    chat_id: str, 
    latest_timestamp: float, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_database)],
    temp_db: Annotated[TempDB, Depends(get_temp_db)],
) -> Sequence[Trace]:
    
    chat = get_chat_by_id(current_user.username, chat_id, temp_db)
    if chat is None:
        raise Exception("invalid chat ID")

    agent_manager = get_agent_manager_for_chat(chat, db, temp_db, current_user.username)
    hist = agent_manager.get_tracer().get_history()

    return [t for t in hist if t.timestamp > latest_timestamp]


class UserRequest(BaseModel):
    user_message: str

@router.post("/api/chat/{chat_id}/send-message/", tags=["chat"])
async def recieve_user_input(
    chat_id: str, 
    user_req: UserRequest, 
    current_user: Annotated[UserTable, Depends(get_current_user)],
    temp_db: Annotated[TempDB, Depends(get_temp_db)],
    db: Annotated[Session, Depends(get_database)],
):
    chat = get_chat_by_id(current_user.username, chat_id, temp_db)
    if chat is None:
        raise Exception("invalid chat ID")

    agent_manager = get_agent_manager_for_chat(chat, db, temp_db, current_user.username)

    _ = agent_manager.invoke_main_agent_with_text(current_user.username, user_req.user_message, db)

    # Store the chat history by serializing the agent manager.
    # This is for the placeholder storing functionality.

    # IGNORE TYPING SINCE THIS IS A TEMPORARY HACK.
    # Just assume that the context *IS* an agent manager.
    chat.agent_manager_serialization = agent_manager.to_serialized() # type: ignore

    # Store the chat DB on disk everytime a message is sent (placeholder).
    temp_db.store_chat_db()
    
    return { "result": "finished processing" }