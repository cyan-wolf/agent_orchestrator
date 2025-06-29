from fastapi import FastAPI
from pydantic import BaseModel
from typing import Sequence

from ai.tracing import *
from ai.agents import AgentManager

app = FastAPI()

AGENT_MANAGER = AgentManager()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class UserRequest(BaseModel):
    user_message: str

@app.get("/api/history")
async def get_history() -> Sequence[Trace]:
    return AGENT_MANAGER.tracer.get_history()


@app.get("/api/get-latest-messages/{latest_timestamp}")
async def get_latest_messages(latest_timestamp: float) -> Sequence[Trace]:
    hist = AGENT_MANAGER.tracer.get_history()
    return [t for t in hist if t.timestamp > latest_timestamp]


@app.post("/api/send-message")
async def recieve_user_input(user_req: UserRequest):
    _resp = AGENT_MANAGER.invoke_main_with_text(user_req.user_message)
    return { "result": "finished processing" }