# Repository: https://github.com/minouris/s4fw
#
# Project: S4FW
# Author: Ciara Norrish (@minouris)
# License: MIT (see LICENSE.md)
#
# Description: Dev container for Sims 4 Framework development

FROM ubuntu:20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git unzip zip sudo build-essential cmake libboost-all-dev tzdata jq \
    wget ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Uninstall conflicting Python versions
 RUN apt-get remove --purge python3.8 python3.8-minimal -y && sudo apt-get autoremove -y && sudo apt-get autoclean

# --- Python 3.7 build from source (fallback, slower, but guaranteed version) ---
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz && \
    tar xzf Python-3.7.0.tgz && \
    cd Python-3.7.0 && \
    ./configure --with-ensurepip=install && \
    make -j"$(nproc)" && \
    make altinstall && \
    cd / && \
    rm -rf /tmp/Python-3.7.0*

# Create symlinks for python and pip
RUN ln -s /usr/local/bin/python3.7 /usr/local/bin/python && \
    ln -s /usr/local/bin/python3.7 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/pip3.7 /usr/local/bin/pip

# Set fallback timezone (will be overridden by host mount if available)
ENV TZ=UTC

# Create a non-root user 'pythondev' with home directory
RUN useradd -ms /bin/bash pythondev
RUN mkdir -p /workspaces/spafw37
RUN echo "pythondev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to the new user
USER pythondev

# Set the working directory for the new user
WORKDIR /workspaces/spafw37