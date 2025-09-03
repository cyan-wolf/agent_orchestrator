#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Building Frontend ---"
cd client
cd agent-orchestrator-client
npm install
npm run build
cd ..
cd ..

echo "--- Building Backend ---"
cd server
uv sync