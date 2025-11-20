"""
This module defines tools and helper functions relating to image generation. 
Mostly used by the creator agent.
"""

import base64
import io
import os
from dotenv import load_dotenv
load_dotenv()

from ai.tracing.schemas import ImageCreationTrace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.registry.tool_register_decorator import register_tool_factory

from huggingface_hub import InferenceClient

from PIL import Image

from utils.utils import get_env_raise_if_none

HUGGINGFACE_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0" 

client = InferenceClient(api_key=get_env_raise_if_none("HUGGINGFACEHUB_API_TOKEN"))

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


def _generate_image_impl(query: str) -> str:
    """
    Generates an image based on the specified query. Returns the base64 encoded image.
    """
    image: Image.Image = client.text_to_image(
        prompt=query, 
        model=HUGGINGFACE_IMAGE_MODEL,
    )
    
    # Save the PIL image to an in-memory buffer and encode to base64.
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG") 
    image_base64: str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return image_base64