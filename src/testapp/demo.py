"""
Enhanced test application demonstrating help/usage features.
"""
from spafw37.config import set_config_file
from spafw37.param import add_params
from spafw37.command import add_commands

from spafw37.config_consts import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_GROUP,
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_HELP,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
)

set_config_file('demo_config.json')


def build_action():
    """Build the project."""
    print("Building project...")


def test_action():
    """Run tests."""
    print("Running tests...")


def deploy_action():
    """Deploy the project."""
    print("Deploying project...")


# Define parameters with groups
demo_params = [
    {
        PARAM_NAME: "input-file",
        PARAM_DESCRIPTION: "Input file to process",
        PARAM_ALIASES: ["--input", "-i"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_GROUP: "Input/Output Options"
    },
    {
        PARAM_NAME: "output-dir",
        PARAM_DESCRIPTION: "Output directory for results",
        PARAM_ALIASES: ["--output", "-o"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_GROUP: "Input/Output Options"
    },
    {
        PARAM_NAME: "verbose",
        PARAM_DESCRIPTION: "Enable verbose output",
        PARAM_ALIASES: ["--verbose", "-v"],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_GROUP: "General Options"
    },
    {
        PARAM_NAME: "debug",
        PARAM_DESCRIPTION: "Enable debug mode",
        PARAM_ALIASES: ["--debug", "-d"],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_GROUP: "General Options"
    },
    {
        PARAM_NAME: "threads",
        PARAM_DESCRIPTION: "Number of threads to use",
        PARAM_ALIASES: ["--threads", "-t"],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_GROUP: "Performance Options"
    },
    {
        PARAM_NAME: "build-type",
        PARAM_DESCRIPTION: "Type of build (debug/release)",
        PARAM_ALIASES: ["--build-type", "-bt"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
    {
        PARAM_NAME: "target",
        PARAM_DESCRIPTION: "Build target platform",
        PARAM_ALIASES: ["--target"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
    {
        PARAM_NAME: "test-pattern",
        PARAM_DESCRIPTION: "Pattern for test files",
        PARAM_ALIASES: ["--test-pattern", "-tp"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
]

# Define commands with extended help
demo_commands = [
    {
        COMMAND_NAME: "build",
        COMMAND_DESCRIPTION: "Build the project",
        COMMAND_HELP: """
This command builds the project using the specified configuration.

The build process will:
  1. Compile all source files
  2. Link dependencies
  3. Generate output in the specified directory

Build types:
  - debug: Includes debug symbols and assertions
  - release: Optimized build for production
        """.strip(),
        COMMAND_ACTION: build_action,
        COMMAND_REQUIRED_PARAMS: ["build-type", "target"]
    },
    {
        COMMAND_NAME: "test",
        COMMAND_DESCRIPTION: "Run project tests",
        COMMAND_HELP: """
Run the project's test suite.

This will execute all tests matching the test pattern.
Use --verbose to see detailed test output.
        """.strip(),
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: ["test-pattern"]
    },
    {
        COMMAND_NAME: "deploy",
        COMMAND_DESCRIPTION: "Deploy the built project",
        COMMAND_HELP: "Deploy the project to the target environment.",
        COMMAND_ACTION: deploy_action,
        COMMAND_REQUIRED_PARAMS: []
    }
]

# Register params and commands
add_params(demo_params)
add_commands(demo_commands)

if __name__ == "__main__":
    from spafw37 import core
    core.run_cli()