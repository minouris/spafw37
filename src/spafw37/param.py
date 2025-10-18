import re
from typing import List, Dict, Any, Optional

# Param Definitions
PARAM_NAME          = 'name'
PARAM_DESCRIPTION   = 'description'
PARAM_BIND_TO       = 'bind_to'
PARAM_TYPE          = 'type'
PARAM_ALIASES       = 'aliases'
PARAM_REQUIRED      = 'required'
PARAM_PERSISTENCE   = 'persistence'
PARAM_SWITCH_LIST   = 'switch-list'
PARAM_ALWAYS_SET    = 'always-set'
PARAM_DEFAULT       = 'default-value'

PARAM_PERSISTENCE_ALWAYS    = 'always'
PARAM_PERSISTENCE_NEVER     = 'never'

# Param Types
PARAM_TYPE_TEXT     = 'text'
PARAM_TYPE_NUMBER   = 'number'
PARAM_TYPE_TOGGLE   = 'toggle'
PARAM_TYPE_LIST     = 'list'

# RegExp Patterns
PATTERN_LONG_ALIAS = r"^--\w+(?:-\w+)*$"
PATTERN_LONG_ALIAS_EQUALS_VALUE = r"^--\w+(?:-\w+)*=.+$"
PATTERN_SHORT_ALIAS = r"^-\w{1,2}$"

_params: Dict[str, dict] = {}
_param_aliases: Dict[str, str] = {}
_xor_list: Dict[str, list] = {}

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

def is_long_alias_with_value(arg):
    return bool(re.match(PATTERN_LONG_ALIAS_EQUALS_VALUE, arg))


def is_alias(alias: str) -> bool:
    return bool(re.match(PATTERN_LONG_ALIAS, alias)
                or re.match(PATTERN_SHORT_ALIAS, alias))

def is_persistence_always(param: dict) -> bool:
    return param.get(PARAM_PERSISTENCE, None) == PARAM_PERSISTENCE_ALWAYS

def is_persistence_never(param: dict) -> bool:
    return param.get(PARAM_PERSISTENCE, None) == PARAM_PERSISTENCE_NEVER

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



# Params to set on the command line
def get_param_by_alias(alias: str) -> dict:
    param_name: Optional[str] = _param_aliases.get(alias)
    if param_name:
        param: Optional[dict] = _params.get(param_name)
        if param:
            return param
    return {}

def add_param(param: dict):
    _param_name = param.get(PARAM_NAME)
    if PARAM_ALIASES in param:
        for alias in param.get(PARAM_ALIASES, []):
            _register_param_alias(param, alias)
    if PARAM_SWITCH_LIST in param:
        _set_param_xor_list(param[PARAM_NAME], param[PARAM_SWITCH_LIST])
    _params[_param_name] = param


def _register_param_alias(param, alias):
    if not is_alias(alias):
        raise ValueError(f"Invalid alias format: {alias}")
    _param_aliases[alias] = param[PARAM_NAME]


def get_bind_name(param: dict) -> str:
    return param.get(PARAM_BIND_TO, param[PARAM_NAME])

def get_param_default(_param: dict, default=None) -> any:
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