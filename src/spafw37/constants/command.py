"""Command definition constants.

These constants are used as keys in command definition dictionaries
to specify command properties such as name, action, required parameters,
sequencing constraints, and execution phase.

Example of a fully constructed command definition:

    {
        COMMAND_NAME: "build",
        COMMAND_DESCRIPTION: "Build the project",
        COMMAND_HELP: "Builds the project by compiling source files and creating artifacts.",
        COMMAND_ACTION: build_project_function,
        COMMAND_REQUIRED_PARAMS: ["source-dir", "output-dir"],
        COMMAND_GOES_BEFORE: ["deploy"],
        COMMAND_GOES_AFTER: ["clean"],
        COMMAND_REQUIRE_BEFORE: ["configure"],
        COMMAND_NEXT_COMMANDS: ["test"],
        COMMAND_TRIGGER_PARAM: "auto-build",
        COMMAND_PHASE: "build",
        COMMAND_FRAMEWORK: False,
        COMMAND_EXCLUDE_HELP: False,
        COMMAND_CYCLE: None,
        COMMAND_INVOCABLE: True
    }

Minimum viable command:

    {
        COMMAND_NAME: "world",
        COMMAND_DESCRIPTION: "Prints Hello, World!",
        COMMAND_ACTION: lambda: print("Hello, World!")
    }

"""

COMMAND_NAME = "command-name"                   # Used on the CLI to queue the command
COMMAND_REQUIRED_PARAMS = "required-params"     # List of param bind names that are required for this command
COMMAND_DESCRIPTION = "description"             # Description of the command
COMMAND_HELP = "command-help"                   # Extended help text for the command
COMMAND_ACTION = "function"                     # Function to call when the command is run
COMMAND_GOES_BEFORE = "sequence-before"         # List of command names that will be sequenced before this in a queue - user queued
COMMAND_GOES_AFTER = "sequence-after"           # List of command names that will be sequenced after this in a queue - user queued
COMMAND_REQUIRE_BEFORE = "require-before"       # List of command names that must be completed before this in a queue - automatically queued if this command is invoked
COMMAND_NEXT_COMMANDS = "next-commands"         # List of command names that will be automatically queued after this command is run
COMMAND_TRIGGER_PARAM = "trigger-param"         # Param bind name that triggers this command when set
COMMAND_PHASE = "command-phase"                 # Phase in which this command should be run
COMMAND_FRAMEWORK = "framework"                 # True if this is a framework-defined command (vs app-defined)
COMMAND_EXCLUDE_HELP = "exclude-from-help"      # True if this command should be excluded from help displays
COMMAND_CYCLE = "command-cycle"                 # Attaches a cycle to a command, from the command side
COMMAND_INVOCABLE = "command-invocable"         # Marks a command as invocable by a param-trigger, or a CLI command. Default true for 
                                                # regular commands, false for cycle-internal commands. Should not be shown in help, except as
                                                # a child of a cycle command, but command help text will be shown as part of the help for the 
                                                # parent command.

