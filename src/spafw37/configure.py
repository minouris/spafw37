# Configures configuration parameters for the application
from spafw37 import logging
from .config import load_persistent_config, save_persistent_config, load_user_config, save_user_config, set_config_file, set_default_run_level
from .param import add_params, add_run_level
from .cli import add_post_parse_actions, add_pre_parse_actions
from .command import add_commands
from .help import show_help_command
from .config_consts import (
    PARAM_GROUP,
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_BIND_TO,
    PARAM_TYPE,
    PARAM_ALIASES,
    PARAM_REQUIRED,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_NEVER,
    CONFIG_INFILE_PARAM,
    CONFIG_OUTFILE_PARAM,
    COMMAND_NAME,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_FRAMEWORK,
    PARAM_TYPE_TEXT,
    RUN_LEVEL_NAME,
    RUN_LEVEL_PARAMS,
    RUN_LEVEL_COMMANDS,
    RUN_LEVEL_CONFIG,
    COMMAND_RUN_LEVEL,
    PARAM_RUN_LEVEL
)

CONFIG_FILE_PARAM_GROUP = "Configuration File Options"

_params_builtin = [
    {
        PARAM_NAME: CONFIG_INFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file containing configuration to load',
        PARAM_BIND_TO: CONFIG_INFILE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--load-config', '-l'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_GROUP: CONFIG_FILE_PARAM_GROUP
    },
    {
        PARAM_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file to save configuration to',
        PARAM_BIND_TO: CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--save-config', '-s'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_GROUP: CONFIG_FILE_PARAM_GROUP
    }
]

_commands_builtin = [
    {
        COMMAND_NAME: "help",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "Display help information",
        COMMAND_ACTION: show_help_command,
        COMMAND_FRAMEWORK: True
    },
    {
        COMMAND_NAME: "save-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_OUTFILE_PARAM ],
        COMMAND_DESCRIPTION: "Saves the current user configuration to a file",
        COMMAND_ACTION: save_user_config,
        COMMAND_FRAMEWORK: True
    }
]

add_params(_params_builtin)
add_params(logging.LOGGING_PARAMS)
add_commands(_commands_builtin)
add_pre_parse_actions([load_persistent_config, load_user_config])
add_post_parse_actions([save_persistent_config, save_user_config])

# Define run-levels for different execution phases
# init: sets up logging, determines output verbosity/silent, log levels, etc
add_run_level({
    RUN_LEVEL_NAME: 'init',
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# config: loads/saves configuration in external files
add_run_level({
    RUN_LEVEL_NAME: 'config',
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# exec: executes the bulk of application commands (DEFAULT)
add_run_level({
    RUN_LEVEL_NAME: 'exec',
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# cleanup: does any cleanup tasks
add_run_level({
    RUN_LEVEL_NAME: 'cleanup',
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# Set the default run-level
set_default_run_level('exec')