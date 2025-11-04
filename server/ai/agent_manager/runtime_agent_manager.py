from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

from ai.tracing.schemas import AIMessageTrace, HumanMessageTrace
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.runnables.config import RunnableConfig

from ai.tools import control_flow, web_searching, image_generator, generic_tools
from ai.tools.code_sandbox import coding_tools
from ai.tools.scheduling import scheduling_tools
from ai.tools.math import math_tools
from ai.tracing.trace_decorator import Tracer
from ai.agent import Agent

from datetime import datetime, timezone

from user_settings import user_settings

from auth.auth import get_user_by_username
from chat.tables import ChatTable
from chat.chat_summaries import chat_summaries

from sqlalchemy.orm import Session

from ai.agent_manager.agent_context import AgentCtx

import uuid

def get_latest_agent_msg(agent_response: dict) -> BaseMessage:
    return agent_response["messages"][-1]


class RuntimeAgentManager:
    """
    The runtime representation of an agent manager. 
    """

    def __init__(self, db: Session, chat: ChatTable, chat_summaries: defaultdict[str, str], tracer: Tracer):
        """
        Initializes an agent manager.

        Args:
            db: The DB session to use during initialization.
            chat_id: The ID of the chat associated with this agent manager.
            owner_username: The username of the user associated with this manager.
            chat_summaries: The current chat summaries present when this manager was created.
            tracer: The tracer associated with this manager.
        """
        self.agents: dict[str, Agent] = {}

        config: RunnableConfig = {"configurable": {"thread_id": "1"}}
        self.config = config

        self.tracer = tracer

        self.chat_summaries = chat_summaries

        self.chat_id = chat.id
        self.owner_username = chat.user.username
        self.owner_user_id = chat.user.id

        self._initialize_agents(db)


    # ===== Protocol methods for `AgentManager` interface. =====

    def get_owner_username(self) -> str:
        return self.owner_username
    
    def get_owner_user_id(self) -> uuid.UUID:
        return self.owner_user_id

    def get_chat_id(self) -> uuid.UUID:
        return self.chat_id

    def get_tracer(self) -> Tracer:
        return self.tracer
    
    def get_agent_dict(self) -> dict[str, Agent]:
        return self.agents
    
    def get_chat_summary_dict(self) -> defaultdict[str, str]:
        return self.chat_summaries
    
    def set_chat_summary_for_current(self, db: Session, chat_summary_content: str) -> None:
        self._set_chat_summary(db, chat_summary_content)

    def invoke_agent(self, agent: Agent, user_input: str, db: Session, as_main_agent: bool = False) -> str:
        """
        Invokes the given agent using the provided user input.
        """

        # Bookeeping to keep track of the agent currently in control.
        prev_agent = self.agents["current_agent"]
        self.agents["current_agent"] = agent

        res = agent.graph.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            self.config,
        )
        message = get_latest_agent_msg(res)
        content = str(message.content)
        self.tracer.add(db, AIMessageTrace(agent_name=agent.name, content=content, is_main_agent=as_main_agent))

        # `agent` is no longer in control.
        # If the "main agent" did not switch during agent invocation, then it is 
        # safe to switch back to `prev_agent`.
        if prev_agent.name == self.agents["main_agent"].name:
            self.agents["current_agent"] = prev_agent

        return content

    def invoke_main_agent_with_text(self, username: str, user_input: str, db: Session) -> str:
        """
        Invokes the agent that is currently designated to be the main agent.
        """
        self.curr_db_session = db
        self.tracer.add(db, HumanMessageTrace(username=username, content=user_input))

        return self.invoke_agent(self.agents["main_agent"], user_input, db, as_main_agent=True)


    # ===== Other methods =====

    def _initialize_agents(self, db: Session):
        """
        Initializes and registers several agents.
        """

        user_owner = get_user_by_username(db, self.owner_username)
        settings = user_settings.get_settings_table_with_username(db, self.owner_username)

        ctx = self._to_ctx(db)

        self._register_agent(Agent("math_agent", 
            "You are a helpful math assistant.",
            """
            You can mainly use your Wolfram Alpha tool to solve math problems. 
            """,
            user_owner,
            settings,
            self.chat_summaries,
            [control_flow.prepare_switch_back_to_supervisor_tool(ctx), 
             control_flow.prepare_summarization_tool(ctx), 
             math_tools.prepare_run_wolfram_alpha_tool(ctx),
            ],
            checkpointer=InMemorySaver(),
        ))

        self._register_agent(Agent("coding_agent", 
            "You are a helpful coding assistant.",
            """
            You only work with Python, no other programming language.
            Always add comments and type annotations to any Python code you run.
            You have access to a Linux environment where you can run commands.
            """,
            user_owner,
            settings,
            self.chat_summaries,
            [coding_tools.prepare_create_file_tool(ctx), 
             coding_tools.prepare_run_command_tool(ctx), 
             coding_tools.prepare_run_code_snippet_tool(ctx),
             control_flow.prepare_switch_back_to_supervisor_tool(ctx), 
             control_flow.prepare_summarization_tool(ctx)],
            checkpointer=InMemorySaver(),
        ))

        self._register_agent(Agent("research_agent",  
            "You are a helpful research agent.",
            f"""
            Use the web search tool to look for information. 
            """, 
            user_owner,
            settings,
            self.chat_summaries,
            [web_searching.prepare_web_search_tool(ctx)],
            checkpointer=InMemorySaver(),
        ))

        self._register_agent(Agent("creator_agent", 
            "You are a a content generation agent.",
            f"""
            You can help the user create images using your image generation tool. 
            You receive requests to write textual content such as poems, stories, scripts.
            """,
            user_owner,
            settings,
            self.chat_summaries,
            [image_generator.prepare_image_generation_tool(ctx), 
             control_flow.prepare_summarization_tool(ctx), 
             control_flow.prepare_switch_back_to_supervisor_tool(ctx)],
            checkpointer=InMemorySaver(),
        ))

        self._register_agent(Agent("planner_agent", 
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
            user_owner,
            settings,
            self.chat_summaries,
            [generic_tools.prepare_get_current_date_tool(ctx),
             web_searching.prepare_request_external_info_tool(ctx),
             scheduling_tools.prepare_view_schedule_tool(ctx),
             scheduling_tools.prepare_add_new_event_tool(ctx),
             scheduling_tools.prepare_delete_event_tool(ctx),
             scheduling_tools.prepare_modify_event_tool(ctx),
             control_flow.prepare_summarization_tool(ctx),
             control_flow.prepare_switch_back_to_supervisor_tool(ctx)],
            checkpointer=InMemorySaver(),
        ))

        self._register_agent(Agent("supervisor_agent", 
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
            user_owner,
            settings,
            self.chat_summaries,
            control_flow.prepare_supervisor_agent_tools(ctx, extra_tools=[web_searching.prepare_request_external_info_tool(ctx)]),
            checkpointer=InMemorySaver()
        ))

        # "main_agent" is the agent that the user directly chats with.
        self.agents["main_agent"] = self.agents["supervisor_agent"]

        # "current_agent" is the agent currently in control. 
        self.agents["current_agent"] = self.agents["main_agent"]
 

    def _to_ctx(self, db: Session) -> AgentCtx:
        return AgentCtx(manager=self, db=db)
    

    def _register_agent(self, agent: Agent):
        """
        Registers the given agent to the agent manager. Allows the agent to be 
        called by other agents using its name.
        """
        self.agents[agent.name] = agent


    def _set_chat_summary(self, db: Session, chat_summary_content: str):
        """
        Sets the chat summary for the current agent.
        """
        agent_name = self._get_current_agent_name()

        # Save the chat summary to both the DB and the manager's runtime dictionary.
        chat_summaries.set_agent_chat_summary_in_db(db, self.chat_id, agent_name, chat_summary_content)
        self.chat_summaries[agent_name] = chat_summary_content


    def _get_current_agent_name(self) -> str:
        return self.agents["current_agent"].name
    
        