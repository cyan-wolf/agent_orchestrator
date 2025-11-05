from ai.agent.agent_interface import IAgent
from ai.agent.runtime_agent import RuntimeAgent
from ai.agent_manager.agent_context import AgentCtx
from ai.tools import control_flow, web_searching, image_generator, generic_tools
from ai.tools.code_sandbox import coding_tools
from ai.tools.scheduling import scheduling_tools
from ai.tools.math import math_tools
from datetime import datetime, timezone
from auth.tables import UserTable
from langgraph.checkpoint.memory import InMemorySaver


# TODO: Read these from the database.
def agent_factory_for_chat(ctx: AgentCtx, owner: UserTable) -> list[IAgent]:
    # from ai.tools.registry.tool_factory_store import get_tool_factory_in_mem_store
    # print(get_tool_factory_in_mem_store().in_memory_store)

    agents: list[IAgent] = []

    agents.append(RuntimeAgent("supervisor_agent", 
        """
        You are a helpful assistant. 
        """,
        f"""
        You are the supervisor of several other helper agents. You sometimes hand-off the user to these helper 
        agents. Thankfully, these agents write summaries of their chats with the user. This tool shows you 
        the chat summaries for all agents. This way, you can see what they have done. You can look up stuff that you don't know using 
        your request_external_info_tool. If the user asks you something you don't know (such as if it were a future event or ocassion) 
        use this tool, it will get the researcher agent to provide you with a result.

        Don't hesitate to use the `switch_to_more_qualified_agent` tool.
        
        Run the `summarize_chat` tool every 5 messages. This is very important.
        """,
        owner,
        ctx.manager.get_chat_summary_dict(),
        [control_flow.prepare_switch_to_more_qualified_agent_tool(ctx),
         control_flow.prepare_check_helper_agent_summaries_tool(ctx), 
         web_searching.prepare_request_external_info_tool(ctx),
         control_flow.prepare_summarization_tool(ctx)],
        checkpointer=InMemorySaver(),
    ))

    agents.append(RuntimeAgent("math_agent", 
        "You are a helpful math assistant.",
        """
        You can mainly use your Wolfram Alpha tool to solve math problems. 
        """,
        owner,
        ctx.manager.get_chat_summary_dict(),
        [control_flow.prepare_switch_back_to_supervisor_tool(ctx), 
            control_flow.prepare_summarization_tool(ctx), 
            math_tools.prepare_run_wolfram_alpha_tool(ctx),
        ],
        checkpointer=InMemorySaver(),
    ))

    agents.append(RuntimeAgent("coding_agent", 
        "You are a helpful coding assistant.",
        """
        You only work with Python, no other programming language.
        Always add comments and type annotations to any Python code you run.
        You have access to a Linux environment where you can run commands.
        """,
        owner,
        ctx.manager.get_chat_summary_dict(),
        [coding_tools.prepare_create_file_tool(ctx), 
            coding_tools.prepare_run_command_tool(ctx), 
            coding_tools.prepare_run_code_snippet_tool(ctx),
            control_flow.prepare_switch_back_to_supervisor_tool(ctx), 
            control_flow.prepare_summarization_tool(ctx)],
        checkpointer=InMemorySaver(),
    ))

    agents.append(RuntimeAgent("research_agent",  
        "You are a helpful research agent.",
        f"""
        Use the web search tool to look for information. 
        """, 
        owner,
        ctx.manager.get_chat_summary_dict(),
        [web_searching.prepare_web_search_tool(ctx)],
        checkpointer=InMemorySaver(),
    ))

    agents.append(RuntimeAgent("creator_agent", 
        "You are a a content generation agent.",
        f"""
        You can help the user create images using your image generation tool. 
        You receive requests to write textual content such as poems, stories, scripts.
        """,
        owner,
        ctx.manager.get_chat_summary_dict(),
        [image_generator.prepare_image_generation_tool(ctx), 
            control_flow.prepare_summarization_tool(ctx), 
            control_flow.prepare_switch_back_to_supervisor_tool(ctx)],
        checkpointer=InMemorySaver(),
    ))

    agents.append(RuntimeAgent("planner_agent", 
        "You are a planner agent.",
        f"""
        You help the user make a schedule along with helping them organize it. 
        You can view and modify the schedule with your tools. You can also check the current date with your tools.

        You don't know where the user lives. Please use your tools to find out. Knowing where the user lives will 
        help you recommend more appropriate events (for example: don't recommend going to the beach if its winter and the user 
        lives in Toronto; but do recommend going to the beach if its summer and the user lives in Miami). You can use the request external 
        information tool to learn more about possible events in a location if the user asks you.

        You can check the current date and time using your get_current_date_tool. As a good reference point, 
        keep in mind that your current conversation with the user started at {datetime.now(tz=timezone.utc)} (UTC time) though.

        When you get data from your view events tool, please format them in a nice way.
        """,
        owner,
        ctx.manager.get_chat_summary_dict(),
        [
            generic_tools.prepare_get_current_date_tool(ctx),
            web_searching.prepare_request_external_info_tool(ctx),
            scheduling_tools.prepare_view_schedule_tool(ctx),
            scheduling_tools.prepare_add_new_event_tool(ctx),
            scheduling_tools.prepare_delete_event_tool(ctx),
            scheduling_tools.prepare_modify_event_tool(ctx),
            control_flow.prepare_summarization_tool(ctx),
            control_flow.prepare_switch_back_to_supervisor_tool(ctx),
        ],
        checkpointer=InMemorySaver(),
    ))

    return agents