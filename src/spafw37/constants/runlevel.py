"""Run-level configuration constants.

These constants define run-levels, which allow segmenting the CLI parsing
and command execution into distinct phases with their own parameters,
commands, and configuration.
"""

# Run-level Definitions
RUN_LEVEL_NAME = 'run-level-name'  # Name of the run-level
RUN_LEVEL_PARAMS = 'run-level-params'  # List of param bind names that are parsed in this run level
RUN_LEVEL_COMMANDS = 'run-level-commands'  # List of commands that are parsed and executed in this run-level
RUN_LEVEL_CONFIG = 'run-level-config'  # Dictionary of config name-value pairs to set for this run-level
RUN_LEVEL_ERROR_HANDLER = 'run-level-error-handler'  # Optional custom error handler for this run-level

# Pre-defined Run-level Names
RUN_LEVEL_INIT = 'init'  # Initialize logging, verbosity, silent mode, log levels
RUN_LEVEL_CONFIG_NAME = 'config'  # Load/save configuration from external files
RUN_LEVEL_EXEC = 'exec'  # Execute the bulk of application commands (DEFAULT)
RUN_LEVEL_CLEANUP = 'cleanup'  # Cleanup tasks after main execution
