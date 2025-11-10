# Configures configuration parameters for the application
from spafw37 import logging
from .config import (
    load_persistent_config,
    save_persistent_config,
    load_user_config, 
    save_user_config, 
    set_config_file, 
    set_default_run_level,
    RUN_LEVEL_INIT,
    RUN_LEVEL_CONFIG as RUN_LEVEL_CONFIG_NAME,
    RUN_LEVEL_EXEC,
    RUN_LEVEL_CLEANUP
)
from .param import add_params, add_run_level, add_pre_parse_args
from .cli import add_post_parse_actions, add_pre_parse_actions
from .command import add_commands
from .help import show_help_command
from .config_consts import (
    COMMAND_EXCLUDE_FROM_HELP,
    COMMAND_TRIGGER_PARAM,
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
HELP_PARAM = 'help'

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
    },
    {
        PARAM_NAME: HELP_PARAM,
        PARAM_DESCRIPTION: 'Display help information',
        PARAM_BIND_TO: 'help',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--help', '-h'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_GROUP: 'General Options',
        PARAM_RUN_LEVEL: RUN_LEVEL_INIT
    }
]

_commands_builtin = [
    {
        COMMAND_NAME: "help",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "Display help information",
        COMMAND_ACTION: show_help_command,
        COMMAND_TRIGGER_PARAM: HELP_PARAM,
        COMMAND_RUN_LEVEL: RUN_LEVEL_INIT,
        COMMAND_FRAMEWORK: True,
        COMMAND_EXCLUDE_FROM_HELP: True
    },
    {
        COMMAND_NAME: "save-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_OUTFILE_PARAM ],
        COMMAND_TRIGGER_PARAM: CONFIG_OUTFILE_PARAM,
        COMMAND_RUN_LEVEL: RUN_LEVEL_CONFIG_NAME,
        COMMAND_DESCRIPTION: "Saves the current user configuration to a file",
        COMMAND_ACTION: save_user_config,
        COMMAND_FRAMEWORK: True,
        COMMAND_EXCLUDE_FROM_HELP: True
    },
    {
        COMMAND_NAME: "load-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_INFILE_PARAM ],
        COMMAND_TRIGGER_PARAM: CONFIG_INFILE_PARAM,
        COMMAND_RUN_LEVEL: RUN_LEVEL_CONFIG_NAME,
        COMMAND_DESCRIPTION: "Loads user configuration from a file",
        COMMAND_ACTION: load_user_config,
        COMMAND_FRAMEWORK: True,
        COMMAND_EXCLUDE_FROM_HELP: True
    }
]

add_params(_params_builtin)
add_params(logging.LOGGING_PARAMS)
add_commands(_commands_builtin)
add_pre_parse_actions([load_persistent_config])
add_post_parse_actions([save_persistent_config])

# Define run-levels for different execution phases
# init: sets up logging, determines output verbosity/silent, log levels, etc
add_run_level({
    RUN_LEVEL_NAME: RUN_LEVEL_INIT,
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {
        logging.LOG_SILENT_PARAM: True
    }
})

# config: loads/saves configuration in external files
add_run_level({
    RUN_LEVEL_NAME: RUN_LEVEL_CONFIG_NAME,
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# exec: executes the bulk of application commands (DEFAULT)
add_run_level({
    RUN_LEVEL_NAME: RUN_LEVEL_EXEC,
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# cleanup: does any cleanup tasks
add_run_level({
    RUN_LEVEL_NAME: RUN_LEVEL_CLEANUP,
    RUN_LEVEL_PARAMS: [],
    RUN_LEVEL_COMMANDS: [],
    RUN_LEVEL_CONFIG: {}
})

# Set the default run-level
set_default_run_level(RUN_LEVEL_EXEC)

# Register pre-parse arguments (params to parse before main CLI parsing)
add_pre_parse_args([
    logging.LOG_VERBOSE_PARAM,
    logging.LOG_TRACE_PARAM,
    logging.LOG_TRACE_CONSOLE_PARAM,
    logging.LOG_SILENT_PARAM,
    logging.LOG_NO_LOGGING_PARAM,
    logging.LOG_SUPPRESS_ERRORS_PARAM,
    logging.LOG_DIR_PARAM,
    logging.LOG_LEVEL_PARAM,
    logging.LOG_PHASE_LOG_LEVEL_PARAM
])
