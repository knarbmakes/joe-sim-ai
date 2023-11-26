#!/bin/bash

# Set the path to your Python script
PYTHON_SCRIPT_PATH="src/main.py"

# Docker image name
IMAGE_NAME="joe-sim-sandbox"

# Set your username
USERNAME="joe"

# Path to your specific SSH key on the host machine
SSH_KEY_PATH="$HOME/.ssh/id_ed25519_knarb"

# Path to the public key on the host machine (for adding to known_hosts)
SSH_PUB_KEY_PATH="$HOME/.ssh/id_ed25519_knarb.pub"

# Path to the .env file on the host machine
ENV_FILE_PATH="$PWD/src/.env"

# Check if the Docker image already exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  # Build the Docker image with user creation
  docker build -t $IMAGE_NAME -f- . <<EOF
FROM maniator/gh
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git openssh-client
RUN python3 -m venv /venv
RUN useradd -m $USERNAME
EOF
fi

# Run the Docker container with the specific SSH key and .env file mounted
docker run -it \
  -v $SSH_KEY_PATH:/home/$USERNAME/.ssh/id_ed25519_knarb \
  -v $SSH_PUB_KEY_PATH:/home/$USERNAME/.ssh/id_ed25519_knarb.pub \
  -v $ENV_FILE_PATH:/home/$USERNAME/tmp/.env \
  -v $HOME/.ssh/config_docker:/home/$USERNAME/.ssh/config \
  -w "/home/$USERNAME" \
  $IMAGE_NAME \
  /bin/bash -c "\
    . /venv/bin/activate && \
    # Setup Git and SSH
    git config --global user.name 'joe' && \
    git config --global user.email 'knarbmakes@gmail.com' && \
    ssh-keyscan github.com >> /home/$USERNAME/.ssh/known_hosts && \
    chmod 600 /home/$USERNAME/.ssh/id_ed25519_knarb && \
    chown $USERNAME:$USERNAME /home/$USERNAME/.ssh/id_ed25519_knarb && \
    chown $USERNAME:$USERNAME /home/$USERNAME/.ssh/id_ed25519_knarb.pub && \
    eval \$(ssh-agent -s) && \
    ssh-add /home/$USERNAME/.ssh/id_ed25519_knarb && \
    # Clone the repo if it doesn't exist, or pull if it does
    if [ ! -d './joe-sim-ai' ]; then
      git clone git@github.com:knarbmakes/joe-sim-ai.git ./joe-sim-ai
    else
      cd ./joe-sim-ai && git pull
    fi && \
    # Now move the .env file to the correct location
    cp /home/$USERNAME/tmp/.env ./joe-sim-ai/src/.env && \
    chown $USERNAME:$USERNAME ./joe-sim-ai/src/.env && \
    # Install dependencies
    pip install -r joe-sim-ai/src/requirements.txt && \
    # Run your script
    python joe-sim-ai/$PYTHON_SCRIPT_PATH"
