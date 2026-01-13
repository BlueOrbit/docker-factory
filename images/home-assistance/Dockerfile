###############################################
# BASE IMAGE
###############################################
FROM python:3.12-slim-bookworm

###############################################
# WORKING DIRECTORY
###############################################
RUN mkdir /app
WORKDIR /app

###############################################
# SYSTEM DEPENDENCIES
###############################################
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    bash \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python-is-python3 \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    autoconf \
    cmake \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

###############################################
# REPO SETUP
###############################################
RUN git clone https://github.com/home-assistant/core.git .

# Use the latest commit from the cloned repo
RUN git checkout 00381e6dfd2a1e3592953312c5c09c281a0acce0

###############################################
# PROJECT DEPENDENCIES
###############################################
# Install minimal Home Assistant core dependencies for testing
RUN pip install --no-cache-dir \
    aiohttp \
    pytest \
    pytest-asyncio \
    pytest-aiohttp \
    pytest-homeassistant-custom-component

###############################################
# ENTRYPOINT / CMD
###############################################
ENTRYPOINT ["/bin/bash"]
