from datetime import datetime, timezone
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Checkpointer

from auth.tables import UserTable
from user_settings.tables import UserSettingsTable

class RuntimeAgent:
    """
    The runtime representation of an agent. Internally builds a chat model using `langchain` and 
    then constructs a ReAct agent using `langgraph`.
    """

    CONFIG: RunnableConfig = {"configurable": {"thread_id": "1"}}

    def __init__(
        self, 
        name: str, 

        persona: str, 
        purpose: str, 
        user: UserTable,
        user_settings: UserSettingsTable,
        chat_summaries: dict[str, str], 

        tools: list, 
        model: BaseChatModel | None = None, 
        checkpointer: Checkpointer = None,
    ):
        """
        Initializes an agent.
        """
        self.name = name

        self.master_prompt = self._prepare_master_prompt(persona, purpose, user, user_settings, chat_summaries)
        self.graph = self._prepare_agent_graph(tools, model, checkpointer)


    # === `IAgent` implementation ===

    def get_name(self) -> str:
        return self.name
    

    def invoke_with_text(self, text_input: str) -> str:
        res = self.graph.invoke(
            {"messages": [{"role": "user", "content": text_input}]},
            RuntimeAgent.CONFIG,
        )
        message = self._get_latest_agent_msg(res)
        content = str(message.content)

        return content

    # === end of `IAgent` implementation


    def _prepare_master_prompt(
        self,         
        persona: str, 
        purpose: str, 
        user: UserTable,
        user_settings: UserSettingsTable,
        chat_summaries: dict[str, str],
    ) -> str:
        """
        Args:
            persona: The personality of the agent.
            purpose: The functionality that the agent is meant to provide.
            user: The user associated to this agent.
            user_settings: The settings set by the user associated to this agent.
            chat_summaries: The chat summaries associated with the current chat.
        """

        master_prompt = (
            f"""
            Persona:
            {persona}

            Purpose:
            {purpose}

            Some basic info on the user:
            * User's username: {user.username}
            * User's full name: {user.full_name}
            * Preferred Language: {user_settings.language}
            * City: {user_settings.city}
            * Country: {user_settings.country}
            * Time Zone: {user_settings.timezone}

            The current date in UTC is {datetime.now(tz=timezone.utc)}. Please use this to adjust how you speak. 
            If you talk about something that ocurred before this date, always speak of it in past tense. 
            For example, if the current date were October 12, 2024 and a tool shows you that something occurred in 2022 
            speak in past tense, always.

            Please speak in the user's preferred language. If the user tries to get you to speak in another language, 
            tell them to change their preferred language in the settings. Of course, tell them about the settings in 
            the language that they are using. For example, if you are set to French and the user is asking you confused 
            in Spanish, tell them to change their language in Spanish.

            Your tools all work with UTC time, but the user is going to be confused if you respond using UTC. Please 
            use your tools / check your info about them to figure out the user's timezone. This won't change how you call your tools, but it will 
            confusing the user when you mention dates and times from your tools, which will be in UTC.

            If you have a chat summarization tool, use it to summarize the chat to save 
            conversation progress whenever something important happens.

            Here is a summary of the previous chat you had with the user:
            {chat_summaries[self.name]}
            """
        )
        return master_prompt


    def _prepare_default_chat_model(self) -> BaseChatModel:
        """
        Prepares a default chat model for an agent.
        """
        return init_chat_model(
            "google_genai:gemini-2.0-flash",
            temperature=0,
        )


    def _prepare_agent_graph(self, tools: list, model: BaseChatModel | None = None, checkpointer: Checkpointer = None) -> CompiledGraph:
        """
        Prepares the graph that the agent uses for control flow.
        """
        if model is None:
            model = self._prepare_default_chat_model()

        return create_react_agent(
            model=model,  
            tools=tools,  
            prompt=self.master_prompt,
            checkpointer=checkpointer,
        )
    

    def _get_latest_agent_msg(self, agent_response: dict) -> BaseMessage:
        return agent_response["messages"][-1]