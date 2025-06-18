from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.types import Checkpointer
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.runnables.config import RunnableConfig

from langchain_tavily import TavilySearch

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph

from tools import generic_tools, code_runner, image_generator

def get_latest_agent_msg(agent_response: dict) -> str:
    return agent_response["messages"][-1].content

def invoke_agent(agent: CompiledGraph, config: RunnableConfig, user_input: str) -> dict:
    res = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
    )
    return res

class AgentManager:
    def __init__(self):
        self.agents = {}

        config: RunnableConfig = {"configurable": {"thread_id": "1"}}
        self.config = config

        self.initialize_agents()


    def initialize_agents(self):
        self.agents["math_agent"] = self.prepare_agent("You are a helpful math assistant.", 
                                                       [generic_tools.add_two_numbers])
        
        self.agents["coding_agent"] = self.prepare_agent(
            """
            You are a helpful coding assistant. 
            Create a Python program based on the given query.
            """, 
            [],
        )
        self.agents["research_agent"] = self.prepare_agent(
            """
            You are a helpful research agent. You look for articles on the internet. 
            You can also tell the current time and use it to tell if an article is 
            talking about something in the past or in the future.
            """, 
            [generic_tools.get_current_date, TavilySearch(max_results=5)],
        )
        self.agents["writer_agent"] = self.prepare_agent(
            """
            You are a writer. You receive requests to write textual content such as poems, stories, scripts.
            """,
            [],
        )

        self.agents["supervisor_agent"] = self.prepare_agent(
            """
            You are a helpful assistant. You are kind of sassy. 
            You can answer any topic except for one caveat: never EVER answer questions about Bruno.
            """,
            self.prepare_supervisor_agent_tools(),
            checkpointer=InMemorySaver(),
        )

        self.agents["main_agent"] = self.agents["supervisor_agent"]


    def prepare_supervisor_agent_tools(self):
        def request_math_help(query: str) -> str:
            """Asks the math expert for help."""

            res = invoke_agent(self.agents["math_agent"], self.config, query)
            return get_latest_agent_msg(res)


        def request_code(query: str) -> str:
            """Asks the coding expert for a Python program that satisfies the given query."""

            print(f"LOG: {query}")

            res = invoke_agent(self.agents["coding_agent"], self.config, query)
            return get_latest_agent_msg(res)


        def request_external_information(query: str) -> str:
            """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""

            res = invoke_agent(self.agents["research_agent"], self.config, query)
            return get_latest_agent_msg(res)
        

        def request_content_generation(query: str, content_type: str) -> str:
            """
            Asks the content generation tool for some content. This could be text or an image.
            The content type must be specified, it can be any of the following:
                - text
                - image
            """
            if content_type == "image":
                # TODO: This just shows the image using a Python library. 
                # Figure out what to do with the image, as it must be given to the client somehow.
                image_generator.generate_image(query)
                return "successfully generated and showed image to user"
            
            elif content_type == "text":
                resp = invoke_agent(self.agents["writer_agent"], self.config, query)
                return get_latest_agent_msg(resp)
            else:
                return f"error: unknown content type '{content_type}'"
        

        return [
            request_math_help, request_code, request_external_information, 
            request_content_generation,
            code_runner.run_python_program]
    

    def prepare_default_chat_model(self) -> BaseChatModel:
        return init_chat_model(
            "google_genai:gemini-2.0-flash",
            temperature=0,
        )


    def prepare_agent(self, master_prompt: str, tools: list, model: BaseChatModel | None = None, checkpointer: Checkpointer = None) -> CompiledGraph:
        if model is None:
            model = self.prepare_default_chat_model()

        return create_react_agent(
            model=model,  
            tools=tools,  
            prompt=master_prompt,
            checkpointer=checkpointer,
        )


    def invoke_with_text(self, user_input: str) -> dict:
        return invoke_agent(self.agents["main_agent"], self.config, user_input)
