from langchain_tavily import TavilySearch
from ai.tracing import trace
from ai.agent_context import AgentContext

import json

def prepare_web_search_tool(ctx: AgentContext):
    search_tool = TavilySearch(max_results=5)

    @trace(ctx)
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


def prepare_request_external_info_tool(ctx: AgentContext):
    @trace(ctx)
    def request_external_information(query: str) -> str:
        """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""
        return ctx.invoke_agent(ctx.get_agent_dict()["research_agent"], query)
    
    return request_external_information