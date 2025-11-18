import re
import json
import os
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
    PARAM_TYPE_DICT,
)
from spafw37.constants.command import (
    COMMAND_FRAMEWORK,
)
from spafw37 import file as spafw37_file
from spafw37 import config


# RegExp Patterns
PATTERN_LONG_ALIAS = r"^--\w+(?:-\w+)*$"
PATTERN_LONG_ALIAS_EQUALS_VALUE = r"^--\w+(?:-\w+)*=.+$"
PATTERN_SHORT_ALIAS = r"^-\w{1,2}$"

# NOTE: Thread Safety - These module-level variables are not thread-safe.
# This framework is designed for single-threaded CLI applications. If using
# in a multi-threaded context, external synchronization is required.
_params = {}
_param_aliases = {}
_xor_list = {}

# Pre-parse arguments (params to parse before main CLI parsing)
_preparse_args = []


# Helper functions for inline object definitions
def _get_param_name(param_def):
    """Extract parameter name from parameter definition.
    
    Args:
        param_def: Parameter definition dict or string name
        
    Returns:
        Parameter name as string
    """
    if isinstance(param_def, str):
        return param_def
    return param_def.get(PARAM_NAME, '')


def _register_inline_param(param_def):
    """Register an inline parameter definition.
    
    If param_def is a dict (inline definition), registers it in the global
    parameter registry. If it's a string (name reference), does nothing.
    
    Args:
        param_def: Parameter definition dict or string name
        
    Returns:
        Parameter name as string
    """
    if isinstance(param_def, dict):
        param_name = param_def.get(PARAM_NAME)
        if param_name and param_name not in _params:
            # Process inline params in switch list first (recursive)
            if PARAM_SWITCH_LIST in param_def:
                switch_list = param_def[PARAM_SWITCH_LIST]
                normalized_switches = []
                for switch_def in switch_list:
                    switch_name = _register_inline_param(switch_def)
                    normalized_switches.append(switch_name)
                param_def[PARAM_SWITCH_LIST] = normalized_switches
            
            _params[param_name] = param_def
            # Register aliases if present
            aliases = param_def.get(PARAM_ALIASES, [])
            for alias in aliases:
                _param_aliases[alias] = param_name
            # Register switch list if present (now normalized)
            if PARAM_SWITCH_LIST in param_def:
                _set_param_xor_list(param_name, param_def[PARAM_SWITCH_LIST])
        return param_name
    return param_def


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

def is_dict_param(param: dict) -> bool:
    """Return True if the parameter definition indicates a dict type.

    Args:
        param: Parameter definition dict.

    Returns:
        True if the param's type is PARAM_TYPE_DICT, False otherwise.
    """
    return is_param_type(param, PARAM_TYPE_DICT)

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


def _validate_number(value):
    """Validate and coerce a value to a number (int or float).
    
    Args:
        value: Value to validate and coerce.
        
    Returns:
        Coerced numeric value (int or float).
        
    Raises:
        ValueError: If value cannot be coerced to a number.
    """
    if isinstance(value, (int, float)):
        return value
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot coerce value to number: {value}")


def _validate_toggle(param_def):
    """Validate and return toggle value (flipped default).
    
    Toggles don't take a value parameter - they flip on presence.
    
    Args:
        param_def: Parameter definition dict.
        
    Returns:
        Flipped boolean value (opposite of default).
    """
    return not bool(param_def.get(PARAM_DEFAULT, False))


def _validate_list(value):
    """Validate and coerce a value to a list.
    
    Args:
        value: Value to validate and coerce.
        
    Returns:
        List value (wraps non-list values in a list).
    """
    if isinstance(value, list):
        return value
    return [value]


def _validate_dict(value):
    """Validate and coerce a value to a dict.
    
    Accepts dict directly, or parses JSON strings starting with '{'.
    File loading (@file) is handled by CLI layer before validation.
    
    Args:
        value: Value to validate and coerce.
        
    Returns:
        Dict value.
        
    Raises:
        ValueError: If value cannot be coerced to a dict.
    """
    if isinstance(value, dict):
        return value
    
    # Normalize raw input into a single JSON text string
    json_text = _normalize_dict_input(value)
    
    # File reference notation: @/path/to/file.json
    # Note: CLI layer should have already loaded this, but handle it anyway
    if json_text.startswith('@'):
        return _load_json_file(json_text[1:])
    
    # JSON object string
    if json_text.startswith('{'):
        return _parse_json_text(json_text)
    
    # Not a valid dict format
    raise ValueError("Dict parameter expects JSON object or @file reference")


