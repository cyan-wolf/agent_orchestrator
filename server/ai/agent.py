from datetime import datetime, timezone
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Checkpointer

from auth.tables import UserTable
from user_settings.tables import UserSettingsTable

class Agent:

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

        self.master_prompt = self.prepare_master_prompt(persona, purpose, user, user_settings, chat_summaries)

        self.graph = self.prepare_agent_graph(tools, model, checkpointer)


    def prepare_master_prompt(
        self,         
        persona: str, 
        purpose: str, 
        user: UserTable,
        user_settings: UserSettingsTable,
        chat_summaries: dict[str, str],
    ) -> str:
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


    def prepare_default_chat_model(self) -> BaseChatModel:
        """
        Prepares a default chat model for an agent.
        """
        return init_chat_model(
            "google_genai:gemini-2.0-flash",
            temperature=0,
        )


    def prepare_agent_graph(self, tools: list, model: BaseChatModel | None = None, checkpointer: Checkpointer = None) -> CompiledGraph:
        """
        Prepares the graph that the agent uses for control flow.
        """
        if model is None:
            model = self.prepare_default_chat_model()

        return create_react_agent(
            model=model,  
            tools=tools,  
            prompt=self.master_prompt,
            checkpointer=checkpointer,
        )