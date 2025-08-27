from dotenv import load_dotenv

from ai.models import AIMessageTrace, HumanMessageTrace, SerializedAgentManager
load_dotenv()

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.runnables.config import RunnableConfig

from ai.tools import control_flow, web_searching, image_generator, generic_tools
from ai.tools.code_sandbox import coding_tools
from ai.tools.scheduling import scheduling_tools
from ai.tracing import Tracer

from ai.agent import Agent

from datetime import datetime, timezone

def get_latest_agent_msg(agent_response: dict) -> BaseMessage:
    return agent_response["messages"][-1]


class AgentManager:
    def __init__(self, serialized_version: SerializedAgentManager, chat_id: str):
        """
        Initializes an agent manager.
        """
        self.agents: dict[str, Agent] = {}

        config: RunnableConfig = {"configurable": {"thread_id": "1"}}
        self.config = config

        self.tracer = Tracer(serialized_version.history)

        # agent name -> chat summary (for that agent)
        self.chat_summaries = serialized_version.chat_summaries

        self.chat_id = chat_id

        self.initialize_agents()

    
    def to_serialized(self) -> SerializedAgentManager:
        return SerializedAgentManager(
            history=self.tracer.get_history(), 
            chat_summaries=self.chat_summaries,
        )


    def set_chat_summary(self, chat_summary: str):
        """
        Sets the chat summary for the current agent.
        """
        self.chat_summaries[self.get_current_agent_name()] = chat_summary


    def initialize_agents(self):
        """
        Initializes and registers several agents.
        """

        self.register_agent(Agent("math_agent", "You are a helpful math assistant.", []))

        self.register_agent(Agent("coding_agent", 
            f"""
            You are a helpful coding assistant. You only work with Python, no other programming language.
            Always add comments and type annotations to any Python code you run.
            You have access to a Linux environment where you can run commands. 

            Run the summarization tool whenever something important gets done.

            Below is a summary of the previous chat you had with the user:
            {self.get_agent_chat_summary('coding_agent')}
            """, 
            [coding_tools.prepare_create_file_tool(self), 
             coding_tools.prepare_run_command_tool(self), 
             control_flow.prepare_switch_back_to_supervisor_tool(self), 
             control_flow.prepare_summarization_tool(self)],
            checkpointer=InMemorySaver(),
        ))

        self.register_agent(Agent("research_agent",  
            f"""
            You are a helpful research agent. Use the web search tool to look for information. 
            The current date in UTC is {datetime.now(tz=timezone.utc)}.
            """, 
            [web_searching.prepare_web_search_tool(self)],
            checkpointer=InMemorySaver(),
        ))

        self.register_agent(Agent("creator_agent", 
            f"""
            You are a a content generation agent. You can help the user create images using your image generation tool. 
            You receive requests to write textual content such as poems, stories, scripts.

            Use the summarization tool whenever you generate a piece of content. Don't spam the summarization tool.

            Below is a summary of the previous chat you had with the user:
            {self.get_agent_chat_summary('creator_agent')}
            """,
            [image_generator.prepare_image_generation_tool(self), 
             control_flow.prepare_summarization_tool(self), 
             control_flow.prepare_switch_back_to_supervisor_tool(self)],
            checkpointer=InMemorySaver(),
        ))

        self.register_agent(Agent("planner_agent", 
            f"""
            You are a planner agent. You help the user make a schedule along with helping them organize it. 
            You can view and modify the schedule with your tools. You can also check the current date with your tools.

            Please assume that the user's timezone is Atlantic Standard Time (AST).

            You can check the current date and time using your get_current_date_tool. As a good reference point, 
            keep in mind that your current conversation with the user started at {datetime.now(tz=timezone.utc)} (UTC time) though.

            Use the summarization tool whenever you do something worth remembering later. Don't spam the summarization tool.

            Below is a summary of the previous chat you had with the user:
            {self.get_agent_chat_summary('planner_agent')}
            """,
            [generic_tools.prepare_get_current_date_tool(self),
             scheduling_tools.prepare_view_schedule_tool(self),
             scheduling_tools.prepare_add_new_event_tool(self),
             scheduling_tools.prepare_delete_event_tool(self),
             scheduling_tools.prepare_modify_event_tool(self),
             control_flow.prepare_summarization_tool(self),
             control_flow.prepare_switch_back_to_supervisor_tool(self)],
            checkpointer=InMemorySaver(),
        ))

        self.register_agent(Agent("supervisor_agent", 
            f"""
            You are a helpful assistant. You are kind of sassy. 
            You can answer any topic except for one caveat: never EVER answer questions about Bruno.

            Don't hesitate to use the `switch_to_more_qualified_agent` tool.

            You are the supervisor of several other helper agents. You sometimes hand-off the user to these helper 
            agents. Thankfully, these agents write summaries of their chats with the user. This tool shows you 
            the chat summaries for all agents. This way, you can see what they have done.

            Run the `summarize_chat` tool every 5 messages. This is very important.

            Below is a summary of the previous chat you had with this user:
            {self.get_agent_chat_summary('supervisor_agent')}
            """,
            control_flow.prepare_supervisor_agent_tools(self),
            checkpointer=InMemorySaver()
        ))

        # "main_agent" is the agent that the user directly chats with.
        self.agents["main_agent"] = self.agents["supervisor_agent"]

        # "current_agent" is the agent currently in control. This is 
        # used to keep track of which agents call the tools.
        # this is currently broken vvv
        self.agents["current_agent"] = self.agents["main_agent"]
 

    def register_agent(self, agent: Agent):
        """
        Registers the given agent to the agent manager. Allows the agent to be 
        called by other agents using its name.
        """
        self.agents[agent.name] = agent


    def invoke_agent(self, agent: Agent, user_input: str, as_main_agent: bool = False) -> str:
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
        self.tracer.add(AIMessageTrace(agent_name=agent.name, content=content, is_main_agent=as_main_agent))

        # `agent` is no longer in control.
        # If the "main agent" did not switch during agent invocation, then it is 
        # safe to switch back to `prev_agent`.
        if prev_agent.name == self.agents["main_agent"].name:
            self.agents["current_agent"] = prev_agent

        return content


    def invoke_main_with_text(self, username: str, user_input: str) -> str:
        """
        Invokes the agent that is currently designated to be the main agent.
        """
        self.tracer.add(HumanMessageTrace(username=username, content=user_input))

        return self.invoke_agent(self.agents["main_agent"], user_input, as_main_agent=True)


    def get_current_agent_name(self) -> str:
        return self.agents["current_agent"].name
    
    
    def get_agent_chat_summary(self, agent_name: str) -> str:
        chat_summary = self.chat_summaries.get(agent_name)

        if chat_summary is None:
            return "This is a new chat. No summary available."
        else:
            return chat_summary