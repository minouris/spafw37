# Configures configuration parameters for the application
from .config import load_persistent_config, save_persistent_config, load_user_config, save_user_config, set_config_file
from .param import add_params
from .cli import add_post_parse_actions, add_pre_parse_actions
from .command import add_commands
from .help import show_help_command
from .config_consts import (
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
    PARAM_TYPE_TEXT
)

_params_builtin = [
    {
        PARAM_NAME: CONFIG_INFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file containing configuration to load',
        PARAM_BIND_TO: CONFIG_INFILE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--load-config', '-l'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    },
    {
        PARAM_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file to save configuration to',
        PARAM_BIND_TO: CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--save-config', '-s'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
]

_commands_builtin = [
    {
        COMMAND_NAME: "help",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "Display help information",
        COMMAND_ACTION: show_help_command
    },
    {
        COMMAND_NAME: "save-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_OUTFILE_PARAM ],
        COMMAND_DESCRIPTION: "Saves the current user configuration to a file",
        COMMAND_ACTION: save_user_config
    }
]

add_params(_params_builtin)
add_commands(_commands_builtin)
add_pre_parse_actions([load_persistent_config, load_user_config])
add_post_parse_actions([save_persistent_config, save_user_config])