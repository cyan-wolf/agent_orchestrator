from pydantic import BaseModel
import uuid

class ToolSchema(BaseModel):
    id: str
    name: str
    description: str


class AgentTemplateSchema(BaseModel):
    id: uuid.UUID
    name: str
    persona: str
    purpose: str
    is_switchable_into: bool

    is_global: bool
    
    tools: list[ToolSchema]


class BaseAgentTemplateSchema(BaseModel):
    name: str
    persona: str
    purpose: str
    is_switchable_into: bool

    tool_id_list: list[str]


class CreateCustomAgentSchema(BaseAgentTemplateSchema): pass


class ModifyCustomAgentSchema(BaseAgentTemplateSchema):
    id: uuid.UUID