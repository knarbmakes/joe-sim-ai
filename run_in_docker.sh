#!/bin/bash

# Set the path to your Python script relative to the source code directory
PYTHON_SCRIPT_PATH="main.py"
SOURCE_CODE_DIR="src"

# Docker image name
IMAGE_NAME="joe-sim-sandbox"

# Check if the Docker image already exists
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
  # Build the Docker image
  docker build -t $IMAGE_NAME -f- . <<EOF
FROM debian:stable-slim
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv
RUN python3 -m venv /venv
COPY $SOURCE_CODE_DIR /src
RUN . /venv/bin/activate && pip install -r /src/requirements.txt
EOF
fi

# Run the Docker container
docker run -it -w "/src" $IMAGE_NAME /bin/bash -c ". /venv/bin/activate && python $PYTHON_SCRIPT_PATH"
