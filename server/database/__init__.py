"""
This package contains the :py:mod:`database.database` module which forms the connection to the database. 
This module also exports the :py:func:`database.database.get_database` function which is used to acquire a 
:py:class:`from sqlalchemy.orm.Session` DB session. Alongside that function, the module also exports the DB engine 
:py:attr:`database.database.engine` and the base class for all ORM table classes :py:class:`database.database.Base`.
"""