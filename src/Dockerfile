FROM debian:stable-slim

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git openssh-client
RUN apt-get install -y wget curl lynx html-xml-utils
RUN python3 -m venv /venv
RUN useradd -m $USERNAME