def _validate_text(value):
    """Validate and coerce a value to text (string).
    
    Args:
        value: Value to validate and coerce.
        
    Returns:
        String value.
    """
    if not isinstance(value, str):
        return str(value)
    return value


def _parse_value(param, value):
    """Parse and coerce a raw parameter value according to param type.

    This function handles number, toggle, list and dict types. For dict
    parameters the accepted input forms are:
      - a Python dict (returned as-is)
      - a JSON string representing an object
      - a file reference using the @path notation (file must contain JSON object)

    Args:
        param: Parameter definition dict.
        value: Raw value (string, list of tokens, dict, etc.).

    Returns:
        Parsed/coerced value appropriate for the param type.

    Raises:
        ValueError, FileNotFoundError, PermissionError for invalid inputs.
    """
    # If caller provided multiple tokens (list) for a non-list param,
    # normalize into a single string here. This normalization applies to
    # text/number/toggle/dict params and keeps parsing logic simpler.
    if isinstance(value, list) and not is_list_param(param):
        value = ' '.join(value)

    # NOTE: file (@path) handling is performed during argument capture in the
    # CLI layer so that the parser receives the file contents at the appropriate
    # time. Do not read files here; this function only parses values.

    if is_number_param(param):
        return _parse_number(value)
    elif is_toggle_param(param):
        return not bool(param.get(PARAM_DEFAULT, False))
    elif is_list_param(param):
        if not isinstance(value, list):
            return [value]
        return value
    elif is_dict_param(param):
        # Accept dict value directly
        if isinstance(value, dict):
            return value

        # Normalize raw input into a single JSON text string
        json_text = _normalize_dict_input(value)
        # File reference notation: @/path/to/file.json
        if json_text.startswith('@'):
            return _load_json_file(json_text[1:])

        # JSON object string
        if json_text.startswith('{'):
            return _parse_json_text(json_text)
        # Fallback: treat as plain string (not allowed for dict)
        raise ValueError("Dict parameter expects JSON object or @file reference")
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


def _get_param_definition(param_name):
    """Get parameter definition by parameter name.
    
    Private version of get_param_by_name for internal use.
    
    Args:
        param_name: Parameter name to look up.
        
    Returns:
        Parameter definition dict or None if not found.
    """
    if param_name in _params:
        return _params.get(param_name)
    return None


def _get_param_definition_by_alias(alias):
    """Get parameter definition by alias.
    
    Private version of get_param_by_alias for internal use.
    
    Args:
        alias: Parameter alias to look up.
        
    Returns:
        Parameter definition dict or None if not found.
    """
    param_name = _param_aliases.get(alias)
    if param_name:
        param = _params.get(param_name)
        if param:
            return param
    return None


def _get_param_definition_by_bind_name(bind_name):
    """Get parameter definition by config bind name.
    
    Searches all parameters for one whose bind name matches.
    
    Args:
        bind_name: Config bind name to look up.
        
    Returns:
        Parameter definition dict or None if not found.
    """
    for param_def in _params.values():
        if _get_bind_name(param_def) == bind_name:
            return param_def
    return None


def _resolve_param_definition(param_name=None, bind_name=None, alias=None):
    """Resolve parameter definition from multiple address spaces.
    
    Flexible param resolution supporting three address spaces:
    - param_name: parameter name (e.g., 'database-host')
    - bind_name: config key (e.g., 'database_host')  
    - alias: CLI alias (e.g., '--db-host', '-d')
    
    When using named arguments, only checks the specified address space.
    When using positional argument, uses failover pattern (name → bind → alias).
    
    Args:
        param_name: Parameter name to resolve (first positional arg).
        bind_name: Config bind name to resolve.
        alias: CLI alias to resolve.
        
    Returns:
        Parameter definition dict or None if not found.
        
    Examples:
        # Named argument - only checks param names:
        _resolve_param_definition(param_name='database')
        
        # Positional argument - tries all three address spaces:
        _resolve_param_definition('database')
        
        # Named bind_name - only checks bind names:
        _resolve_param_definition(bind_name='database_host')
    """
    # If multiple address spaces specified, check each in priority order
    if param_name is not None:
        param_def = _get_param_definition(param_name)
        if param_def:
            return param_def
        # If only param_name provided (positional usage), try failover
        if bind_name is None and alias is None:
            param_def = _get_param_definition_by_bind_name(param_name)
            if param_def:
                return param_def
            param_def = _get_param_definition_by_alias(param_name)
            if param_def:
                return param_def
    
    if bind_name is not None:
        param_def = _get_param_definition_by_bind_name(bind_name)
        if param_def:
            return param_def
    
    if alias is not None:
        param_def = _get_param_definition_by_alias(alias)
        if param_def:
            return param_def
    
    return None


