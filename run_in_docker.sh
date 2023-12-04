#!/bin/bash

# Export the necessary environment variables
export ENV_FILE_PATH="$PWD/src/.env"
export STARTUP_SCRIPT="$PWD/src/run_in_container.sh"
export STARTUP_SCRIPT_2="$PWD/src/run_app.sh"
export MEMORY_PATH="$PWD/memory"
export DOWNLOADS_PATH="$PWD/downloads"
export USERNAME="joe"

# Start Docker Compose services in detached mode
docker-compose up -d --build

# Wait for the setup script to finish
docker-compose exec -T app bash -c "while [ ! -f /tmp/setup_complete ]; do sleep 1; done"

# Execute the second startup script in the 'app' service's container
docker-compose exec -T app bash -c "./run_app.sh"
