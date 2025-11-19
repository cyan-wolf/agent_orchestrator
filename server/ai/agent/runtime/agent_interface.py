from typing import Protocol

class IAgent(Protocol):
    """
    Abstract interface for a runtime agent.
    """

    def get_name(self) -> str:
        ...

    
    def invoke_with_text(self, text_input: str) -> str:
        ...

