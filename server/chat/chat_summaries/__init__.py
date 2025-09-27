"""
This package defines the ORM table class for the chat summaries and the functions for reading and handling them. 
In contrast to other entities in the application, the chat summaries do not have a schema associated with their ORM table versions. 
Rather, the ORM tables are read into a Python :py:class:`collections.defaultdict` which holds agent names as keys and 
the associated summary contents as the values. 
"""