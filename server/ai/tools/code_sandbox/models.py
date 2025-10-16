from pydantic import BaseModel, Field

class RunCommandSchema(BaseModel):
    """
    Input schema for the run_command tool.
    """
    command: str = Field(
        description="The exact, complete command string (e.g., 'ls -l', 'echo hello world', 'python script.py') to execute in the sandbox environment."
    )


class RunCodeSnippetSchema(BaseModel):
    """
    Input schema for the run_code_snippet tool.
    """
    source_code: str = Field(
        description="The exact contents of the Python code to execute in the sandbox environment."
    )