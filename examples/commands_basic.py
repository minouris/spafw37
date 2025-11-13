"""Basic Commands Example - Simple command execution.

This example shows:
- Defining commands
- Command actions
- Basic command execution
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Command action functions

def hello_command():
    """Simple hello command."""
    print("Hello from the command!")
    print("This is a basic command action.")

def greet_command():
    """Greeting command."""
    print("Welcome to spafw37!")
    print("Commands are executed by the framework.")
    print("You can define any actions you need.")

def goodbye_command():
    """Farewell command."""
    print("Thanks for using spafw37!")
    print("Goodbye!")

# Define commands
commands = [
    {
        COMMAND_NAME: 'hello',
        COMMAND_DESCRIPTION: 'Say hello',
        COMMAND_ACTION: hello_command,
    },
    {
        COMMAND_NAME: 'greet',
        COMMAND_DESCRIPTION: 'Display welcome message',
        COMMAND_ACTION: greet_command,
    },
    {
        COMMAND_NAME: 'goodbye',
        COMMAND_DESCRIPTION: 'Say goodbye',
        COMMAND_ACTION: goodbye_command,
    },
]

# Register commands
spafw37.add_commands(commands)
spafw37.set_app_name('commands-basic-demo')

if __name__ == '__main__':
    spafw37.run_cli()
