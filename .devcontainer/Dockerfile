# Repository: https://github.com/minouris/s4fw
#
# Project: SPAFW37
# Author: Ciara Norrish (@minouris)
# License: MIT (see LICENSE.md)
#
# Description: Dev container for Simple Python 3.7 Application Framework development
FROM python:3.7.9-slim-buster

# Prevent interactive prompts during package installation and set default TZ
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Buster is archived; point apt sources to the archive mirrors and disable
# the 'Valid-Until' check so apt can use older Release files.
RUN sed -i 's|deb.debian.org|archive.debian.org|g; s|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
 && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until \
 && apt-get update -o Acquire::Check-Valid-Until=false \
 && apt-get install -y --no-install-recommends \
    build-essential \
    sudo \
    tzdata \
    git \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ENV PIP_OPTIONS="--trusted-host pypi.org --trusted-host files.pythonhosted.org"

RUN python -m pip install ${PIP_OPTIONS} --upgrade pip setuptools wheel && \
    python -m pip install ${PIP_OPTIONS} "pytest==6.2.5" typing_extensions && \
    python -m pip install ${PIP_OPTIONS} "pytest-cov==2.12.1" && \
    python -m pip install ${PIP_OPTIONS} virtualenv
    
# Apply patches to the container
COPY patch /

# Set fallback timezone (will be overridden by host mount if available)
ENV TZ=UTC

# Create a non-root user 'pythondev' with home directory
RUN useradd -ms /bin/bash pythondev
RUN mkdir -p /workspaces/spafw37
RUN echo "pythondev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to the new user
USER pythondev
RUN cat >> /home/pythondev/.bashrc << 'EOF'
# Define custom prompt function
parse_git_branch() { 
    git branch 2>/dev/null | sed -e "/^[^*]/d" -e "s/* \(.*\)/[\1]/"; 
}
parse_python_version() {
    python --version 2>&1 | awk '{print $2}';
}

# Create venv if it doesn't exist
#if [ ! -d "/workspaces/spafw37/.venv" ]; then
#    python -m venv /workspaces/spafw37/.venv
#fi

# Activate venv
source /workspaces/spafw37/.venv/bin/activate

# Configure pip to trust default PyPI hosts
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org test.pypi.python.org"

export PS1="\[\033[92m\][python-\$(parse_python_version)]\[\033[00m\] \[\033[33m\]\$(parse_git_branch)\[\033[01;34m\] \w\[\033[00m\]\$ "
export PYTHONPATH="/workspaces/spafw37/src:\$PYTHONPATH"

# Display MOTD
echo -e "\n\033[92mWelcome to the SPAFW37 Development Container!\033[0m\n"
echo -e "Getting started:\n"
echo -e "📦 \033[33mInstall dependencies:\033[0m"
echo -e "   pip install -e .[dev]\n"
echo -e "🧪 \033[33mRun tests:\033[0m"
echo -e "   pytest tests/ -v --cov=spafw37 --cov-report=term-missing\n"
echo -e "🔨 \033[33mBuild package:\033[0m"
echo -e "   pip install build"
echo -e "   python -m build\n"
echo -e "📚 \033[33mDocumentation:\033[0m doc/\n"
echo -e "📚 \033[33mExamples:\033[0m examples/\n"

EOF

# Set the working directory for the new user
WORKDIR /workspaces/spafw37