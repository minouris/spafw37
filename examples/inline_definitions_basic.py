"""Basic Inline Definitions Example - Define objects where you use them.

This example demonstrates:
- Inline parameter definitions in COMMAND_REQUIRED_PARAMS
- Inline parameter definitions in COMMAND_TRIGGER_PARAM
- Inline command definitions in dependency fields
- Benefits of inline definitions for quick prototyping
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_TRIGGER_PARAM,
    COMMAND_REQUIRE_BEFORE,
    COMMAND_NEXT_COMMANDS,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_TOGGLE,
    PARAM_ALIASES,
)


# Example 1: Inline parameters in COMMAND_REQUIRED_PARAMS
# Instead of separately defining and registering parameters,
# you can define them directly in the command

commands = [
    {
        COMMAND_NAME: "greet",
        COMMAND_DESCRIPTION: "Greet a user by name",
        COMMAND_ACTION: lambda: spafw37.output(
            f"Hello, {spafw37.get_param('user-name')}!"
        ),
        # Define the required parameter inline - no separate add_param() needed!
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "user-name",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                PARAM_ALIASES: ["--name", "-n"],
            }
        ]
    },
    
    # Example 2: Inline parameter in COMMAND_TRIGGER_PARAM
    # Commands can be triggered automatically when a parameter is set
    {
        COMMAND_NAME: "auto-greet",
        COMMAND_DESCRIPTION: "Automatically greet when --auto flag is set",
        COMMAND_ACTION: lambda: spafw37.output("Auto-greeting enabled!"),
        # The trigger parameter is defined inline
        COMMAND_TRIGGER_PARAM: {
            PARAM_NAME: "auto-greet-flag",
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ["--auto"],
        }
    },
    
    # Example 3: Inline commands in COMMAND_REQUIRE_BEFORE
    # Define prerequisite commands inline
    {
        COMMAND_NAME: "deploy",
        COMMAND_DESCRIPTION: "Deploy the application",
        COMMAND_ACTION: lambda: spafw37.output("Deploying application..."),
        # This command requires validation to run first
        # We define the validation command inline!
        COMMAND_REQUIRE_BEFORE: [
            {
                COMMAND_NAME: "validate",
                COMMAND_DESCRIPTION: "Validate configuration",
                COMMAND_ACTION: lambda: spafw37.output("Validating configuration...")
            }
        ]
    },
    
    # Example 4: Inline commands in COMMAND_NEXT_COMMANDS
    # Define follow-up commands inline
    {
        COMMAND_NAME: "build",
        COMMAND_DESCRIPTION: "Build the project",
        COMMAND_ACTION: lambda: spafw37.output("Building project..."),
        # After building, automatically run tests
        COMMAND_NEXT_COMMANDS: [
            {
                COMMAND_NAME: "test",
                COMMAND_DESCRIPTION: "Run tests",
                COMMAND_ACTION: lambda: spafw37.output("Running tests...")
            }
        ]
    }
]

# Register commands - inline definitions are automatically registered!
spafw37.add_commands(commands)
spafw37.set_app_name('inline-definitions-basic')

if __name__ == '__main__':
    spafw37.run_cli()
