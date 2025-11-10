from typing import Sequence

from sqlalchemy import or_
from ai.agent.schemas import AgentTemplateSchema, CreateCustomAgentSchema, ModifyCustomAgentSchema, ToolSchema
from ai.agent.tables import AgentTemplateTable, ToolTable
from sqlalchemy.orm import Session
from fastapi import HTTPException

from auth.tables import UserTable

import uuid

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


def get_agent_template_by_name_for_user(db: Session, user: UserTable, agent_name: str) -> AgentTemplateTable | None:
    return db.query(AgentTemplateTable)\
        .filter(
            or_(AgentTemplateTable.user_id.is_(None), AgentTemplateTable.user_id == user.id),
            AgentTemplateTable.name == agent_name,
        )\
        .first()


def tool_id_list_to_tool_objs(db: Session, tool_ids: list[str]):
    for tool_id in tool_ids:
        tool = get_tool_by_id(db, tool_id)

        if tool is not None:
            yield tool

        else:
            raise HTTPException(
                status_code=400, 
                detail=f"tool '{tool_id}' was not found in database",
            )


def try_create_custom_agent_for_user(
    db: Session,
    current_user: UserTable,
    create_agent_template_schema: CreateCustomAgentSchema,
):
    # If any of the user's agent templates already has the same name as the new agent schema, then throw.
    if get_agent_template_by_name_for_user(db, current_user, create_agent_template_schema.name) is not None:
        raise HTTPException(status_code=400, detail=f"agent template with name '{create_agent_template_schema.name}' already exists")

    new_agent_template = AgentTemplateTable(
        name=create_agent_template_schema.name,
        persona=create_agent_template_schema.persona,
        purpose=create_agent_template_schema.purpose,
        is_switchable_into=create_agent_template_schema.is_switchable_into,

        user_id=current_user.id,
    )

    db.add(new_agent_template)
    db.flush()

    new_agent_template.tools = list(tool_id_list_to_tool_objs(db, create_agent_template_schema.tool_id_list))

    db.commit()


def try_modify_custom_agent_for_user(
    db: Session,
    current_user: UserTable,
    modify_agent_template_schema: ModifyCustomAgentSchema,
):
    agent_template_from_db = db.query(AgentTemplateTable)\
        .filter(
            AgentTemplateTable.user_id.is_not(None),                    # the template is not global
            AgentTemplateTable.user_id == current_user.id,              # the template belongs to the current user
            AgentTemplateTable.id == modify_agent_template_schema.id,   # template ID matches requested ID
        )\
        .first()
    
    if agent_template_from_db is None:
        raise HTTPException(
            status_code=400, 
            detail=f"agent template with ID `{modify_agent_template_schema.id}` could not be modified",
        )
    
    # Check that the user is not trying to rename an agent to a name that already belongs to another 
    # agent accessible to the user.
    existing_agent_with_name = get_agent_template_by_name_for_user(db, current_user, modify_agent_template_schema.name) 
    if existing_agent_with_name is not None and existing_agent_with_name.id != modify_agent_template_schema.id:
        raise HTTPException(
            status_code=400,
            detail=f"agent template with name '{modify_agent_template_schema.name}' already exists",
        )

    agent_template_from_db.name = modify_agent_template_schema.name
    agent_template_from_db.persona = modify_agent_template_schema.persona
    agent_template_from_db.purpose = modify_agent_template_schema.purpose
    agent_template_from_db.is_switchable_into = modify_agent_template_schema.is_switchable_into

    agent_template_from_db.tools = list(tool_id_list_to_tool_objs(db, modify_agent_template_schema.tool_id_list))

    db.commit()


def try_delete_custom_agent_for_user(
    db: Session,
    current_user: UserTable,
    agent_template_id: uuid.UUID,
):
    agent_template_from_db = db.query(AgentTemplateTable)\
        .filter(
            AgentTemplateTable.user_id.is_not(None),                    # the template is not global
            AgentTemplateTable.user_id == current_user.id,              # the template belongs to the current user
            AgentTemplateTable.id == agent_template_id,                 # template ID matches requested ID
        )\
        .first()
    
    if agent_template_from_db is None:
        raise HTTPException(
            status_code=400, 
            detail=f"agent template with ID '{agent_template_id}' did not exist",
        )
    
    db.delete(agent_template_from_db)
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


def get_tool_by_id(db: Session, tool_id: str) -> ToolTable | None:
    return db.query(ToolTable).filter(ToolTable.id == tool_id).first()