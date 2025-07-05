from fastapi import Depends, FastAPI
from pydantic import BaseModel
from typing import Annotated, Sequence

from ai.tracing import *
from ai.agent_manager import AgentManager

from auth.auth import User, get_current_user
from auth.router import router as auth_router

app = FastAPI()

app.include_router(auth_router)

AGENT_MANAGER = AgentManager()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class UserRequest(BaseModel):
    user_message: str

@app.get("/api/history")
async def get_history(_current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Trace]:
    return AGENT_MANAGER.tracer.get_history()


@app.get("/api/get-latest-messages/{latest_timestamp}")
async def get_latest_messages(latest_timestamp: float, _current_user: Annotated[User, Depends(get_current_user)]) -> Sequence[Trace]:
    hist = AGENT_MANAGER.tracer.get_history()
    return [t for t in hist if t.timestamp > latest_timestamp]


@app.post("/api/send-message")
async def recieve_user_input(user_req: UserRequest, current_user: Annotated[User, Depends(get_current_user)]):
    _resp = AGENT_MANAGER.invoke_main_with_text(current_user.username, user_req.user_message)
    return { "result": "finished processing" }