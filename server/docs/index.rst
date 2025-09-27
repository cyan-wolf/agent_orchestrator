.. Agent Orchestrator documentation master file, created by
   sphinx-quickstart on Sun Sep 21 10:36:36 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Agent Orchestrator documentation
================================

System documentation for the Agent Orchestrator Server. Packages usually contain the following modules:

- schemas.py
   * Holds all the Pydantic model classes (schemas) used for validating the data integrity of the data types.
   * The schemas are used for interfacing with FastAPI as DTOs.
- tables.py
   * Holds all the ORM table classes used for storing application data. 
   * The table classes usually correspond exactly to the schemas classes.
   * This module must be "side-effect" imported in :py:attr:`main.py` to load the module before the database engine loads its metadata. For example:

   .. code-block:: python

      # For making sure the database is setup.
      from database.database import Base, engine

      # Side-effect import all the tables to make sure they are loaded.
      import auth.tables as _ # only the auth tables here as an example

      # Create the metadata on the engine.
      Base.metadata.create_all(bind=engine)

- router.py
   * Defines the FastAPI endpoints on a local :py:class:`fastapi.routing.APIRouter` API router conventionally called :py:attr:`router`. 
   * The local router must be exported and included into the main router that is created in :py:attr:`main.py`. For example: 

   .. code-block:: python

      # auth/router.py
      from fastapi.routing import APIRouter
      router = APIRouter()

   .. code-block:: python

      # main.py
      from fastapi import FastAPI
      from auth.router import router as auth_router
      app = FastAPI()
      app.include_router(auth_router)

   * Routes should be one-line functions that merely call an associated service function defined in :py:attr:`services.py`.

- services.py
   * This type of module should be composed entirely of public functions that are called by an associated route in :py:attr:`routes.py`.
   * Uses "lower-level" APIs defined in the module with the same name as the package.

- module_with_same_name_as_package.py
   * This module has the same name as its package, for example the :py:mod:`auth.auth` or :py:mod:`chat.chat` modules.
   * This module defines the functions for implementing the business logic associated the package and for basic Create-Read-Update-Delete (CRUD) operations. 

.. toctree::
   :maxdepth: 3
   :caption: Table of Contents:

   ai_module_docs/modules
   auth_module_docs/modules
   chat_module_docs/modules
   database_module_docs/modules
   user_settings_module_docs/modules