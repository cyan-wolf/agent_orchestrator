# Agent Orchestrator Server

The root directory for the server is `agent_orchestrator/server`. This is where the `uv.lock` file is, which is important 
for the `uv` tool which manages dependencies and scripts. For information on the Agent Orchestrator project as whole, read the main project [README](../README.md).

## Running the Server
The server can be run using the following command while in the `server` directory: `uv run uvicorn main:app --reload`.

## Building the documentation
The documentation for the server can be built by running the provided batch file in the `docs/` sub-directory. The 
batch file can be run from the `server` directory using the following command: `./docs/build_docs.bat`. This builds the documentation 
into an HTML output. The built documentation can be viewed by opening the HTML file at this location: `./docs/_build/html/html/index.html`. 
