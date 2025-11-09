from typing import Annotated, Sequence
from fastapi import APIRouter, Depends

from ai.agent.schemas import AgentTemplateSchema, ToolSchema, CreateCustomAgentSchema, ModifyCustomAgentSchema
from ai.agent.agent_templates import get_all_agent_template_schemas_for_user, get_all_tool_schemas, try_create_custom_agent_for_user, try_modify_custom_agent_for_user
from sqlalchemy.orm import Session
from auth.auth import get_current_user
from auth.tables import UserTable
from database.database import get_database

router = APIRouter()

@router.get("/api/agent-templates/all/", tags=["agent-templates"])
def view_all_agent_templates(
    db: Annotated[Session, Depends(get_database)],
    current_user: Annotated[UserTable, Depends(get_current_user)],
) -> Sequence[AgentTemplateSchema]:
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
    try_create_custom_agent_for_user(db, current_user, create_agent_template_schema)
    return { "message": "Successfully created custom agent" }


@router.post("/api/agent-templates/custom/modify/", tags=["agent-templates"])
def modify_custom_agent_template(
    db: Annotated[Session, Depends(get_database)],
    current_user: Annotated[UserTable, Depends(get_current_user)],
    modify_agent_template_schema: ModifyCustomAgentSchema,
):
    try_modify_custom_agent_for_user(db, current_user, modify_agent_template_schema)
    return { "message": "Successfully modified custom agent" }


@router.get("/api/agent-templates/tools/all/", tags=["agent-templates"])
def view_all_tools(
    db: Annotated[Session, Depends(get_database)],
) -> Sequence[ToolSchema]:
    return get_all_tool_schemas(db)