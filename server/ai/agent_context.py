from typing import Protocol
from ai.tracer import Tracer
from ai.agent import Agent

class AgentContext(Protocol):
    
    def get_owner_username(self) -> str:
        ...

    def get_chat_id(self) -> str:
        ...

    def get_tracer(self) -> Tracer:
        ...

    def get_agent_dict(self) -> dict[str, Agent]:
        ...
    
    def get_chat_summary_dict(self) -> dict[str, str]:
        ...

    def set_chat_summary_for_current(self, chat_summary: str) -> None:
        ...

    def invoke_agent(self, agent: Agent, user_input: str, as_main_agent: bool = False) -> str:
        ...

    def invoke_main_agent_with_text(self, username: str, user_input: str) -> str:
        ...
