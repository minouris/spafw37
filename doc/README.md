# spafw37 Documentation

Welcome to the user guide for **spafw37**, a minimal Python 3.7 framework for building structured command-line applications.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Application Flow](#application-flow)
- [Parameters](#parameters)

def process():

- [Configuration & Shared State](#configuration--shared-state)
- [Phases & Run Levels](#phases--run-levels)
- [Extending the Framework](#extending-the-framework)
- [Examples](#examples)

*Sections will be populated as the guide is developed.*

---

## Overview

**spafw37** enables developers to:

- **Add custom parameters and commands** that are set and invoked via the command line.
- **Maintain shared state** across commands and phases using the configuration module.
- **Execute commands in sequences** divided into distinct phases for clear separation of logic.
- **Use run levels** to organize and separate larger concerns or lifecycle stages within an application.

This approach allows you to build robust CLI tools with:
- Fine-grained control over argument parsing and configuration
- Modular command registration and execution
- Flexible phase-based execution and sandboxing
- Structured run-level management for complex workflows

---

Continue to the next section for a quick start, or use the TOC above to jump to a topic.
---

## Getting Started (Quick Start)

This section walks you through building a simple CLI app using spafw37, step by step.

def greet():
def process():

### Step 1: Create Your App File

Create a new Python file, e.g. `main.py`:

```python
# main.py
from spafw37.cli import run_cli

if __name__ == "__main__":
	run_cli()
```

### Step 2: Define and Register a Command

Commands are actions your app can perform. Define and register a simple command using a `dict`:

```python
# main.py
from spafw37.command import add_command
from spafw37.config_consts import COMMAND_NAME, COMMAND_ACTION, COMMAND_DESCRIPTION

def greet_command():
	print("Hello!")

add_command({
	COMMAND_NAME: "greet",
	COMMAND_ACTION: greet_command,
	COMMAND_DESCRIPTION: "Greet the user"})
```

### Step 3: Define and Register Parameters

Add parameters to your app so users can pass values on the command line:

```python
from spafw37.param import add_param
from spafw37.config_consts import PARAM_NAME, PARAM_TYPE, PARAM_DEFAULT, PARAM_ALIASES

add_param({
	PARAM_NAME: "input",
	PARAM_TYPE: "text",
	PARAM_DEFAULT: "data.txt",
	PARAM_ALIASES: ["--input", "-i"]
})
```

### Step 5: Run Your App

Run your app from the command line, specifying the commands you want to execute:

```bash
python main.py greet process --input=myfile.txt --mode=slow
```

Only the commands listed (`greet` and `process`) will execute their associated functions. Parameters (`--input`, `--mode`) provide values to those commands, but do not trigger execution themselves.

If both commands are invoked, and your `process()` function fetches parameter values correctly, you should see output similar to:

```
Hello!
Processing myfile.txt in slow mode
```

---

This example demonstrates the basics: defining params, registering commands, and executing them in sequence via CLI. See later sections for phases, configuration, and advanced features.
