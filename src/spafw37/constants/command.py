"""Command definition constants.

These constants are used as keys in command definition dictionaries
to specify command properties such as name, action, required parameters,
sequencing constraints, and execution phase.
"""

# Command Definitions
COMMAND_NAME = "command-name"  # Used on the CLI to queue the command
COMMAND_REQUIRED_PARAMS = "required-params"  # List of param bind names that are required for this command
COMMAND_DESCRIPTION = "description"  # Description of the command
COMMAND_HELP = "command-help"  # Extended help text for the command
COMMAND_ACTION = "function"  # Function to call when the command is run
COMMAND_GOES_BEFORE = "sequence-before"  # List of command names that will be sequenced before this in a queue - user queued
COMMAND_GOES_AFTER = "sequence-after"  # List of command names that will be sequenced after this in a queue - user queued
COMMAND_REQUIRE_BEFORE = "require-before"  # List of command names that must be completed before this in a queue - automatically queued if this command is invoked
COMMAND_NEXT_COMMANDS = "next-commands"  # List of command names that will be automatically queued after this command is run
COMMAND_TRIGGER_PARAM = "trigger-param"  # Param bind name that triggers this command when set
COMMAND_PHASE = "command-phase"  # Phase in which this command should be run
COMMAND_FRAMEWORK = "framework"  # True if this is a framework-defined command (vs app-defined)
COMMAND_EXCLUDE_FROM_HELP = "exclude-from-help"  # True if this command should be excluded from help displays
