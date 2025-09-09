from pydantic import BaseModel
import uuid

class CreateNewChat(BaseModel):
    name: str    


class Chat(BaseModel):
    chat_id: uuid.UUID
    name: str
