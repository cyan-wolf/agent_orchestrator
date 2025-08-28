from langchain_tavily import TavilySearch
from ai.tracing import trace

import json

def prepare_web_search_tool(agent_manager):
    search_tool = TavilySearch(max_results=5)

    @trace(agent_manager)
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


def prepare_request_external_info_tool(agent_manager):
    @trace(agent_manager)
    def request_external_information(query: str) -> str:
        """Asks the research agent for help whenever external information is needed, such as external websites or the current date."""
        return agent_manager.invoke_agent(agent_manager.agents["research_agent"], query)
    
    return request_external_information