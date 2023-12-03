#!/bin/bash

# Export the necessary environment variables
export SSH_KEY_PATH="$HOME/.ssh/id_ed25519_knarb"
export SSH_PUB_KEY_PATH="$HOME/.ssh/id_ed25519_knarb.pub"
export ENV_FILE_PATH="$PWD/src/.env"
export MEMORY_PATH="$PWD/memory"
export DOWNLOADS_PATH="$PWD/downloads"
export USERNAME="joe"

# Run Docker Compose
docker-compose up --build
