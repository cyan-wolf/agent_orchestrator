from typing import Protocol

class IAgent(Protocol):
    def get_name(self) -> str:
        ...

    
    def invoke_with_text(self, text_input: str) -> str:
        ...

