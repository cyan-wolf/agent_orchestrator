from ai.models import ImageSideEffectTrace
from ai.tools import image_generator
from ai.tracing import trace

def prepare_supervisor_agent_tools(agent_manager):
    @trace(agent_manager)
    def request_math_help(query: str) -> str:
        """Asks the math expert for help."""
        return agent_manager.invoke_agent(agent_manager.agents["math_agent"], query)

    @trace(agent_manager)
    def switch_to_more_qualified_agent(agent_name: str) -> str:
        """
        Switches to the given agent.

        Possible agents:
            - coding_agent
            - creator_agent
        """
        if agent_name in {"coding_agent", "creator_agent"}:
            agent_manager.agents["main_agent"] = agent_manager.agents[agent_name]
            return f"switched to {agent_name}!"
        
        else:
            return f"unknown agent name '{agent_name}'"

    @trace(agent_manager)
    def request_external_information(query: str) -> str:
        """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""
        return agent_manager.invoke_agent(agent_manager.agents["research_agent"], query)
    
    return [
        request_math_help, request_external_information, 
        switch_to_more_qualified_agent, 
        prepare_summarization_tool(agent_manager),
    ]


def run_agent_specific_cleanup(agent_manager):
    from ai.tools.code_sandbox.sandbox_management import clean_up_container_for_chat

    if agent_manager.agents["main_agent"].name == "coding_agent":
        # Clean up container for current chat when the coding agent runs cleanup.
        clean_up_container_for_chat(agent_manager.chat_id)


def prepare_summarization_tool(agent_manager):
    @trace(agent_manager)
    def summarize_chat(chat_summary: str):
        """
        Stores a summary of the current chat.
        """
        agent_manager.set_chat_summary(chat_summary)

        return "Successfully summarized chat."

    return summarize_chat


def prepare_switch_back_to_supervisor_tool(agent_manager):
    @trace(agent_manager)
    def switch_back_to_supervisor():
        """
        Switches back to the supervisor. 
        """
        run_agent_specific_cleanup(agent_manager)

        agent_manager.agents["main_agent"] = agent_manager.agents["supervisor_agent"]
        return "switched back to supervisor"
    
    return switch_back_to_supervisor
