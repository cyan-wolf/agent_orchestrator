"""
This module defines the tools used by the math agent, along with helper functions.
"""

import os
import requests
import base64
from ai.tracing.schemas import ImageCreationTrace
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.registry.tool_register_decorator import register_tool_factory

_API_URL = "https://www.wolframalpha.com/api/v1/llm-api"


@register_tool_factory(tool_id='run_wolfram_alpha_tool')
def prepare_run_wolfram_alpha_tool(ctx: AgentCtx):
    """
    Prepares a tool that sends queries to the Wolfram Alpha API.
    """

    
    def run_wolfram_alpha_tool(query: str) -> str:
        """
        Invokes Wolfram Alpha with the given query. Only use when necessary, 
        for example if the user asks you basic arithmetic just answer it without 
        using this tool. If the user explicitly tells you to use this tool, then use it, but 
        avoid using it unless absolutely necessary. When the tool output contains plots, they 
        are automatically shown to the user.
        """
        try:
            params = {
                "input": query,
                "appid": _get_wolfram_alpha_app_id(),
            }
            resp = requests.get(_API_URL, params=params)
            resp.raise_for_status()
            
            output = resp.text

            for image_link, caption in _extract_image_links_from_api_response(output):
                image_base64 = _get_image_as_base64(image_link)

                if image_base64 is not None:
                    _add_image_to_trace_history(ctx, image_base64, caption)

            return output
        
        # 400 and 500 errors
        except requests.exceptions.HTTPError as err:
            # Error code 501 means that the API did not understand the given query.
            if err.response.status_code == 501:
                return f"Error: The API could not interpret the given query '{query}'. The API returned status (501) in response."

            # Do not print the `err` itself, it may contain the URL used to 
            # perform the request. However, since the API uses URL encoded params, 
            # the API key is part of the URL.
            err_msg = f"Error: HTTP error occurred: (status {err.response.status_code})"
            return err_msg

        except requests.exceptions.RequestException as e:
            err_msg = f"Error: Other request error occurred: {e}"
            print(err_msg)
            return err_msg
    
    return run_wolfram_alpha_tool


def _get_wolfram_alpha_app_id() -> str:
    app_id = os.getenv("WOLFRAM_ALPHA_APPID")
    assert app_id, "Wolfram APP ID was None"
    return app_id


def _get_image_as_base64(url: str) -> str | None:
    """
    Fetches an image from a URL and returns its base64 encoded string.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Raise an exception for bad status codes

        # The raw content of the image.
        image_content = response.content

        # Encode the binary content to Base64.
        base64_encoded_bytes = base64.b64encode(image_content)

        # Decode the bytes to a string.
        base64_encoded_string = base64_encoded_bytes.decode('utf-8')

        return base64_encoded_string

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None


def _extract_image_links_from_api_response(tool_output: str) -> list[tuple[str, str]]:
    lines = tool_output.split('\n')
    image_links = []

    for i in range(len(lines)):
        if lines[i].startswith("image: "):
            url = lines[i].split("image: ")[1]
            caption = lines[i + 1]

            image_links.append((url, caption))

    return image_links


def _add_image_to_trace_history(ctx: AgentCtx, image_base64: str, caption: str):
    # Used for showing the image to the user.
    ctx.manager.get_tracer().add(ctx.db, ImageCreationTrace(base64_encoded_image=image_base64, caption=caption))