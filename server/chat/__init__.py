"""
This package defines the functions, methods, classes, and routes for working with chats. Conceptually, a chat:

- Has an owner, which is the user who created the chat.
- Has an associated agent manager, which in turn holds a reference to the :py:class:`ai.tracing.tracer.Tracer` object associated to the chat.
- Has several agent chat summaries. A chat summary is a summary of a chat written by an AI agent for remembering the contents of a chat. 
- A chat's associated tracer object holds all the traces (chat messages and logs) for the chat. 
"""