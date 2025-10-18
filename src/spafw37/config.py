

# Config dict to hold parameters that are saved to disk
from .param import get_bind_name, is_list_param, is_persistence_always, is_persistence_never, is_toggle_param

_persistent_config = {}

# Config dict to hold parameter names that are never saved to disk
_non_persisted_config_names = []

# Config dict to hold runtime parameters
config = {}

def set_config_value(param: dict, value):
    bind_name = get_bind_name(param)
    if is_list_param(param):
        config[bind_name].append(value)
    elif is_toggle_param(param):
        config[bind_name] = bool(value)
    else:
        config[bind_name] = value
    _manage_config_persistence(param, bind_name)

def _manage_config_persistence(param, bind_name):
    if is_persistence_never(param):
        _non_persisted_config_names.append(bind_name)
        return
    if is_persistence_always(param):
        _persistent_config[bind_name] = param


