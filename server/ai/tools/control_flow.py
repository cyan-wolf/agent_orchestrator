from ai.models import ImageSideEffectTrace
from ai.tools import image_generator
from ai.tracing import trace

def prepare_supervisor_agent_tools(agent_manager):
    @trace(agent_manager)
    def request_math_help(query: str) -> str:
        """Asks the math expert for help."""
        return agent_manager.invoke_agent(agent_manager.agents["math_agent"], query)

    @trace(agent_manager)
    def switch_to_more_qualified_agent(agent_name: str, reason: str | None) -> str:
        """
        Switches to the given agent. A reason for the switch can optionally be passed to this tool. 
        The reason is passed on to the new agent so that it has context on what it's supposed to do.

        Possible agents:
            - coding_agent
            - creator_agent
            - planner_agent
        """
        if agent_name in {"coding_agent", "creator_agent", "planner_agent"}:
            # Switch the 'main_agent' (i.e. the agent actually in control).
            agent_manager.agents["main_agent"] = agent_manager.agents[agent_name]

            # Tell the new 'main_agent' why it's supposed to do.
            agent_manager.invoke_agent(
                agent_manager.agents["main_agent"], 
                f"The supervisor agent handed off the user to you! Do your best. This was its reason: {reason}"
            )

            return f"switched to {agent_name}!"
        
        else:
            return f"unknown agent name '{agent_name}'"
        
    @trace(agent_manager)
    def check_helper_agent_chat_summaries():
        """
        Used for checking what the helper agents have talked about with the user.
        """
        return str(agent_manager.chat_summaries)

    @trace(agent_manager)
    def request_external_information(query: str) -> str:
        """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""
        return agent_manager.invoke_agent(agent_manager.agents["research_agent"], query)
    
    return [
        request_math_help, request_external_information, 
        switch_to_more_qualified_agent, 
        check_helper_agent_chat_summaries,
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
