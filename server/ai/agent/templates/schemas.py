from pydantic import BaseModel, field_validator
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

    @field_validator('name')
    def validate_name(cls, value: str) -> str:
        if len(value.strip()) == 0:
            raise ValueError("name cannot be empty")
        return value
    
    @field_validator('persona')
    def validate_persona(cls, value: str) -> str:
        if len(value.strip()) == 0:
            raise ValueError("persona cannot be empty")
        return value
    
    @field_validator('purpose')
    def validate_purpose(cls, value: str) -> str:
        if len(value.strip()) == 0:
            raise ValueError("purpose cannot be empty")
        return value


class CreateCustomAgentSchema(BaseAgentTemplateSchema): pass


class ModifyCustomAgentSchema(BaseAgentTemplateSchema):
    id: uuid.UUID