"""Advanced Inline Definitions Example - Complex nested scenarios.

This example demonstrates:
- Mixing inline and named references
- Nested inline definitions (params with inline switch lists)
- Inline commands with inline required params
- Real-world use cases
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_GOES_BEFORE,
    COMMAND_GOES_AFTER,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_NUMBER,
    PARAM_ALIASES,
    PARAM_SWITCH_LIST,
    PARAM_DEFAULT,
)


# Example 1: Mixing inline and pre-registered parameters
# Pre-register some common application parameters
common_params = [
    {
        PARAM_NAME: "database",
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ["--database", "--db"],
    },
    {
        PARAM_NAME: "verbose",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ["--verbose", "-v"],
    }
]

spafw37.add_params(common_params)

# Example 2: Nested inline definitions
# Toggle parameter with inline mutually exclusive toggles
verbosity_params = [
    {
        PARAM_NAME: "debug",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ["--debug", "-d"],
        # Define mutually exclusive verbosity modes inline
        # Note: PARAM_SWITCH_LIST creates bidirectional XOR relationships
        PARAM_SWITCH_LIST: [
            {
                PARAM_NAME: "quiet",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,
                PARAM_ALIASES: ["--quiet", "-q"],
            },
            {
                PARAM_NAME: "silent",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,
                PARAM_ALIASES: ["--silent"],
            }
        ]
    }
]

spafw37.add_params(verbosity_params)

# Example 3: Complex command with mixed inline and named references
commands = [
    {
        COMMAND_NAME: "process-data",
        COMMAND_DESCRIPTION: "Process data with validation and cleanup",
        COMMAND_ACTION: lambda: spafw37.output(
            f"Processing data from {spafw37.get_param('input-file')} "
            f"with {spafw37.get_param('workers')} workers..."
        ),
        # Mix named and inline required params
        COMMAND_REQUIRED_PARAMS: [
            "database",  # Named reference to pre-registered param
            {
                # Inline parameter definition
                PARAM_NAME: "input-file",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                PARAM_ALIASES: ["--input", "-i"],
            },
            {
                # Another inline parameter
                PARAM_NAME: "workers",
                PARAM_TYPE: PARAM_TYPE_NUMBER,
                PARAM_ALIASES: ["--workers", "-w"],
                PARAM_DEFAULT: 1,
            }
        ],
        # Inline prerequisite command
        COMMAND_GOES_AFTER: [
            {
                COMMAND_NAME: "setup-environment",
                COMMAND_DESCRIPTION: "Set up processing environment",
                COMMAND_ACTION: lambda: spafw37.output("Setting up environment...")
            }
        ],
        # Inline follow-up command
        COMMAND_GOES_BEFORE: [
            {
                COMMAND_NAME: "cleanup",
                COMMAND_DESCRIPTION: "Clean up temporary files",
                COMMAND_ACTION: lambda: spafw37.output("Cleaning up temporary files...")
            }
        ]
    },
    
    # Example 4: Inline command with its own inline requirements
    # This creates a full dependency chain inline
    {
        COMMAND_NAME: "deploy-production",
        COMMAND_DESCRIPTION: "Deploy to production with safety checks",
        COMMAND_ACTION: lambda: spafw37.output("Deploying to production..."),
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "deployment-target",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                PARAM_ALIASES: ["--target"],
            },
            {
                PARAM_NAME: "confirm-deploy",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,
                PARAM_ALIASES: ["--confirm"],
            }
        ],
        # Inline command that itself has inline requirements
        COMMAND_GOES_AFTER: [
            {
                COMMAND_NAME: "run-safety-checks",
                COMMAND_DESCRIPTION: "Run pre-deployment safety checks",
                COMMAND_ACTION: lambda: spafw37.output("Running safety checks..."),
                # Nested inline params for the inline command!
                COMMAND_REQUIRED_PARAMS: [
                    {
                        PARAM_NAME: "check-database",
                        PARAM_TYPE: PARAM_TYPE_TOGGLE,
                        PARAM_ALIASES: ["--check-db"],
                        PARAM_DEFAULT: True,
                    }
                ]
            }
        ]
    }
]

# Register commands
spafw37.add_commands(commands)
spafw37.set_app_name('inline-definitions-advanced')

if __name__ == '__main__':
    spafw37.run_cli()
