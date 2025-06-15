from fastapi import FastAPI
from pydantic import BaseModel

import orchestration

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


class UserRequest(BaseModel):
    user_message: str


@app.post("/")
async def recieve_user_input(user_req: UserRequest):
    resp = orchestration.invoke_agent(user_req.user_message)
    return {"message": resp}