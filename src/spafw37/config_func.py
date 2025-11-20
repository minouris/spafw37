# Config dict to hold parameters that are saved to disk
from spafw37 import param
from spafw37 import logging
from spafw37 import config
from spafw37 import file as spafw37_file
from spafw37.constants.config import (
    CONFIG_INFILE_PARAM,
    CONFIG_OUTFILE_PARAM,
)
import json

_persistent_config = {}

# File to store persisting params
_config_file = 'config.json'

# Config dict to hold parameter names that are never saved to disk
_non_persisted_config_names = []

# Application name for logging and other purposes
_app_name = 'spafw37'

def set_app_name(name):
    """Set the application name.
    
    Args:
        name: Application name.
    """
    global _app_name
    _app_name = name

def get_app_name():
    """Get the application name.
    
    Returns:
        Application name.
    """
    return _app_name

def set_config_file(config_file):
    global _config_file
    _config_file = config_file

def set_config_value(param_def, value):
    bind_name = param._get_bind_name(param_def)
    if param._is_list_param(param_def):
        config.set_config_list_value(value, bind_name)
    elif param._is_toggle_param(param_def):
        config.set_config_value(bind_name, bool(value))
    else:
        config.set_config_value(bind_name, param._parse_value(param_def, value))
    logging.log_debug(_message=f"Set param '{bind_name}' = {value}")
    _manage_config_persistence(param_def, value)

def set_config_value_from_cmdline(param_def, value):
    """Set config value from command line, handling toggle switching.
    
    When setting a toggle param from command line, unset conflicting toggles.
    
    Args:
        param_def: Parameter definition dict.
        value: Value to set.
    """
    bind_name = param._get_bind_name(param_def)
    
    # If it's a toggle, unset conflicting toggles
    if param._is_toggle_param(param_def):
        xor_params = param.get_xor_params(bind_name)
        for xor_param in xor_params:
            if xor_param in config.list_config_params():
                config.set_config_value(xor_param, False)
                logging.log_debug(_message=f"Unsetting conflicting toggle '{xor_param}'")
    
    # Set the value
    set_config_value(param_def, value)

def _manage_config_persistence(param_def, value):
    bind_name = param._get_bind_name(param_def)
    if param.is_persistence_never(param_def):
        _non_persisted_config_names.append(bind_name)
        return
    if param.is_persistence_always(param_def):
        _persistent_config[bind_name] = value


def load_config(config_file_in):
    if config_file_in:
        try:
            validated_path = spafw37_file._validate_file_for_reading(config_file_in)
        except ValueError as value_error:
            # Catch binary file or directory errors from validator
            logging.log_error(_scope='config', _message=str(value_error))
            raise value_error
        
        try:
            with open(validated_path, 'r') as file_handle:
                content = file_handle.read()
                if not content.strip():
                    # Treat empty files as empty configuration
                    return {}
                file_handle.seek(0)
                return json.loads(content)
        except FileNotFoundError:
            logging.log_error(_scope='config', _message=f"Config file '{config_file_in}' not found")
            raise FileNotFoundError(f"Config file '{config_file_in}' not found")
        except PermissionError:
            logging.log_error(_scope='config', _message=f"Permission denied for config file '{config_file_in}'")
            raise PermissionError(f"Permission denied for config file '{config_file_in}'")
        except UnicodeDecodeError as e:
            logging.log_error(_scope='config', _message=f"Unicode decode error in config file '{config_file_in}': {e.reason}")
            raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, f"Unicode decode error in config file '{config_file_in}': {e.reason}")
        except json.JSONDecodeError:
            logging.log_error(_scope='config', _message=f"Invalid JSON in config file '{config_file_in}'")
            raise ValueError(f"Invalid JSON in config file '{config_file_in}'")
    return {}


# Removes temporary params from config
def filter_temporary_config(config_dict):
    return {config_key: config_value for config_key, config_value in config_dict.items() if config_key not in _non_persisted_config_names}


def save_config(config_file_out, config_dict):
    if (config_file_out and filter_temporary_config(config_dict)):
        try:
            with open(config_file_out, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except (OSError, IOError) as e:
            logging.log_error(_scope='config', _message=f"Error writing to config file '{config_file_out}': {e}")
            raise IOError(f"Error writing to config file '{config_file_out}': {e}")


def load_persistent_config():
    _persistent_config.update(load_config(_config_file))
    config.update_config(_persistent_config)


def load_user_config():
    in_file = config.get_config_value(CONFIG_INFILE_PARAM)
    if in_file:
        _new_config = load_config(in_file)
        config.update_config(_new_config)


# Create a copy of _config excluding non-persisted names
def get_filtered_config_copy():
    # Return a shallow copy of _config without keys in _non_persisted_config_names
    return {config_key: config_value for config_key, config_value in config.list_config_items() if config_key not in _non_persisted_config_names}


def save_user_config():
    out_file = config.get_config_value(CONFIG_OUTFILE_PARAM)
    if out_file:
        # Save a filtered copy of the runtime config (exclude non-persisted params)
        save_config(out_file, get_filtered_config_copy())


def save_persistent_config():
    save_config(_config_file, _persistent_config)


