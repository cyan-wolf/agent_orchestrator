"""
This module defines tools and helper functions relating to image generation. 
Mostly used by the creator agent.
"""

from dotenv import load_dotenv
load_dotenv()

from ai.tracing.schemas import ImageCreationTrace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.registry.tool_register_decorator import register_tool_factory

from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

_IMAGE_LLM = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash-image")


@register_tool_factory(tool_id='generate_image_and_show_it_to_user')
def prepare_image_generation_tool(ctx: AgentCtx):
    """
    Prepares a tool that generates the image specified by the query and automatically 
    shows the image to the user.
    """

    def generate_image_and_show_it_to_user(query: str) -> str:
        """
        Generates the image specified by the query. This tool automatically 
        shows the image to the user.
        """
        image_base64 = _generate_image_impl(query)

        # Used for showing the image to the user.
        ctx.manager.get_tracer().add(ctx.db, ImageCreationTrace(base64_encoded_image=image_base64, caption=query))

        return "Successfully generated and showed image to user."
        
    return generate_image_and_show_it_to_user


def _get_image_base64(response: BaseMessage):
    image_block = next(
        block
        for block in response.content
        if isinstance(block, dict) and block.get("image_url")
    )
    return image_block["image_url"].get("url").split(",")[-1]


def _generate_image_impl(query: str) -> str:
    """
    Generates an image based on the specified query. Returns the base64 encoded image.
    """
    message = {
        "role": "user",
        "content": query,
    }

    response = _IMAGE_LLM.invoke(
        [message],
        generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
    )

    image_base64: str = _get_image_base64(response)
    return image_base64