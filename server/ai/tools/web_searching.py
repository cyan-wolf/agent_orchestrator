from langchain_tavily import TavilySearch
from ai.tracing import trace

import json

def prepare_web_search_tool(agent_manager):
    search_tool = TavilySearch(max_results=5)

    @trace(agent_manager.tracer)
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
