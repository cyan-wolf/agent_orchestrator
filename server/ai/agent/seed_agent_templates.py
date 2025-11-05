"""
This module exports a helper function of the same name that seeds the database with default agent templates and tools.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from ai.agent.tables import AgentTemplateTable, ToolTable
from typing import Any

DEFAULT_TOOLS: list[dict[str, str]] = [
    {
        "id": "switch_to_more_qualified_agent",
        "name": "Switch to more Qualified Agent",
        "description": """Switches to a more qualified agent.""",
    },
    {
        "id": "check_helper_agent_chat_summaries",
        "name": "Check Helper Agent Chat Summaries",
        "description": 
            """Checks the helper agent chat summaries.""",
    },
    {
        "id": "summarize_chat",
        "name": "Summarize Chat",
        "description": 
            """Summarizes current chat.""",
    },
    {
        "id": "switch_back_to_supervisor",
        "name": "Switch back to Supervisor Agent",
        "description": 
            """Switches back to the supervisor agent.""",
    },
    {
        "id": "run_wolfram_alpha_tool",
        "name": "Run Wolfram Alpha API Tool",
        "description": 
            """Connects to the Wolfram Alpha API. """,
    },
    {
        "id": "create_file", 
        "name": "Create File in Linux Environment",
        "description": 
            """Creates a file in the agent's Linux environment.""",
    },
    {
        "id": "run_command",
        "name": "Run Command in Linux Environment",
        "description": 
            """Runs a command in the agent's Linux environment.""",
    },
    {
        "id": "run_code_snippet_tool",
        "name": "Run Code Snippet in Linux Environment",
        "description": 
            """Runs a code snippet in the agent's Linux environment.""",
    },
    {
        "id": "request_external_information",
        "name": "Request External Information",
        "description": 
            """Requests external information.""",
    },
    {
        "id": "get_current_date",
        "name": "Get Current Date",
        "description": 
            """Gets the current (UTC) date as an ISO formatted string.""",
    },
    {
        "id": "perform_web_search",
        "name": "Perform Web Search",
        "description": 
            """Performs a web search.""",
    },
    {
        "id": "generate_image_and_show_it_to_user",
        "name": "Generate Image and Show it to User",
        "description": 
            """Generates an image and shows it to the user.""",
    },
    {
        "id": "view_schedule",
        "name": "View Schedule",
        "description": 
            """View the events in the user's schedule.""",
    },
    {
        "id": "add_new_event",
        "name": "Add New Event to Schedule",
        "description": 
            """Adds a new event to the user's schedule.""",
    },
    {
        "id": "remove_event_with_id",
        "name": "Remove Event with ID from Schedule",
        "description": 
            """Removes the event with the given ID from the user's schedule.""",
    },
    {
        "id": "modify_event",
        "name": "Modify Event in Schedule",
        "description": 
            """Modifies an event in the user's schedule.""",
    },
]


DEFAULT_AGENTS: list[dict[str, Any]] = [
    {
        "name": "supervisor_agent",
        "persona": """You are a helpful assistant. """,
        "purpose": 
            """
You are the supervisor of several other helper agents. You sometimes hand-off the user to these helper 
agents. Thankfully, these agents write summaries of their chats with the user. This tool shows you 
the chat summaries for all agents. This way, you can see what they have done. You can look up stuff that you don't know using 
your request_external_info_tool. If the user asks you something you don't know (such as if it were a future event or ocassion) 
use this tool, it will get the researcher agent to provide you with a result.

Don't hesitate to use the `switch_to_more_qualified_agent` tool.

Run the `summarize_chat` tool every 5 messages. This is very important.
            """,
        "is_switchable_into": True,
        "tools": [
            'switch_to_more_qualified_agent',
            'check_helper_agent_chat_summaries',
            'request_external_information',
            'summarize_chat',
        ],
    },
    {
        "name": "math_agent",
        "persona": """You are a helpful math assistant.""",
        "purpose": 
            """
            You can mainly use your Wolfram Alpha tool to solve math problems. 
            """,
        "is_switchable_into": True,
        "tools": [
            'switch_back_to_supervisor',
            'summarize_chat',
            'run_wolfram_alpha_tool',
        ],
    },
    {
        "name": "coding_agent",
        "persona": """You are a helpful coding assistant.""",
        "purpose": 
            """
You only work with Python, no other programming language.
Always add comments and type annotations to any Python code you run.
You have access to a Linux environment where you can run commands.
            """,
        "is_switchable_into": True,
        "tools": [
            'create_file',
            'run_command',
            'run_code_snippet_tool',
            'switch_back_to_supervisor',
            'summarize_chat',
        ],
    },
    {
        "name": "research_agent",
        "persona": """You are a helpful research agent.""",
        "purpose": 
            """
Use the web search tool to look for information. 
            """,
        "is_switchable_into": False,
        "tools": [
            'perform_web_search',
        ],
    },
    {
        "name": "creator_agent",
        "persona": """You are a a content generation agent.""",
        "purpose": 
            """
You can help the user create images using your image generation tool. 
You receive requests to write textual content such as poems, stories, scripts.
            """,
        "is_switchable_into": True,
        "tools": [
            'generate_image_and_show_it_to_user',
            'switch_back_to_supervisor',
            'summarize_chat',
        ],
    },
    {
        "name": "planner_agent",
        "persona": """You are a planner agent.""",
        "purpose": 
            """
You help the user make a schedule along with helping them organize it. 
You can view and modify the schedule with your tools. You can also check the current date with your tools.

You don't know where the user lives. Please use your tools to find out. Knowing where the user lives will 
help you recommend more appropriate events (for example: don't recommend going to the beach if its winter and the user 
lives in Toronto; but do recommend going to the beach if its summer and the user lives in Miami). You can use the request external 
information tool to learn more about possible events in a location if the user asks you.

When you get data from your view events tool, please format them in a nice way.
            """,
        "is_switchable_into": True,
        "tools": [
            'get_current_date',
            'request_external_information',
            'view_schedule',
            'add_new_event',
            'remove_event_with_id',
            'modify_event',
            'switch_back_to_supervisor',
            'summarize_chat',
        ],
    },
]

def seed_agent_templates(db: Session):
    tool_table_populated = db.scalar(select(ToolTable).limit(1)) is not None

    if tool_table_populated:
        existing_tools = { tool.id: tool for tool in db.scalars(select(ToolTable)) }

    else:
        print("LOG: Seeding default tools")
        existing_tools = {}
        for tool_data in DEFAULT_TOOLS:
            tool = ToolTable(**tool_data)
            db.add(tool)
            existing_tools[tool.id] = tool

        # Make sure that the tool PKs are assigned.
        db.flush()

    agent_table_populated = db.scalar(select(AgentTemplateTable).limit(1)) is not None

    if agent_table_populated:
        print("LOG: agent template seeding skipped; agent templates already exist")
        return

    for agent_template_data in DEFAULT_AGENTS:
        # Strip unnecessary whitespace.
        agent_template_data["purpose"] = agent_template_data["purpose"].strip()

        needed_tool_ids: list[str] = agent_template_data.pop("tools")

        agent_template = AgentTemplateTable(**agent_template_data)
        db.add(agent_template)

        for tool_id in needed_tool_ids:
            tool_in_db = existing_tools.get(tool_id)
            if tool_in_db is not None:
                agent_template.tools.append(tool_in_db)
            
            else:
                print(f"Error: tool with id `{tool_id}` did not exist")

    db.commit()
    print("LOG: finished seeding database with default agent templates and tools")
    
