# Agent Orchestrator
This is a multi-agent orchestration framework. The system is managed by a supervisor agent that hands off control to other agent based on the user's needs. The system provides some pre-built agents, but the user can add more.

# Usage
The app can be tested out by visiting the [public URL](https://agent-orchestrator-jb9i.onrender.com/) or can be built and ran locally. 

# Installation
## Backend
The backend uses Python and is ran using the `uv` package manager. It can be installed with `pip`:
```bash
pip install uv
```
or it can be installed as a standalone binary over at uv's [official installation page](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer). 

Once installated, the installation can be checked with the `uv --version` command. 

If `uv` is successfully installed, then the server can be started with the following commands:
```bash
cd server
uv run uvicorn main:app
```

## Frontend
The frontend uses React and MUI and can be built using `npm`.

See [this](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) for instructions on how to install `npm`.

The frontend can be built using the following commands:
```bash
cd client\agent-orchestrator-client
npm run dev
```

# Agents
The app is built on the idea of agent templates. When a user creates a new chat, agents are loaded from the user's agent templates. All users have the following agent templates by default:
- supervisor agent
- coding agent
- math agent
- creator agent
- planner agent
- research agent

Users can add new agent templates by specifying the name, persona, purpose, and tools that the agent will use.

# Tools
## Backend
* FastAPI
* Uvicorn
* Pydantic
* SQLAlchemy
* Sphinx
* LangChain
* LangGraph

## Frontend
* React
* MUI
* Vite

# Documentation
The backend documentation can be found [here](https://cyan-wolf.github.io/agent_orchestrator/index.html).
