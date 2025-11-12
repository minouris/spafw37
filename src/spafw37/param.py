import re
from typing import List, Dict, Any, Optional

from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_RUNTIME_ONLY,
    PARAM_TYPE,
    PARAM_ALIASES,
    PARAM_PERSISTENCE,
    PARAM_SWITCH_LIST,
    PARAM_DEFAULT,
    PARAM_HAS_VALUE,
    PARAM_PERSISTENCE_ALWAYS,
    PARAM_PERSISTENCE_NEVER,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_LIST,
)
from spafw37.constants.command import (
    COMMAND_FRAMEWORK,
)

# RegExp Patterns
PATTERN_LONG_ALIAS = r"^--\w+(?:-\w+)*$"
PATTERN_LONG_ALIAS_EQUALS_VALUE = r"^--\w+(?:-\w+)*=.+$"
PATTERN_SHORT_ALIAS = r"^-\w{1,2}$"

_params = {}
_param_aliases = {}
_xor_list = {}

# Pre-parse arguments (params to parse before main CLI parsing)
_preparse_args = []


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

def has_xor_with(param_name: str, other_param_name: str) -> bool:
    xor_list = _xor_list.get(param_name, [])
    return other_param_name in xor_list

def get_xor_params(param_name: str):
    """Get list of params that are mutually exclusive with given param.
    
    Args:
        param_name: Bind name of the parameter.
        
    Returns:
        List of param names that are mutually exclusive with this param.
    """
    return _xor_list.get(param_name, [])

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

def param_in_args(param_name, args):
    """Check if a parameter appears in the command-line args.
    
    Args:
        param_name: Bind name of the parameter.
        args: List of command-line arguments.
        
    Returns:
        True if any alias of the param is in args.
    """
    param = get_param_by_name(param_name)
    if not param:
        return False
    
    aliases = param.get(PARAM_ALIASES, [])
    for arg in args:
        # Check exact match or --param=value format
        for alias in aliases:
            if arg == alias or arg.startswith(alias + '='):
                return True
    return False

def add_param(_param: dict):
    """Add a parameter and activate it immediately.
    
    Args:
        _param: Parameter definition dictionary with keys like
                PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, etc.
    """
    _activate_param(_param)


def _register_param_alias(param, alias):
    """Register an alias for a parameter.
    
    Args:
        param: Parameter dictionary.
        alias: Alias string to register.
    """
    if not is_alias(alias):
        raise ValueError(f"Invalid alias format: {alias}")
    _param_aliases[alias] = param[PARAM_NAME]


def _activate_param(_param):
    """Activate a parameter by adding it to the active registry.
    
    This is called internally during build_params_for_run_level to process
    buffered parameters.
    
    Args:
        _param: Parameter definition dictionary.
    """
    _param_name = _param.get(PARAM_NAME)
    if PARAM_ALIASES in _param:
        for alias in _param.get(PARAM_ALIASES, []):
            _register_param_alias(_param, alias)
    if PARAM_SWITCH_LIST in _param:
        _set_param_xor_list(_param[PARAM_NAME], _param[PARAM_SWITCH_LIST])
    if _param.get(PARAM_RUNTIME_ONLY, False):
        _param[PARAM_PERSISTENCE] = PARAM_PERSISTENCE_NEVER
    _params[_param_name] = _param


def get_bind_name(param: dict) -> str:
    return param.get(PARAM_CONFIG_NAME, param[PARAM_NAME])

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


def add_pre_parse_args(preparse_args):
    """Register params to be parsed before main CLI parsing.
    
    Pre-parse params are typically used for logging/verbosity control
    to configure logging before parsing other params.
    
    Args:
        preparse_args: List of dicts with PARAM_NAME and PARAM_HAS_VALUE keys.
                      Example: [{PARAM_NAME: "silent", PARAM_HAS_VALUE: False}]
    """
    global _preparse_args
    _preparse_args.extend(preparse_args)


def get_pre_parse_args():
    """Get the list of registered pre-parse params.
    
    Returns:
        List of pre-parse param definitions (full param dicts).
    """
    # Convert param names to full param definitions
    result = []
    for param_name in _preparse_args:
        param_def = get_param_by_name(param_name)
        if param_def:
            result.append(param_def)
    return result


def get_all_param_definitions():
    """Accessor function to retrieve all parameter definitions."""
    return _params.values()



