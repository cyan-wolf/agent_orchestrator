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
        """
        if agent_name == "coding_agent":
            agent_manager.agents["main_agent"] = agent_manager.agents[agent_name]
            return "switched to coding agent!"
        
        else:
            return f"unknown agent name '{agent_name}'"

    @trace(agent_manager)
    def request_external_information(query: str) -> str:
        """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""
        return agent_manager.invoke_agent(agent_manager.agents["research_agent"], query)
    
    @trace(agent_manager)
    def request_content_generation(query: str, content_type: str) -> str:
        """
        Asks the content generation tool for some content. This could be text or an image.
        The content type must be specified, it can be any of the following:
            - text
            - image
        """
        if content_type == "image":
            image_base64 = image_generator.generate_image(query)
            agent_manager.tracer.add(ImageSideEffectTrace(base64_encoded_image=image_base64))

            return "successfully generated and showed image to user"
        
        elif content_type == "text":
            return agent_manager.invoke_agent(agent_manager.agents["writer_agent"], query)
        else:
            return f"error: unknown content type '{content_type}'"
    
    return [
        request_math_help, request_external_information, 
        request_content_generation, switch_to_more_qualified_agent, 
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
