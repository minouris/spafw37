# Configures configuration parameters for the application
from spafw37 import logging
from spafw37 import config_func
from spafw37 import config
from spafw37 import param
from spafw37 import cli
from spafw37 import command
from spafw37 import help as help_module
from spafw37.constants.param import (
    PARAM_GROUP,
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_CONFIG_NAME,
    PARAM_TYPE,
    PARAM_ALIASES,
    PARAM_REQUIRED,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_NEVER,
    PARAM_TYPE_TEXT,
)
from spafw37.constants.command import (
    COMMAND_EXCLUDE_HELP,
    COMMAND_TRIGGER_PARAM,
    COMMAND_NAME,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_FRAMEWORK,
    COMMAND_PHASE,
)
from spafw37.constants.config import (
    CONFIG_INFILE_PARAM,
    CONFIG_OUTFILE_PARAM,
)
from spafw37.constants.phase import (
    PHASE_SETUP,
    PHASE_TEARDOWN,
)

CONFIG_FILE_PARAM_GROUP = "Configuration File Options"
HELP_PARAM = 'help'

_params_builtin = [
    {
        PARAM_NAME: CONFIG_INFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file containing configuration to load',
        PARAM_CONFIG_NAME: CONFIG_INFILE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--load-config', '-l'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_GROUP: CONFIG_FILE_PARAM_GROUP
    },
    {
        PARAM_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file to save configuration to',
        PARAM_CONFIG_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--save-config', '-s'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_GROUP: CONFIG_FILE_PARAM_GROUP
    },
    {
        PARAM_NAME: HELP_PARAM,
        PARAM_DESCRIPTION: 'Display help information',
        PARAM_CONFIG_NAME: 'help',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--help', '-h'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_GROUP: 'General Options'
    }
]

_commands_builtin = [
    {
        COMMAND_NAME: "help",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "Display help information",
        COMMAND_ACTION: help_module.show_help_command,
        COMMAND_TRIGGER_PARAM: HELP_PARAM,
        COMMAND_FRAMEWORK: True,
        COMMAND_EXCLUDE_HELP: True,
        COMMAND_PHASE: PHASE_SETUP
    },
    {
        COMMAND_NAME: "save-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_OUTFILE_PARAM ],
        COMMAND_TRIGGER_PARAM: CONFIG_OUTFILE_PARAM,
        COMMAND_DESCRIPTION: "Saves the current user configuration to a file",
        COMMAND_ACTION: config_func.save_user_config,
        COMMAND_FRAMEWORK: True,
        COMMAND_EXCLUDE_HELP: True,
        COMMAND_PHASE: PHASE_TEARDOWN
    },
    {
        COMMAND_NAME: "load-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_INFILE_PARAM ],
        COMMAND_TRIGGER_PARAM: CONFIG_INFILE_PARAM,
        COMMAND_DESCRIPTION: "Loads user configuration from a file",
        COMMAND_ACTION: config_func.load_user_config,
        COMMAND_FRAMEWORK: True,
        COMMAND_EXCLUDE_HELP: True,
        COMMAND_PHASE: PHASE_SETUP
    }
]

param.add_params(_params_builtin)
param.add_params(logging.LOGGING_PARAMS)
command.add_commands(_commands_builtin)
command.set_phases_order(config.get_phases_order())
cli.add_pre_parse_actions([config_func.load_persistent_config])
cli.add_post_parse_actions([config_func.save_persistent_config])

# Register pre-parse arguments (params to parse before main CLI parsing)
param.add_pre_parse_args([
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
