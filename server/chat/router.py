import base64
from typing import Annotated, Sequence
import uuid
from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from ai.agent_manager import AgentManager
from ai.tracing import Trace
from auth.auth import User, get_current_user
from chat.chat import Chat, delete_chat, get_agent_manager_for_chat, get_chat_by_id, get_user_chat_list, initialize_chat

router = APIRouter()

@router.get("/api/chat/get-all-chats/", tags=["chat"])
async def get_all_chats(current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Chat]:
    username = current_user.username
    return get_user_chat_list(username)


@router.post("/api/chat/create/", tags=["chat"])
async def create_new_chat(current_user: Annotated[User, Depends(get_current_user)]) -> Chat:
    username = current_user.username

    new_chat = initialize_chat(username)
    return new_chat


@router.post("/api/chat/{chat_id}/delete/", tags=["chat"])
async def delete_chat_with_id(chat_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    could_delete = delete_chat(current_user.username, chat_id)

    if could_delete:
        return { "response": f"deleted chat {chat_id}" }
    
    else:
        return { "response": "could not delete chat" }


@router.get("/api/chat/{chat_id}/history/", tags=["chat"])
async def get_history(chat_id: str, current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Trace]:
    if get_chat_by_id(current_user.username, chat_id) is None:
        raise Exception("invalid chat ID")

    agent_manager = get_agent_manager_for_chat(chat_id)
    return agent_manager.tracer.get_history()


@router.get("/api/chat/{chat_id}/get-latest-messages/{latest_timestamp}/", tags=["chat"])
async def get_latest_messages(chat_id: str, latest_timestamp: float, current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Trace]:
    if get_chat_by_id(current_user.username, chat_id) is None:
        raise Exception("invalid chat ID")

    agent_manager = get_agent_manager_for_chat(chat_id)
    hist = agent_manager.tracer.get_history()

    return [t for t in hist if t.timestamp > latest_timestamp]


class UserRequest(BaseModel):
    user_message: str

@router.post("/api/chat/{chat_id}/send-message/", tags=["chat"])
async def recieve_user_input(chat_id: str, user_req: UserRequest, current_user: Annotated[User, Depends(get_current_user)]):
    if get_chat_by_id(current_user.username, chat_id) is None:
        raise Exception("invalid chat ID")

    agent_manager = get_agent_manager_for_chat(chat_id)

    _ = agent_manager.invoke_main_with_text(current_user.username, user_req.user_message)
    
    return { "result": "finished processing" }