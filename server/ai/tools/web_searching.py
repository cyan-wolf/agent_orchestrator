"""
This module is for defining tools relating to web searches.
"""

from langchain_tavily import TavilySearch
from ai.agent_manager.agent_context import AgentCtx
from ai.tools.registry.tool_register_decorator import register_tool_factory

import json

@register_tool_factory(tool_id='perform_web_search')
def prepare_web_search_tool(ctx: AgentCtx):
    """
    Prepares a tool that looks for information on the internet with a query.
    """

    search_tool = TavilySearch(max_results=5)

    def perform_web_search(query: str) -> str:
        """
        Looks for information on the internet.
        """
        output = search_tool.invoke(query)

        json_output = json.dumps(
            output,
            sort_keys=True,
            indent=4,
            separators=(',', ': '),
        )

        return str(json_output)

    return perform_web_search


@register_tool_factory(tool_id='request_external_information')
def prepare_request_external_info_tool(ctx: AgentCtx):
    """
    Prepares a tool that requests external information from the research agent.
    """

    def request_external_information(query: str) -> str:
        """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""
        return ctx.manager.invoke_agent(ctx.manager.get_agent_dict()["research_agent"], query, ctx.db)
    
    return request_external_information