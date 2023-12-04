#!/bin/bash
set -e

# Set the path to your Python script
PYTHON_SCRIPT_PATH="src/main.py"

# Set your username
USERNAME="joe"

echo "Starting run_in_container.sh"

# Configure Git
git config --global user.name 'joe'
git config --global user.email 'knarbmakes@gmail.com'

# Ensure the .ssh directory exists with correct permissions
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/known_hosts

# Manually append GitHub's known host key
ssh-keyscan github.com >> ~/.ssh/known_hosts

# Clone the repo if it doesn't exist, or pull if it does
if [ ! -d './joe-sim-ai' ]; then
  git clone git@github.com:knarbmakes/joe-sim-ai.git ./joe-sim-ai
else
  cd ./joe-sim-ai && git pull
fi

# Now move the .env file to the correct location
if [ ! -f ./joe-sim-ai/src/.env ]; then
  cp /home/$USERNAME/tmp/.env ./joe-sim-ai/src/.env
  chown $USERNAME:$USERNAME ./joe-sim-ai/src/.env
fi

# Source the virtual environment
source /venv/bin/activate

# Install dependencies
pip install -r joe-sim-ai/src/requirements.txt

# Signal that setup is complete but keep it running.
touch /tmp/setup_complete
tail -f /dev/null