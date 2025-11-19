from typing import Annotated, Sequence
from fastapi import APIRouter, Depends

from ai.agent.templates.schemas import AgentTemplateSchema, ToolSchema, CreateCustomAgentSchema, ModifyCustomAgentSchema
from ai.agent.templates.agent_templates import get_all_agent_template_schemas_for_user, get_all_tool_schemas, try_create_custom_agent_for_user, try_modify_custom_agent_for_user, try_delete_custom_agent_for_user
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from auth.tables import UserTable
from database.database import get_database

import uuid

router = APIRouter()

@router.get("/api/agent-templates/all/", tags=["agent-templates"])
def view_all_agent_templates(
    db: Annotated[Session, Depends(get_database)],
    current_user: Annotated[UserTable, Depends(get_current_user)],
) -> Sequence[AgentTemplateSchema]:
    """
    Returns the agent templates accessible to the user.
    """
    # TEMP: default data seeding
    from ai.agent.db_seeding.seed_agent_templates import seed_agent_templates
    seed_agent_templates(db)

    return get_all_agent_template_schemas_for_user(db, current_user)


@router.post("/api/agent-templates/custom/create/", tags=["agent-templates"])
def create_custom_agent_template(
    db: Annotated[Session, Depends(get_database)],
    current_user: Annotated[UserTable, Depends(get_current_user)],
    create_agent_template_schema: CreateCustomAgentSchema,
):
    """
    Tries to create a new custom agent template for the user.
    """
    try_create_custom_agent_for_user(db, current_user, create_agent_template_schema)
    return { "message": "Successfully created custom agent" }


@router.post("/api/agent-templates/custom/modify/", tags=["agent-templates"])
def modify_custom_agent_template(
    db: Annotated[Session, Depends(get_database)],
    current_user: Annotated[UserTable, Depends(get_current_user)],
    modify_agent_template_schema: ModifyCustomAgentSchema,
):
    """
    Tries to modify the given custom agent template.
    """
    try_modify_custom_agent_for_user(db, current_user, modify_agent_template_schema)
    return { "message": "Successfully modified custom agent" }


@router.delete("/api/agent-templates/custom/{agent_template_id}/", tags=["agent-templates"])
def delete_custom_agent_template(
    db: Annotated[Session, Depends(get_database)],
    current_user: Annotated[UserTable, Depends(get_current_user)],
    agent_template_id: uuid.UUID,
):
    """
    Tries to delete the custom agent template with the given ID for the given user.
    """
    try_delete_custom_agent_for_user(db, current_user, agent_template_id)
    return { "message": "Successfully deleted custom agent" }


@router.get("/api/agent-templates/tools/all/", tags=["agent-templates"])
def view_all_tools(
    db: Annotated[Session, Depends(get_database)],
) -> Sequence[ToolSchema]:
    """
    Returns all the tools in the system.
    """
    return get_all_tool_schemas(db)