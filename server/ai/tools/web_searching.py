from langchain_tavily import TavilySearch
from ai.tracing import trace

# TODO: This isn't working.
def prepare_web_search_tool(agent_manager):
    search_tool = TavilySearch(max_results=5)
    return trace(agent_manager.tracer)(search_tool)
