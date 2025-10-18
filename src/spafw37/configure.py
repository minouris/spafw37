# Configures configuration parameters for the application
from .param import add_params
from .consts import *
from .config import _persistent_config, _non_persisted_config_names, config
from .cli import add_post_parse_action, add_post_parse_actions, add_pre_parse_actions
import json

_CONFIG_INFILE_KEY='config-infile'
_CONFIG_OUTFILE_KEY='config-outfile'

# File to store persisting params
_config_file = 'config.json'

_params_builtin = [
    {
        PARAM_NAME:'config-infile',
        PARAM_DESCRIPTION: 'A JSON file containing configuration to load',
        PARAM_BIND_TO:_CONFIG_INFILE_KEY,
        PARAM_TYPE: 'string',
        PARAM_ALIASES: ['--save-config','-save'],
        PARAM_REQUIRED: False,
        PARAM_NON_PERSISTED: True
    },
    {
        PARAM_NAME:'config-outfile',
        PARAM_DESCRIPTION: 'A JSON file to save configuration to',
        PARAM_BIND_TO:_CONFIG_OUTFILE_KEY,
        PARAM_TYPE: 'string',
        PARAM_ALIASES: ['--load-config','-load'],
        PARAM_REQUIRED: False,
        PARAM_NON_PERSISTED: True
    }
]

def load_config(config_file_in: str) -> dict:
    if config_file_in:
        try:
            with open(config_file_in, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # TODO: Log file not found
            pass
        except json.JSONDecodeError:
            # TODO: Log invalid JSON
            pass
    return {}

# Removes temporary params from config
def filter_temporary_config(config_dict: dict) -> dict:
    return {k: v for k, v in config_dict.items() if k not in _non_persisted_config_names}

def save_config(config_file_out: str, config_dict: dict):
    if (config_file_out and filter_temporary_config(config_dict)):
        try:
            with open(config_file_out, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except (OSError, IOError):
            # TODO: Log file write error
            pass

def load_persistent_config():
    _persistent_config.update(load_config(_config_file))
    config.update(_persistent_config)

def load_user_config():
    if (config.get(_CONFIG_INFILE_KEY)):
        config.update(load_config(config[_CONFIG_INFILE_KEY]))

def save_user_config():
    if (config.get(_CONFIG_OUTFILE_KEY)):
        save_config(config[_CONFIG_OUTFILE_KEY], config)

def save_persistent_config():
    save_config(_config_file, _persistent_config)

add_params(_params_builtin)
add_pre_parse_actions([load_persistent_config, load_user_config])
add_post_parse_actions([save_persistent_config, save_user_config])