def get_param_by_name(param_name):
    """Get parameter definition by parameter name.
    
    Public API - delegates to private _get_param_definition().
    
    Args:
        param_name: Parameter name to look up.
        
    Returns:
        Parameter definition dict or None if not found.
    """
    return _get_param_definition(param_name)


# Params to set on the command line
def get_param_by_alias(alias: str) -> dict:
    """Get parameter definition by alias.
    
    Public API - delegates to private _get_param_definition_by_alias().
    Returns empty dict for backward compatibility when not found.
    
    Args:
        alias: Parameter alias to look up.
        
    Returns:
        Parameter definition dict or empty dict if not found.
    """
    result = _get_param_definition_by_alias(alias)
    return result if result else {}

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
    
    # Process inline parameter definitions in PARAM_SWITCH_LIST
    if PARAM_SWITCH_LIST in _param:
        switch_list = _param[PARAM_SWITCH_LIST]
        normalized_switches = []
        for param_def in switch_list:
            param_name = _register_inline_param(param_def)
            normalized_switches.append(param_name)
        _param[PARAM_SWITCH_LIST] = normalized_switches
        _set_param_xor_list(_param[PARAM_NAME], normalized_switches)
    
    if _param.get(PARAM_RUNTIME_ONLY, False):
        _param[PARAM_PERSISTENCE] = PARAM_PERSISTENCE_NEVER
    _params[_param_name] = _param


def _get_bind_name(param):
    """Get the config bind name for a parameter.
    
    Returns the PARAM_CONFIG_NAME if specified, otherwise PARAM_NAME.
    """
    return param.get(PARAM_CONFIG_NAME, param[PARAM_NAME])

def _get_param_default(_param, default=None):
    """Get the default value for a parameter."""
    return _param.get(PARAM_DEFAULT, default)

def _param_has_default(_param):
    """Check if parameter has a default value defined."""
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


