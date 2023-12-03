#!/bin/bash

# Set the path to your Python script
PYTHON_SCRIPT_PATH="src/main.py"

# Set your username
USERNAME="joe"

# Setup Git and SSH
git config --global user.name 'joe'
git config --global user.email 'knarbmakes@gmail.com'
ssh-keyscan github.com >> /home/$USERNAME/.ssh/known_hosts
chmod 600 /home/$USERNAME/.ssh/id_ed25519_knarb
chown $USERNAME:$USERNAME /home/$USERNAME/.ssh/id_ed25519_knarb
chown $USERNAME:$USERNAME /home/$USERNAME/.ssh/id_ed25519_knarb.pub
eval $(ssh-agent -s)
ssh-add /home/$USERNAME/.ssh/id_ed25519_knarb

# Clone the repo if it doesn't exist, or pull if it does
if [ ! -d './joe-sim-ai' ]; then
  git clone git@github.com:knarbmakes/joe-sim-ai.git ./joe-sim-ai
else
  cd ./joe-sim-ai && git pull
fi

# Now move the .env file to the correct location
cp /home/$USERNAME/tmp/.env ./joe-sim-ai/src/.env
chown $USERNAME:$USERNAME ./joe-sim-ai/src/.env

# Install dependencies
pip install -r joe-sim-ai/src/requirements.txt

# Run your script
python joe-sim-ai/$PYTHON_SCRIPT_PATH
