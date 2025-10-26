# Config dict to hold parameters that are saved to disk
from .param import _parse_value, get_bind_name, is_list_param, is_persistence_always, is_persistence_never, is_toggle_param
from .config_consts import CONFIG_INFILE_PARAM, CONFIG_OUTFILE_PARAM
import json
from . import logging

_persistent_config = {}

# File to store persisting params
_config_file = 'config.json'

# Config dict to hold parameter names that are never saved to disk
_non_persisted_config_names = []

# Config dict to hold runtime parameters
_config = {}

# Application name for logging and other purposes
_app_name = 'spafw37'

# Default run-level name
_default_run_level = 'exec'

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

def set_default_run_level(run_level_name):
    """Set the default run-level name.
    
    Args:
        run_level_name: Name of the run-level to use as default.
    """
    global _default_run_level
    _default_run_level = run_level_name

def get_default_run_level():
    """Get the default run-level name.
    
    Returns:
        Default run-level name.
    """
    return _default_run_level

def set_config_file(config_file):
    global _config_file
    _config_file = config_file

def update_config(new_config):
    _config.update(new_config)

def get_config_value(name):
    return _config.get(name)

def set_config_value(param, value):
    bind_name = get_bind_name(param)
    if is_list_param(param):
        set_config_list_value(value, bind_name)
    elif is_toggle_param(param):
        _config[bind_name] = bool(value)
    else:
        _config[bind_name] = _parse_value(param,value)
    logging.log_debug(_message=f"Set param '{bind_name}' = {value}")
    _manage_config_persistence(param, value)

def set_config_list_value(value, bind_name):
    if bind_name not in _config:
        _config[bind_name] = []
    if isinstance(value, list):
        _config[bind_name].extend(value)
    else:
        _config[bind_name].append(value)

def list_config_params():
    return list(_config.keys())

# Not sure this is doing the right thing - values 
#   that are Persistent should be stored in _persistent_config, not their param defs
def _manage_config_persistence(param,value):
    bind_name = get_bind_name(param)
    if is_persistence_never(param):
        _non_persisted_config_names.append(bind_name)
        return
    if is_persistence_always(param):
        _persistent_config[bind_name] = value


def load_config(config_file_in) -> dict:
    if config_file_in:
        try:
            with open(config_file_in, 'r') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError(f"Config file '{config_file_in}' is empty")
                f.seek(0)
                return json.loads(content)
        except FileNotFoundError:
            # TODO: Log file not found
            raise FileNotFoundError(f"Config file '{config_file_in}' not found")
        except PermissionError:
            # TODO: Log permission error
            raise PermissionError(f"Permission denied for config file '{config_file_in}'")
        except UnicodeDecodeError as e:
            # TODO: Log Unicode decode error
            raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, f"Unicode decode error in config file '{config_file_in}': {e.reason}")
        except json.JSONDecodeError:
            # TODO: Log invalid JSON
            raise ValueError(f"Invalid JSON in config file '{config_file_in}'")
    return {}


# Removes temporary params from config
def filter_temporary_config(config_dict):
    return {k: v for k, v in config_dict.items() if k not in _non_persisted_config_names}


def save_config(config_file_out, config_dict):
    if (config_file_out and filter_temporary_config(config_dict)):
        try:
            with open(config_file_out, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except (OSError, IOError) as e:
            # TODO: Log file write error
            raise IOError(f"Error writing to config file '{config_file_out}': {e}")


def load_persistent_config():
    _persistent_config.update(load_config(_config_file))
    update_config(_persistent_config)


def load_user_config():
    in_file = get_config_value(CONFIG_INFILE_PARAM)
    if in_file:
        _new_config = load_config(in_file)
        update_config(_new_config)


# Create a copy of _config excluding non-persisted names
def get_filtered_config_copy():
    # Return a shallow copy of _config without keys in _non_persisted_config_names
    return {k: v for k, v in _config.items() if k not in _non_persisted_config_names}


def save_user_config():
    out_file = get_config_value(CONFIG_OUTFILE_PARAM)    
    if out_file:
        # Save a filtered copy of the runtime config (exclude non-persisted params)
        save_config(out_file, get_filtered_config_copy())


def save_persistent_config():
    save_config(_config_file, _persistent_config)


