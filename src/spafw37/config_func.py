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

def track_persistent_value(bind_name, value):
    """Track a parameter value for persistent config storage.
    
    Called by param.py when a parameter with PARAM_PERSISTENCE_ALWAYS is set.
    
    Args:
        bind_name: Config bind name for the parameter.
        value: Value to store in persistent config.
    """
    _persistent_config[bind_name] = value

def set_config_file(config_file):
    global _config_file
    _config_file = config_file


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
    """Filter out non-persisted parameters from config dict.
    
    Queries param.py for the list of config bind names that should not be persisted.
    
    Args:
        config_dict: Dictionary to filter.
        
    Returns:
        Filtered dictionary without non-persisted parameters.
    """
    non_persisted_names = param.get_non_persisted_config_names()
    return {config_key: config_value for config_key, config_value in config_dict.items() if config_key not in non_persisted_names}


def save_config(config_file_out, config_dict):
    if (config_file_out and filter_temporary_config(config_dict)):
        try:
            with open(config_file_out, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except (OSError, IOError) as e:
            logging.log_error(_scope='config', _message=f"Error writing to config file '{config_file_out}': {e}")
            raise IOError(f"Error writing to config file '{config_file_out}': {e}")


def load_persistent_config():
    """Load persistent configuration from file.
    
    Loads config.json and updates the runtime config. XOR validation is disabled
    during loading since values were already validated when saved.
    """
    loaded_config = load_config(_config_file)
    _persistent_config.update(loaded_config)
    
    # Disable XOR validation while loading to avoid false conflicts
    param._set_xor_validation_enabled(False)
    try:
        # Load config values through param API to trigger proper initialization
        for config_key, value in loaded_config.items():
            # Try to find param with this bind name and set through param API
            try:
                param.set_param_value(bind_name=config_key, value=value)
            except ValueError:
                # If param not registered, set directly in config (backward compatibility)
                config.set_config_value(config_key, value)
    finally:
        # Always re-enable XOR validation after loading
        param._set_xor_validation_enabled(True)


def load_user_config():
    """Load user configuration from file specified by CONFIG_INFILE_PARAM.
    
    Loads user config file and updates runtime config. XOR validation is disabled
    during loading since values were already validated when saved.
    """
    in_file = config.get_config_value(CONFIG_INFILE_PARAM)
    if in_file:
        loaded_config = load_config(in_file)
        
        # Disable XOR validation while loading to avoid false conflicts
        param._set_xor_validation_enabled(False)
        try:
            # Load config values through param API to trigger proper initialization
            for config_key, value in loaded_config.items():
                # Try to find param with this bind name and set through param API
                try:
                    param.set_param_value(bind_name=config_key, value=value)
                except ValueError:
                    # If param not registered, set directly in config (backward compatibility)
                    config.set_config_value(config_key, value)
        finally:
            # Always re-enable XOR validation after loading
            param._set_xor_validation_enabled(True)


# Create a copy of _config excluding non-persisted names
def get_filtered_config_copy():
    """Get a copy of runtime config excluding non-persisted parameters.
    
    Queries param.py for the list of config bind names that should not be persisted.
    
    Returns:
        Shallow copy of runtime config without non-persisted parameters.
    """
    non_persisted_names = param.get_non_persisted_config_names()
    return {config_key: config_value for config_key, config_value in config.list_config_items() if config_key not in non_persisted_names}


def save_user_config():
    out_file = config.get_config_value(CONFIG_OUTFILE_PARAM)
    if out_file:
        # Save a filtered copy of the runtime config (exclude non-persisted params)
        save_config(out_file, get_filtered_config_copy())


def save_persistent_config():
    save_config(_config_file, _persistent_config)


