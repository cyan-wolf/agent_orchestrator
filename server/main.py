from fastapi import Depends, FastAPI
from pydantic import BaseModel
from typing import Annotated, Sequence

from ai.tracing import *
from ai.agent_manager import AgentManager

from auth.auth import User, get_current_user
from auth.router import router as auth_router

app = FastAPI()

app.include_router(auth_router)

FAKE_AGENT_MANAGER_DB: dict[str, AgentManager] = {}

def initialize_agent_manager_for_user(user: User):
    FAKE_AGENT_MANAGER_DB[user.username] = AgentManager()

def get_or_create_agent_manager(user: User) -> AgentManager:
    username = user.username

    if username not in FAKE_AGENT_MANAGER_DB:
        initialize_agent_manager_for_user(user)

    agent_manager = FAKE_AGENT_MANAGER_DB[user.username]
    return agent_manager

@app.get("/")
async def root():
    return {"message": "Hello World"}


class UserRequest(BaseModel):
    user_message: str

@app.get("/api/history/", tags=["chat"])
async def get_history(current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Trace]:
    agent_manager = get_or_create_agent_manager(current_user)
    return agent_manager.tracer.get_history()


@app.get("/api/get-latest-messages/{latest_timestamp}/", tags=["chat"])
async def get_latest_messages(latest_timestamp: float, current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Trace]:
    agent_manager = get_or_create_agent_manager(current_user)

    hist = agent_manager.tracer.get_history()

    return [t for t in hist if t.timestamp > latest_timestamp]


@app.post("/api/send-message/", tags=["chat"])
async def recieve_user_input(user_req: UserRequest, current_user: Annotated[User, Depends(get_current_user)]):
    agent_manager = get_or_create_agent_manager(current_user)

    _ = agent_manager.invoke_main_with_text(current_user.username, user_req.user_message)
    
    return { "result": "finished processing" }