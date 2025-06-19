from fastapi import FastAPI
from pydantic import BaseModel

from agents import AgentManager, get_latest_agent_msg

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class UserRequest(BaseModel):
    user_message: str

AGENT_MANAGER = AgentManager()

@app.post("/")
async def recieve_user_input(user_req: UserRequest):
    resp = AGENT_MANAGER.invoke_main_with_text(user_req.user_message)
    return {"message": resp}