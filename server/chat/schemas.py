from pydantic import BaseModel
import uuid

class CreateNewChat(BaseModel):
    name: str    


class Chat(BaseModel):
    id: uuid.UUID
    name: str
