from typing import Annotated, Sequence
from fastapi import APIRouter, Depends

from ai.agent.schemas import AgentTemplateSchema, ToolSchema
from ai.agent.agent_templates import get_all_agent_template_schemas, get_all_tool_schemas
from sqlalchemy.orm import Session
from database.database import get_database

router = APIRouter()

@router.get("/api/agent-templates/all/", tags=["agent-templates"])
def view_all_agent_templates(
    db: Annotated[Session, Depends(get_database)],
) -> Sequence[AgentTemplateSchema]:
    # TEMP: default data seeding
    from ai.agent.db_seeding.seed_agent_templates import seed_agent_templates
    seed_agent_templates(db)

    return get_all_agent_template_schemas(db)


@router.get("/api/agent-templates/tools/all/", tags=["agent-templates"])
def view_all_tools(
    db: Annotated[Session, Depends(get_database)],
) -> Sequence[ToolSchema]:
    return get_all_tool_schemas(db)