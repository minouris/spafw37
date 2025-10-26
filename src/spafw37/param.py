import re
from typing import List, Dict, Any, Optional
from .config_consts import (
    PARAM_NAME,
    PARAM_BIND_TO,
    PARAM_RUNTIME_ONLY,
    PARAM_TYPE,
    PARAM_ALIASES,
    PARAM_PERSISTENCE,
    PARAM_SWITCH_LIST,
    PARAM_DEFAULT,
    PARAM_PERSISTENCE_ALWAYS,
    PARAM_PERSISTENCE_NEVER,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_LIST,
)

# RegExp Patterns
PATTERN_LONG_ALIAS = r"^--\w+(?:-\w+)*$"
PATTERN_LONG_ALIAS_EQUALS_VALUE = r"^--\w+(?:-\w+)*=.+$"
PATTERN_SHORT_ALIAS = r"^-\w{1,2}$"

_params = {}
_param_aliases = {}
_xor_list = {}

# Buffered parameters for deferred processing
_buffered_params = []

# Run-level definitions
_run_levels = {}

def is_long_alias(arg):
    return bool(re.match(PATTERN_LONG_ALIAS, arg))

def is_long_alias_with_value(arg):
    return bool(re.match(PATTERN_LONG_ALIAS_EQUALS_VALUE, arg))

def is_short_alias(arg):
    return bool(re.match(PATTERN_SHORT_ALIAS, arg))

def is_param_type(param: dict, param_type: str) -> bool:
    return param.get(PARAM_TYPE, PARAM_TYPE_TEXT) == param_type

def is_number_param(param: dict) -> bool:
    return is_param_type(param, PARAM_TYPE_NUMBER)

def is_list_param(param: dict) -> bool:
    return is_param_type(param, PARAM_TYPE_LIST)

def is_toggle_param(param: dict) -> bool:
    return is_param_type(param, PARAM_TYPE_TOGGLE)


def is_alias(alias: str) -> bool:
    return bool(re.match(PATTERN_LONG_ALIAS, alias)
                or re.match(PATTERN_SHORT_ALIAS, alias))

def is_persistence_always(param: dict) -> bool:
    return param.get(PARAM_PERSISTENCE, None) == PARAM_PERSISTENCE_ALWAYS

def is_persistence_never(param: dict) -> bool:
    return param.get(PARAM_PERSISTENCE, None) == PARAM_PERSISTENCE_NEVER

def is_runtime_only_param(_param):
    if not _param:
        return False
    return _param.get(PARAM_RUNTIME_ONLY, False)

def _parse_number(value, default=0):
    if isinstance(value, float) or isinstance(value, int):
        return value
    else:
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return default

def _parse_value(param, value):
    if is_number_param(param):
        return _parse_number(value)
    elif is_toggle_param(param):
        return not bool(param.get(PARAM_DEFAULT, False))
    elif is_list_param(param):
        if not isinstance(value, list):
            return [value]
        return value
    else:
        return value

def _add_param_xor(param_name: str, xor_param_name: str):
    if param_name not in _xor_list:
        _xor_list[param_name] = [ xor_param_name]
        return
    if xor_param_name not in _xor_list[param_name]:
        _xor_list[param_name].append(xor_param_name)

def _has_xor_with(param_name: str, other_param_name: str) -> bool:
    xor_list = _xor_list.get(param_name, [])
    return other_param_name in xor_list

def _set_param_xor_list(param_name: str, xor_list: list):
    for xor_param_name in xor_list:
        _add_param_xor(param_name, xor_param_name)
        _add_param_xor(xor_param_name, param_name)

def get_param_by_name(param_name):
    if param_name in _params:
        return _params.get(param_name)
    return None

# Params to set on the command line
def get_param_by_alias(alias: str) -> dict:
    param_name: Optional[str] = _param_aliases.get(alias)
    if param_name:
        param: Optional[dict] = _params.get(param_name)
        if param:
            return param
    return {}

def is_param_alias(_param: dict, alias: str) -> bool:
    aliases = _param.get(PARAM_ALIASES, [])
    return alias in aliases

def add_param(_param: dict):
    _param_name = _param.get(PARAM_NAME)
    if PARAM_ALIASES in _param:
        for alias in _param.get(PARAM_ALIASES, []):
            _register_param_alias(_param, alias)
    if PARAM_SWITCH_LIST in _param:
        _set_param_xor_list(_param[PARAM_NAME], _param[PARAM_SWITCH_LIST])
    if _param.get(PARAM_RUNTIME_ONLY, False):
        _param[PARAM_PERSISTENCE] = PARAM_PERSISTENCE_NEVER
    _params[_param_name] = _param


def _register_param_alias(param, alias):
    if not is_alias(alias):
        raise ValueError(f"Invalid alias format: {alias}")
    _param_aliases[alias] = param[PARAM_NAME]


def get_bind_name(param: dict) -> str:
    return param.get(PARAM_BIND_TO, param[PARAM_NAME])

def get_param_default(_param: dict, default=None):
    return _param.get(PARAM_DEFAULT, default)

def param_has_default(_param: dict) -> bool:
    return PARAM_DEFAULT in _param

def add_params(params: List[Dict[str, Any]]):
    """Add multiple parameter dictionaries.

    Args:
        params: A list of parameter dicts.
    """
    for param in params:
       add_param(param)


def add_buffered_param(param_dict):
    """Add a parameter to the buffer for deferred processing.
    
    Parameters are stored as dictionaries and processed later when
    build_params_for_run_level is called.
    
    Args:
        param_dict: Parameter definition dictionary with keys like
                    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, etc.
    """
    _buffered_params.append(param_dict)


def add_buffered_params(params):
    """Add multiple parameters to the buffer.
    
    Args:
        params: List of parameter definition dictionaries.
    """
    for param in params:
        add_buffered_param(param)


def register_run_level(name, defaults):
    """Register a named run-level with default parameter values.
    
    Args:
        name: Name of the run-level (e.g., 'dev', 'prod', 'staging').
        defaults: Dictionary mapping parameter bind names to default values.
    """
    _run_levels[name] = defaults


def get_run_level(name):
    """Get the defaults for a named run-level.
    
    Args:
        name: Name of the run-level.
        
    Returns:
        Dictionary of parameter defaults, or None if run-level not found.
    """
    return _run_levels.get(name)


def list_run_levels():
    """Get list of all registered run-level names.
    
    Returns:
        List of run-level names.
    """
    return list(_run_levels.keys())


def build_params_for_run_level(run_level=None):
    """Process buffered parameters and register them.
    
    This flushes the buffered parameter list and adds them to the
    active parameter registry. If a run_level is specified, applies
    that run-level's defaults.
    
    Args:
        run_level: Name of run-level to apply, or None for base defaults.
    """
    for param in _buffered_params:
        param_copy = dict(param)
        
        if run_level:
            run_level_defaults = get_run_level(run_level)
            if run_level_defaults:
                bind_name = param_copy.get(PARAM_BIND_TO, param_copy.get(PARAM_NAME))
                if bind_name in run_level_defaults:
                    param_copy[PARAM_DEFAULT] = run_level_defaults[bind_name]
        
        add_param(param_copy)
    
    _buffered_params.clear()


def get_buffered_params():
    """Get the list of buffered parameters.
    
    Returns:
        List of buffered parameter dictionaries.
    """
    return list(_buffered_params)


