"""
This package contains the classes relating to agent managers. In the server, agent managers are held 
in an in-memory store :py:class:`ai.agent_manager.agent_manager_store.AgentMangerInMemoryStore`. The entire codebase 
only accepts types that implement the :py:class:`ai.agent_manager.agent_manager_interface.IAgentManager` protocol. This protocol 
defines a public API for accessing and interacting with the various agents.
"""