from typing import Sequence

from sqlalchemy import or_
from ai.agent.schemas import AgentTemplateSchema, CreateCustomAgentSchema, ToolSchema
from ai.agent.tables import AgentTemplateTable, ToolTable
from sqlalchemy.orm import Session
from fastapi import HTTPException

from auth.tables import UserTable

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
        is_global=template_in_db.user_id is None, # a template is global if it has no associated user
        tools=[tool_schema_from_db(t) for t in template_in_db.tools]
    )


def get_all_agent_template_schemas_for_user(db: Session, user: UserTable) -> Sequence[AgentTemplateSchema]:
    # This query shows both global (`user_id ==  None`) and custom (`user_id == user.id`) templates
    templates = db.query(AgentTemplateTable)\
        .filter(or_(AgentTemplateTable.user_id.is_(None), AgentTemplateTable.user_id == user.id))\
        .all()

    return [agent_template_schema_from_db(template) for template in templates]


def try_create_custom_agent_for_user(
    db: Session,
    current_user: UserTable,
    create_agent_template_schema: CreateCustomAgentSchema,
):
    # If any of the user's agent templates already has the same name as the new agent schema, then throw.
    if any(
        create_agent_template_schema.name == template.name 
        for template in get_all_agent_template_schemas_for_user(db, current_user)
    ):
        raise HTTPException(status_code=400, detail=f"agent template with name '{create_agent_template_schema.name}' already exists")

    new_agent_template = AgentTemplateTable(
        name=create_agent_template_schema.name,
        persona=create_agent_template_schema.persona,
        purpose=create_agent_template_schema.purpose,
        is_switchable_into=create_agent_template_schema.is_switchable_into,

        user_id=current_user.id,
    )

    db.add(new_agent_template)
    db.commit()


def get_all_switchable_agent_names(db: Session, owner: UserTable) -> Sequence[str]:
    templates = db.query(AgentTemplateTable)\
        .filter(
            AgentTemplateTable.is_switchable_into == True, 
            or_(AgentTemplateTable.user_id.is_(None), AgentTemplateTable.user_id == owner.id)
        )\
        .all()

    return [template.name for template in templates]


def get_all_tool_schemas(db: Session) -> Sequence[ToolSchema]:
    return [tool_schema_from_db(t) for t in db.query(ToolTable).all()]