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
echo "--- Finished Building Frontend ---"

echo "--- Building Backend ---"
cd server
# Call `uv` using its location in Render's environment.
/home/render/envwrappers/uv sync
echo "--- Finished Building Backend ---"