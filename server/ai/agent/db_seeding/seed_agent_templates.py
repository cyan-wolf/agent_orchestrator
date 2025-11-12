"""
This module exports a helper function of the same name that seeds the database with default agent templates and tools.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from ai.agent.templates.tables import AgentTemplateTable, ToolTable
from typing import Any
import json
from pathlib import Path
from uuid import UUID

TOOL_SEED_FILE_PATH = Path(__file__).parent / "tool_seeds.json"
AGENT_TEMPLATE_SEED_FILE_PATH = Path(__file__).parent / "agent_template_seeds.json"


def load_tool_seeds() -> list[dict[str, str]]:
    with open(TOOL_SEED_FILE_PATH, 'r') as f:
        return json.load(f)


def load_agent_template_seeds() -> list[dict[str, Any]]:
    with open(AGENT_TEMPLATE_SEED_FILE_PATH, 'r') as f:
        return json.load(f)


def seed_agent_templates(db: Session):
    tool_table_populated = db.scalar(select(ToolTable).limit(1)) is not None

    if tool_table_populated:
        existing_tools = { tool.id: tool for tool in db.scalars(select(ToolTable)) }

    else:
        print("LOG: Seeding default tools")
        existing_tools = {}
        for tool_data in load_tool_seeds():
            tool = ToolTable(**tool_data)
            db.add(tool)
            existing_tools[tool.id] = tool

        # Make sure that the tool PKs are assigned.
        db.flush()

    agent_table_populated = db.scalar(select(AgentTemplateTable).limit(1)) is not None

    if agent_table_populated:
        print("LOG: agent template seeding skipped; agent templates already exist")
        return

    for agent_template_data in load_agent_template_seeds():
        agent_template_data["id"] = UUID(agent_template_data["id"]) # use same GUID

        del agent_template_data["is_global"] # remove `is_global` attribute

        needed_tools: list[dict[str, str]] = agent_template_data.pop("tools")

        agent_template = AgentTemplateTable(**agent_template_data)
        db.add(agent_template)

        for tool in needed_tools:
            tool_in_db = existing_tools.get(tool['id'])
            if tool_in_db is not None:
                agent_template.tools.append(tool_in_db)
            
            else:
                print(f"Error: tool with id `{tool['id']}` did not exist")

    db.commit()
    print("LOG: finished seeding database with default agent templates and tools")
    
