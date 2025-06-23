from fastapi import FastAPI
from pydantic import BaseModel
import json

from ai.agents import AgentManager

app = FastAPI()

AGENT_MANAGER = AgentManager()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class UserRequest(BaseModel):
    user_message: str

@app.get("/history")
async def get_history() -> str:
    hist = [t.as_json() for t in AGENT_MANAGER.tracer.get_history()]
    return json.dumps(hist)


@app.post("/")
async def recieve_user_input(user_req: UserRequest):
    resp = AGENT_MANAGER.invoke_main_with_text(user_req.user_message)
    return {"message": resp}