# Helper functions ---------------------------------------------------------
def _load_json_file(path: str) -> dict:
    """Load and parse JSON from a file path.

    Args:
        path: Path to JSON file (tilde expansion performed).

    Returns:
        Parsed JSON as dict.

    Raises:
        FileNotFoundError, PermissionError, ValueError on parse errors.
    """
    validated_path = spafw37_file._validate_file_for_reading(path)
    try:
        with open(validated_path, 'r') as file_handle:
            file_content = file_handle.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Dict param file not found: {validated_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied reading dict param file: {validated_path}")
    except UnicodeDecodeError:
        raise ValueError(f"Dict param file contains invalid text encoding: {validated_path}")
    try:
        parsed_json = json.loads(file_content)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in dict param file: {validated_path}")
    if not isinstance(parsed_json, dict):
        raise ValueError(f"Dict param file must contain a JSON object: {validated_path}")
    return parsed_json


def _parse_json_text(text: str) -> dict:
    """Parse a JSON string and validate it is an object.

    Args:
        text: JSON string.

    Returns:
        Parsed dict.

    Raises:
        ValueError if JSON invalid or not an object.
    """
    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON for dict parameter; quote your JSON or use @file")
    if not isinstance(parsed_json, dict):
        raise ValueError("Provided JSON must be an object for dict parameter")
    return parsed_json


def _normalize_dict_input(value) -> str:
    """Normalize raw dict parameter input into a JSON text string.

    Accepts a list of tokens or a single-string token and returns a
    stripped JSON text string. Raises ValueError for unsupported types.

    Args:
        value: Raw value provided from the CLI (str or list).

    Returns:
        A stripped string containing JSON text or an @file reference.
    """
    # After higher-level normalization, value should be a string here.
    if not isinstance(value, str):
        raise ValueError("Invalid dict parameter value")
    return value.strip()


def get_param_value(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Retrieve raw parameter value from configuration with flexible resolution.
    
    Resolves parameter using param_name, bind_name, or alias with failover logic,
    then retrieves the value from internal configuration. Returns default if not found
    unless strict mode is enabled.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found (default: None)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Returns:
        The raw value from configuration, or default if not found
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    param_definition = _resolve_param_definition(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias
    )
    
    if param_definition is None:
        if strict:
            raise ValueError("Parameter '{}' not found".format(param_name or bind_name or alias))
        return default
    
    resolved_param_name = _get_param_name(param_definition)
    value = config.get_config_value(resolved_param_name)
    
    if value is None:
        if strict:
            raise ValueError("Parameter '{}' not found in configuration".format(resolved_param_name))
        return default
    
    return value


def get_param_str(param_name=None, bind_name=None, alias=None, default='', strict=False):
    """
    Retrieve string parameter value with type coercion.
    
    Gets raw value via get_param_value() and coerces to string using str().
    Any value type can be converted to string representation.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found (default: '')
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Returns:
        The value coerced to string, or default if not found
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    value = get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )
    
    return str(value)


def get_param_int(param_name=None, bind_name=None, alias=None, default=0, strict=False):
    """
    Retrieve integer parameter value with type coercion and truncation.
    
    Gets raw value via get_param_value() and coerces to int via int(float(value))
    for truncation behavior. In strict mode, raises ValueError on coercion failure.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found or coercion fails (default: 0)
        strict: If True, raises ValueError on coercion failure (default: False)
    
    Returns:
        The value coerced to int (truncated), or default if not found or coercion fails
    
    Raises:
        ValueError: If strict=True and coercion fails
    """
    value = get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=False  # Handle strict mode ourselves after coercion
    )
    
    try:
        # Use int(float(value)) for truncation behavior
        return int(float(value))
    except (ValueError, TypeError) as error:
        if strict:
            raise ValueError("Cannot convert '{}' to int: {}".format(value, error))
        return default


def get_param_bool(param_name=None, bind_name=None, alias=None, default=False, strict=False):
    """
    Retrieve boolean parameter value with truthiness coercion.
    
    Gets raw value via get_param_value() and coerces using Python's bool()
    for truthy/falsy evaluation. Non-empty strings, non-zero numbers, and
    non-empty collections are True; empty values are False.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found (default: False)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Returns:
        The value coerced to boolean, or default if not found
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    value = get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )
    
    return bool(value)


def get_param_float(param_name=None, bind_name=None, alias=None, default=0.0, strict=False):
    """
    Retrieve float parameter value with type coercion.
    
    Gets raw value via get_param_value() and coerces to float using float().
    In strict mode, raises ValueError on coercion failure.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found or coercion fails (default: 0.0)
        strict: If True, raises ValueError on coercion failure (default: False)
    
    Returns:
        The value coerced to float, or default if not found or coercion fails
    
    Raises:
        ValueError: If strict=True and coercion fails
    """
    value = get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=False  # Handle strict mode ourselves after coercion
    )
    
    try:
        return float(value)
    except (ValueError, TypeError) as error:
        if strict:
            raise ValueError("Cannot convert '{}' to float: {}".format(value, error))
        return default


def get_param_list(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Retrieve list parameter value without coercion.
    
    Gets raw value via get_param_value() and returns as-is. Defaults to empty list
    if not found and no explicit default provided. Does not perform type coercion.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found (default: empty list)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Returns:
        The value as-is, or empty list if not found and no default provided
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    if default is None:
        default = []
    
    return get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )


def get_param_dict(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Retrieve dict parameter value without coercion.
    
    Gets raw value via get_param_value() and returns as-is. Defaults to empty dict
    if not found and no explicit default provided. Does not perform type coercion.
    
    Args:
        param_name: Parameter name to look up (optional if bind_name or alias provided)
        bind_name: Bind name to look up (optional if param_name or alias provided)
        alias: Alias to look up (optional if param_name or bind_name provided)
        default: Value to return if parameter not found (default: empty dict)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Returns:
        The value as-is, or empty dict if not found and no default provided
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    if default is None:
        default = {}
    
    return get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )



