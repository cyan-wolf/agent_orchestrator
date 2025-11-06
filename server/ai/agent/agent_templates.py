from typing import Sequence
from ai.agent.schemas import AgentTemplateSchema, ToolSchema
from ai.agent.tables import AgentTemplateTable, ToolTable
from sqlalchemy.orm import Session

def tool_schema_from_db(tool_in_db: ToolTable) -> ToolSchema:
    return ToolSchema(
        id=tool_in_db.id,
        name=tool_in_db.name,
        description=tool_in_db.description,
    )


def agent_template_schema_from_db(template_in_db: AgentTemplateTable) -> AgentTemplateSchema:
    return AgentTemplateSchema(
        id=template_in_db.id,
        name=template_in_db.name,
        persona=template_in_db.persona,
        purpose=template_in_db.purpose,
        is_switchable_into=template_in_db.is_switchable_into,
        tools=[tool_schema_from_db(t) for t in template_in_db.tools]
    )


def get_all_agent_template_schemas(db: Session) -> Sequence[AgentTemplateSchema]:
    return [agent_template_schema_from_db(template) for template in db.query(AgentTemplateTable).all()]


def get_all_switchable_agent_names(db: Session) -> Sequence[str]:
    return [template.name for template in db.query(AgentTemplateTable).filter(AgentTemplateTable.is_switchable_into == True)]


def get_all_tool_schemas(db: Session) -> Sequence[ToolSchema]:
    return [tool_schema_from_db(t) for t in db.query(ToolTable).all()]