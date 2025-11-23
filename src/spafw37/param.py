import re

from spafw37 import logging

from spafw37.constants.param import (
    PARAM_ALLOWED_VALUES,
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_RUNTIME_ONLY,
    PARAM_TYPE,
    PARAM_ALIASES,
    PARAM_PERSISTENCE,
    PARAM_SWITCH_LIST,
    PARAM_DEFAULT,
    PARAM_IMMUTABLE,
    PARAM_PERSISTENCE_ALWAYS,
    PARAM_PERSISTENCE_NEVER,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
    PARAM_JOIN_SEPARATOR,
    PARAM_INPUT_FILTER,
    PARAM_DEFAULT_INPUT_FILTERS,
    PARAM_DICT_MERGE_TYPE,
    PARAM_DICT_OVERRIDE_STRATEGY,
    DICT_MERGE_SHALLOW,
    DICT_MERGE_DEEP,
    DICT_OVERRIDE_RECENT,
    DICT_OVERRIDE_OLDEST,
    DICT_OVERRIDE_ERROR,
    SEPARATOR_SPACE,
)
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

# XOR validation control - used internally to skip validation during defaults/config loading
_skip_xor_validation = False


# Helper functions for inline object definitions
def _set_xor_validation_enabled(enabled):
    """Private mutator to control XOR validation.
    
    Used internally to temporarily disable XOR validation during
    defaults initialization and config loading operations.
    
    Args:
        enabled: True to enable XOR validation (default), False to disable
    """
    global _skip_xor_validation
    _skip_xor_validation = not enabled


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

def _is_param_type(param, param_type):
    return param.get(PARAM_TYPE, PARAM_TYPE_TEXT) == param_type

def _is_toggle_param(param):
    return _is_param_type(param, PARAM_TYPE_TOGGLE)


def is_toggle_param(param_name=None, bind_name=None, alias=None):
    """Check if parameter is a toggle type by name/bind/alias.
    
    Args:
        param_name: Parameter's PARAM_NAME
        bind_name: Parameter's PARAM_CONFIG_NAME
        alias: Any of the parameter's PARAM_ALIASES
        
    Returns:
        True if parameter is a toggle type, False otherwise.
    """
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    return _is_toggle_param(param_def) if param_def else False


def is_list_param(param_name=None, bind_name=None, alias=None):
    """Check if parameter is a list type by name/bind/alias.
    
    Args:
        param_name: Parameter's PARAM_NAME
        bind_name: Parameter's PARAM_CONFIG_NAME
        alias: Any of the parameter's PARAM_ALIASES
        
    Returns:
        True if parameter is a list type, False otherwise.
    """
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    return _is_param_type(param_def, PARAM_TYPE_LIST) if param_def else False


def is_dict_param(param_name=None, bind_name=None, alias=None):
    """Check if parameter is a dict type by name/bind/alias.
    
    Args:
        param_name: Parameter's PARAM_NAME
        bind_name: Parameter's PARAM_CONFIG_NAME
        alias: Any of the parameter's PARAM_ALIASES
        
    Returns:
        True if parameter is a dict type, False otherwise.
    """
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    return _is_param_type(param_def, PARAM_TYPE_DICT) if param_def else False


def is_number_param(param_name=None, bind_name=None, alias=None):
    """Check if parameter is a number type by name/bind/alias.
    
    Args:
        param_name: Parameter's PARAM_NAME
        bind_name: Parameter's PARAM_CONFIG_NAME
        alias: Any of the parameter's PARAM_ALIASES
        
    Returns:
        True if parameter is a number type, False otherwise.
    """
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    return _is_param_type(param_def, PARAM_TYPE_NUMBER) if param_def else False


def is_text_param(param_name=None, bind_name=None, alias=None):
    """Check if parameter is a text type by name/bind/alias.
    
    Args:
        param_name: Parameter's PARAM_NAME
        bind_name: Parameter's PARAM_CONFIG_NAME
        alias: Any of the parameter's PARAM_ALIASES
        
    Returns:
        True if parameter is a text type, False otherwise.
    """
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    return _is_param_type(param_def, PARAM_TYPE_TEXT) if param_def else False


def is_alias(alias):
    return bool(re.match(PATTERN_LONG_ALIAS, alias)
                or re.match(PATTERN_SHORT_ALIAS, alias))

def is_persistence_always(param):
    """Check if parameter has PARAM_PERSISTENCE_ALWAYS set.
    
    Args:
        param: Parameter definition dict.
        
    Returns:
        True if param should always be persisted.
    """
    return param.get(PARAM_PERSISTENCE, None) == PARAM_PERSISTENCE_ALWAYS

def is_persistence_never(param):
    """Check if parameter has PARAM_PERSISTENCE_NEVER set.
    
    Args:
        param: Parameter definition dict.
        
    Returns:
        True if param should never be persisted.
    """
    return param.get(PARAM_PERSISTENCE, None) == PARAM_PERSISTENCE_NEVER

def get_non_persisted_config_names():
    """Get list of config bind names that should never be persisted.
    
    Queries all registered parameters and returns the config bind names
    for those with PARAM_PERSISTENCE_NEVER.
    
    Returns:
        List of config bind names that should not be persisted.
    """
    non_persisted_names = []
    for param_name, param_def in _params.items():
        if is_persistence_never(param_def):
            bind_name = _get_bind_name(param_def)
            non_persisted_names.append(bind_name)
    return non_persisted_names

def notify_persistence_change(param_name, value):
    """Notify config_func about parameter value changes for persistence tracking.
    
    This is called when a parameter value is set, to allow config_func to
    track which values should be saved to persistent config.
    
    Args:
        param_name: Name of the parameter.
        value: New value for the parameter.
    """
    from spafw37 import config_func
    param_def = _get_param_definition(param_name)
    if param_def and is_persistence_always(param_def):
        bind_name = _get_bind_name(param_def)
        config_func.track_persistent_value(bind_name, value)

def is_runtime_only_param(_param):
    if not _param:
        return False
    return _param.get(PARAM_RUNTIME_ONLY, False)

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
    """Validate and parse a value to a dict.
    
    Accepts dict directly, or parses JSON strings.
    The CLI passes JSON strings which this function parses and validates.
    
    Args:
        value: Value to validate (dict or JSON string).
        
    Returns:
        Dict value.
        
    Raises:
        ValueError: If value cannot be parsed or is not a dict/object.
    """
    if isinstance(value, dict):
        return value
    
    # Parse JSON string
    if isinstance(value, str):
        json_text = value.strip()
        # Parse JSON
        try:
            import json
            parsed = json.loads(json_text)
        except json.JSONDecodeError as parse_error:
            raise ValueError(f"Invalid JSON for dict parameter: {str(parse_error)}")
        
        # Validate it's actually a dict/object, not array or primitive
        if not isinstance(parsed, dict):
            raise ValueError(f"Dict parameter requires JSON object, got {type(parsed).__name__}")
        
        return parsed
    
    # Reject non-dict, non-string values
    raise ValueError(f"Dict parameter requires dict or JSON string, got {type(value).__name__}")


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


def _normalise_text_to_allowed_case(value, allowed_values):
    """Match value case-insensitively against allowed_values and return canonical case.
    
    Performs case-insensitive comparison between value and each item in allowed_values.
    Returns the canonical case from allowed_values if a match is found, None otherwise.
    
    Args:
        value: String value to normalise
        allowed_values: List of allowed string values in canonical case
        
    Returns:
        String in canonical case if match found, None otherwise
        
    Example:
        If allowed_values contains 'DEBUG' and value is 'debug', returns 'DEBUG'
    """
    value_lower = value.lower()
    for allowed in allowed_values:
        if allowed.lower() == value_lower:
            return allowed
    return None


def _validate_text_allowed_values(param_name, value, allowed_values):
    """Validate TEXT parameter value against allowed values with case-insensitive matching.
    
    Args:
        param_name: Parameter name for error messages
        value: String value to validate
        allowed_values: List of allowed string values
        
    Raises:
        ValueError: If value not in allowed values list
    """
    if _normalise_text_to_allowed_case(value, allowed_values) is None:
        allowed_str = ', '.join(str(av) for av in allowed_values)
        raise ValueError(
            f"Value '{value}' not allowed for parameter '{param_name}'. "
            f"Allowed values: {allowed_str}"
        )


def _validate_list_allowed_values(param_name, value, allowed_values):
    """Validate LIST parameter elements against allowed values.
    
    Validates each element individually with case-insensitive matching.
    Rejects empty lists when allowed values are specified.
    
    Args:
        param_name: Parameter name for error messages
        value: List of values to validate
        allowed_values: List of allowed values
        
    Raises:
        ValueError: If list is empty or any element not in allowed values
    """
    if not value:
        allowed_str = ', '.join(str(av) for av in allowed_values)
        raise ValueError(
            f"Empty list not allowed for parameter '{param_name}'. "
            f"Must provide at least one value from: {allowed_str}"
        )
    
    if isinstance(value, (list, tuple)):
        for element in value:
            if _normalise_text_to_allowed_case(element, allowed_values) is None:
                allowed_str = ', '.join(str(av) for av in allowed_values)
                raise ValueError(
                    f"List element '{element}' not allowed for parameter '{param_name}'. "
                    f"Allowed values: {allowed_str}"
                )


def _validate_number_allowed_values(param_name, value, allowed_values):
    """Validate NUMBER parameter value against allowed values with exact match.
    
    Args:
        param_name: Parameter name for error messages
        value: Numeric value to validate
        allowed_values: List of allowed numeric values
        
    Raises:
        ValueError: If value not in allowed values list
    """
    if value not in allowed_values:
        allowed_str = ', '.join(str(av) for av in allowed_values)
        raise ValueError(
            f"Value {value} not allowed for parameter '{param_name}'. "
            f"Allowed values: {allowed_str}"
        )


def _validate_allowed_values(param_definition, value):
    """Validate value against allowed values list if specified.
    
    Checks if the parameter has PARAM_ALLOWED_VALUES defined and validates
    that the provided value is in the allowed list. Delegates to type-specific
    handlers for TEXT, NUMBER, and LIST parameters.
    
    Does not modify the value - raises ValueError if validation fails.
    
    Args:
        param_definition: Parameter definition dict
        value: Value to validate (single value for TEXT/NUMBER, list for LIST)
        
    Raises:
        ValueError: If value is not in allowed values list
    """
    allowed_values = param_definition.get(PARAM_ALLOWED_VALUES)
    if allowed_values is None:
        return
    
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    param_name = param_definition.get(PARAM_NAME, 'unknown')
    
    # Only validate TEXT, NUMBER, and LIST params
    if param_type not in (PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_LIST):
        return
    
    # Delegate to type-specific validator
    if param_type == PARAM_TYPE_LIST:
        _validate_list_allowed_values(param_name, value, allowed_values)
    elif param_type == PARAM_TYPE_TEXT:
        _validate_text_allowed_values(param_name, value, allowed_values)
    elif param_type == PARAM_TYPE_NUMBER:
        _validate_number_allowed_values(param_name, value, allowed_values)


def _normalise_allowed_value(param_definition, value):
    """Normalise value to canonical case from allowed values list.
    
    For TEXT parameters, returns the canonical case from PARAM_ALLOWED_VALUES.
    For LIST parameters, returns list with each element normalised to canonical case.
    For NUMBER parameters and others, returns value unchanged.
    
    Should only be called after _validate_allowed_values() has confirmed the value is valid.
    
    Args:
        param_definition: Parameter definition dict
        value: Value to normalise (must be valid)
        
    Returns:
        Normalised value with canonical case
    """
    allowed_values = param_definition.get(PARAM_ALLOWED_VALUES)
    if allowed_values is None:
        return value
    
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # Normalise LIST elements to canonical case
    if param_type == PARAM_TYPE_LIST:
        normalised_list = []
        if isinstance(value, (list, tuple)):
            for element in value:
                canonical = _normalise_text_to_allowed_case(element, allowed_values)
                normalised_list.append(canonical)
        return normalised_list
    
    # Normalise TEXT to canonical case
    if param_type == PARAM_TYPE_TEXT:
        return _normalise_text_to_allowed_case(value, allowed_values)
    
    # NUMBER and others - no normalisation needed
    return value


def _default_filter_number(value):
    """Default input filter for NUMBER params - parse int or float."""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Cannot coerce value to number: {value}")


def _default_filter_toggle(value):
    """Default input filter for TOGGLE params - passthrough (no conversion needed).
    
    Toggles are handled specially by set_param_value - the filter just passes
    the value through unchanged. The toggle logic handles None vs provided values.
    """
    return value


def _default_filter_list(value):
    """Default input filter for LIST params - split using shlex."""
    import shlex
    return shlex.split(value)


def _normalize_json_quotes(value):
    """Normalize single-quoted JSON to double-quoted JSON.
    
    Converts single quotes used for JSON structure to double quotes,
    while preserving apostrophes within string values and escaping
    any internal double quotes.
    
    This allows shell-friendly syntax like {'key':'value'} to work
    while properly handling strings like {'name':'O'Brien'} or
    {'msg':'He said "hello"'}.
    
    Args:
        value: JSON string with single or double quotes
        
    Returns:
        JSON string with double quotes for structure
    """
    result = []
    in_string = False
    escape_next = False
    string_delimiter = None
    
    for index, char in enumerate(value):
        if escape_next:
            result.append(char)
            escape_next = False
            continue
            
        if char == '\\':
            result.append(char)
            escape_next = True
            continue
        
        # Track whether we're inside a string
        if char in ('"', "'"):
            if not in_string:
                # Starting a string
                in_string = True
                string_delimiter = char
                result.append('"')  # Always use double quotes
            elif char == string_delimiter:
                # Ending the string with matching delimiter
                in_string = False
                string_delimiter = None
                result.append('"')  # Always use double quotes
            else:
                # It's the opposite quote inside a string
                # If we started with single quote and find double quote inside, escape it
                if string_delimiter == "'" and char == '"':
                    result.append('\\')
                result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)


def _split_top_level_json_objects(text):
    """Split text into separate top-level JSON objects.
    
    Detects multiple adjacent JSON objects like {"a":1} {"b":2} by tracking
    brace depth. Only splits at depth 0 (between top-level objects), not
    within nested structures. Non-object JSON (arrays, primitives) are
    returned as single blocks for downstream validation.
    
    Args:
        text: String potentially containing multiple JSON objects
        
    Returns:
        List of JSON object strings. Returns single-item list if only one object.
    """
    blocks = []
    current_block = []
    brace_depth = 0
    bracket_depth = 0
    in_string = False
    string_delimiter = None
    escape_next = False
    found_any_structure = False
    
    for char in text:
        # Handle escape sequences in strings
        if escape_next:
            current_block.append(char)
            escape_next = False
            continue
            
        if char == '\\':
            current_block.append(char)
            escape_next = True
            continue
        
        # Track string state
        if char in ('"', "'"):
            if not in_string:
                in_string = True
                string_delimiter = char
            elif char == string_delimiter:
                in_string = False
                string_delimiter = None
        
        # Track brace and bracket depth only outside strings
        if not in_string:
            if char == '{':
                brace_depth += 1
                found_any_structure = True
            elif char == '}':
                brace_depth -= 1
            elif char == '[':
                bracket_depth += 1
                found_any_structure = True
            elif char == ']':
                bracket_depth -= 1
        
        current_block.append(char)
        
        # When depth returns to 0 AND we found JSON structures, we've completed a top-level item
        # Only split on brace completion (objects), not brackets (arrays should be single block)
        if brace_depth == 0 and bracket_depth == 0 and len(current_block) > 0 and found_any_structure:
            block_text = ''.join(current_block).strip()
            if block_text and block_text.startswith('{'):
                # Only treat as separate block if it's an object
                blocks.append(block_text)
                current_block = []
                found_any_structure = False
    
    # Handle any remaining content
    if current_block:
        block_text = ''.join(current_block).strip()
        if block_text:
            blocks.append(block_text)
    
    return blocks if blocks else [text]


def _default_filter_dict(value):
    """Default input filter for DICT params - parse JSON.
    
    Accepts both single and double quoted JSON (common in shell args).
    Converts single quotes to double quotes before parsing while preserving
    apostrophes within string values.
    """
    import json
    
    # Normalize single quotes to double quotes for JSON parsing
    # This allows shell-friendly syntax like {'a':1} to work
    normalized = _normalize_json_quotes(value)
    
    try:
        parsed = json.loads(normalized)
    except json.JSONDecodeError as parse_error:
        raise ValueError("Invalid JSON for dict parameter: {}".format(str(parse_error)))
    
    if not isinstance(parsed, dict):
        raise ValueError("Dict parameter requires JSON object, got {}".format(type(parsed).__name__))
    return parsed


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
    if isinstance(value, list) and not _is_param_type(param, PARAM_TYPE_LIST):
        value = ' '.join(value)

    if _is_param_type(param, PARAM_TYPE_NUMBER):
        return _validate_number(value)
    elif _is_toggle_param(param):
        return not bool(param.get(PARAM_DEFAULT, False))
    elif _is_param_type(param, PARAM_TYPE_LIST):
        if not isinstance(value, list):
            return [value]
        return value
    elif _is_param_type(param, PARAM_TYPE_DICT):
        return _validate_dict(value)
    else:
        return value

def _add_param_xor(param_name, xor_param_name):
    if param_name not in _xor_list:
        _xor_list[param_name] = [ xor_param_name]
        return
    if xor_param_name not in _xor_list[param_name]:
        _xor_list[param_name].append(xor_param_name)

def get_xor_params(param_name):
    """Get list of params that are mutually exclusive with given param.
    
    Args:
        param_name: Bind name of the parameter.
        
    Returns:
        List of param names that are mutually exclusive with this param.
    """
    return _xor_list.get(param_name, [])

def _set_param_xor_list(param_name, xor_list):
    for xor_param_name in xor_list:
        _add_param_xor(param_name, xor_param_name)
        _add_param_xor(xor_param_name, param_name)


def has_xor_with(param_name, other_param_name):
    return other_param_name in _xor_list.get(param_name, [])


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
def get_param_by_alias(alias):
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

def is_param_alias(_param, alias):
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

def add_param(_param):
    """Add a parameter and activate it immediately.
    
    Args:
        _param: Parameter definition dictionary with keys like
                PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, etc.
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
    
    # Assign default input filter if not specified
    if PARAM_INPUT_FILTER not in _param:
        param_type = _param.get(PARAM_TYPE, PARAM_TYPE_TEXT)
        # Look up the filter function name from the constants dict
        filter_func_name = PARAM_DEFAULT_INPUT_FILTERS.get(param_type)
        if filter_func_name:
            # Resolve the function from this module's globals
            _param[PARAM_INPUT_FILTER] = globals()[filter_func_name]
    
    # Validate default value is in allowed values and store normalised value
    default_value = _param.get(PARAM_DEFAULT)
    if default_value is not None:
        _validate_allowed_values(_param, default_value)
        normalised_default = _normalise_allowed_value(_param, default_value)
        # Update param with normalised default (canonical case for TEXT, normalised list for LIST)
        _param[PARAM_DEFAULT] = normalised_default
    
    if _param.get(PARAM_RUNTIME_ONLY, False):
        _param[PARAM_PERSISTENCE] = PARAM_PERSISTENCE_NEVER
    _params[_param_name] = _param


def _register_param_alias(param, alias):
    """Register an alias for a parameter.
    
    Args:
        param: Parameter dictionary.
        alias: Alias string to register.
    """
    if not is_alias(alias):
        raise ValueError(f"Invalid alias format: {alias}")
    _param_aliases[alias] = param[PARAM_NAME]


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

def add_params(params):
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

def _get_param_value(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Internal helper to retrieve raw parameter value from configuration.
    
    This is a private method used internally by the param layer. External code
    should use get_param() which provides automatic type coercion.
    
    Resolves parameter using param_name, bind_name, or alias with failover logic,
    then retrieves the value from internal configuration. Returns default if not found
    unless strict mode is enabled.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found (default: None)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
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
    
    config_key = _get_bind_name(param_definition)
    value = config.get_config_value(config_key)
    
    if value is None:
        if strict:
            raise ValueError("Parameter '{}' not found in configuration".format(config_key))
        return default
    
    return value


def _get_param_str(param_name=None, bind_name=None, alias=None, default='', strict=False):
    """
    Retrieve string parameter value with type coercion.
    
    Gets raw value via get_param_value() and coerces to string using str().
    Any value type can be converted to string representation.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found (default: '')
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The value coerced to string, or default if not found
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    value = _get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )
    
    if value is None:
        return default
    return str(value)


def _get_param_int(param_name=None, bind_name=None, alias=None, default=0, strict=False):
    """
    Retrieve integer parameter value with type coercion and truncation.
    
    Gets raw value via get_param_value() and coerces to int via int(float(value))
    for truncation behaviour. In strict mode, raises ValueError on coercion failure.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found or coercion fails (default: 0)
        strict: If True, raises ValueError on coercion failure (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The value coerced to int (truncated), or default if not found or coercion fails
    
    Raises:
        ValueError: If strict=True and coercion fails
    """
    value = _get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=False  # Handle strict mode ourselves after coercion
    )
    
    if value is None:
        return default
    
    try:
        # Use int(float(value)) for truncation behaviour
        return int(float(value))
    except (ValueError, TypeError) as error:
        if strict:
            raise ValueError("Cannot convert '{}' to int: {}".format(value, error))
        return default


def _get_param_bool(param_name=None, bind_name=None, alias=None, default=False, strict=False):
    """
    Retrieve boolean parameter value with truthiness coercion.
    
    Gets raw value via get_param_value() and coerces using Python's bool()
    for truthy/falsy evaluation. Non-empty strings, non-zero numbers, and
    non-empty collections are True; empty values are False.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found (default: False)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The value coerced to boolean, or default if not found
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    value = _get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )
    
    if value is None:
        return default
    return bool(value)


def _get_param_float(param_name=None, bind_name=None, alias=None, default=0.0, strict=False):
    """
    Retrieve float parameter value with type coercion.
    
    Gets raw value via get_param_value() and coerces to float using float().
    In strict mode, raises ValueError on coercion failure.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found or coercion fails (default: 0.0)
        strict: If True, raises ValueError on coercion failure (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The value coerced to float, or default if not found or coercion fails
    
    Raises:
        ValueError: If strict=True and coercion fails
    """
    value = _get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=False  # Handle strict mode ourselves after coercion
    )
    
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError) as error:
        if strict:
            raise ValueError("Cannot convert '{}' to float: {}".format(value, error))
        return default


def _get_param_list(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Retrieve list parameter value without coercion.
    
    Gets raw value via get_param_value() and returns as-is. Defaults to empty list
    if not found and no explicit default provided. Does not perform type coercion.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found (default: empty list)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The value as-is, or empty list if not found and no default provided
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    if default is None:
        default = []
    
    return _get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )


def _get_param_dict(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Retrieve dict parameter value without coercion.
    
    Gets raw value via get_param_value() and returns as-is. Defaults to empty dict
    if not found and no explicit default provided. Does not perform type coercion.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found (default: empty dict)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The value as-is, or empty dict if not found and no default provided
    
    Raises:
        ValueError: If strict=True and parameter not found
    """
    if default is None:
        default = {}
    
    return _get_param_value(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias,
        default=default,
        strict=strict
    )


def get_param(param_name=None, bind_name=None, alias=None, default=None, strict=False):
    """
    Retrieve parameter value with automatic type coercion based on parameter definition.
    
    This is the primary facade method for retrieving parameter values. It automatically
    determines the parameter type from the definition and calls the appropriate typed
    getter (_get_param_str, _get_param_int, etc.) to return a properly coerced value.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        default: Value to return if parameter not found (default: None)
        strict: If True, raises ValueError when parameter not found (default: False)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Returns:
        The parameter value coerced to the appropriate type based on PARAM_TYPE,
        or default if not found
    
    Raises:
        ValueError: If strict=True and parameter not found, or if parameter definition not found
    
    Example:
        >>> get_param('database-host')  # Returns string value
        'localhost'
        >>> get_param('port')  # Returns int value based on PARAM_TYPE
        5432
        >>> get_param('verbose')  # Returns bool value
        True
    """
    # Resolve parameter definition to determine type
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    
    if not param_def:
        if strict:
            raise ValueError("Parameter definition not found for param_name={}, bind_name={}, alias={}".format(
                param_name, bind_name, alias))
        return default
    
    # Get parameter type from definition
    param_type = param_def.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # Route to appropriate typed getter based on parameter type
    if param_type == PARAM_TYPE_NUMBER:
        # Number params could be int or float, use int getter for consistency
        return _get_param_int(param_name=param_name, bind_name=bind_name, alias=alias, default=default, strict=strict)
    elif param_type == PARAM_TYPE_TOGGLE:
        return _get_param_bool(param_name=param_name, bind_name=bind_name, alias=alias, default=default, strict=strict)
    elif param_type == PARAM_TYPE_LIST:
        return _get_param_list(param_name=param_name, bind_name=bind_name, alias=alias, default=default, strict=strict)
    elif param_type == PARAM_TYPE_DICT:
        return _get_param_dict(param_name=param_name, bind_name=bind_name, alias=alias, default=default, strict=strict)
    else:  # PARAM_TYPE_TEXT or unknown
        return _get_param_str(param_name=param_name, bind_name=bind_name, alias=alias, default=default, strict=strict)


def _validate_toggle(value):
    """Validate TOGGLE parameter by converting to bool."""
    return bool(value)


# Type validator lookup dict - maps param types to validation functions
_TYPE_VALIDATORS = {
    PARAM_TYPE_NUMBER: _validate_number,
    PARAM_TYPE_TOGGLE: _validate_toggle,
    PARAM_TYPE_LIST: _validate_list,
    PARAM_TYPE_DICT: _validate_dict,
    PARAM_TYPE_TEXT: _validate_text,
}


def _validate_param_value(param_definition, value, strict=True):
    """
    Validate and coerce value according to parameter type definition.
    
    Applies type-specific validation using existing validation helpers. In strict
    mode, raises ValueError for validation failures. In non-strict mode, attempts
    best-effort coercion.
    
    Args:
        param_definition: Parameter definition dict containing type information
        value: Value to validate and potentially coerce
        strict: If True, raises ValueError on validation failure (default: True)
    
    Returns:
        Validated and potentially coerced value appropriate for the parameter type
    
    Raises:
        ValueError: If strict=True and validation fails
    """
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # Type validation using lookup dict
    validator = _TYPE_VALIDATORS.get(param_type)
    if validator:
        validated_value = validator(value)
    else:
        validated_value = value
    
    # Allowed values validation (TEXT/NUMBER/LIST)
    _validate_allowed_values(param_definition, validated_value)
    
    # Normalisation to canonical case (TEXT/LIST only)
    normalised_value = _normalise_allowed_value(param_definition, validated_value)
    
    return normalised_value


def _validate_xor_conflicts(param_definition, value_to_set):
    """
    Check for XOR conflicts when setting any parameter with a switch list.
    
    Verifies that no mutually exclusive parameter is already set in configuration.
    For parameters with PARAM_SWITCH_LIST defined, checks if any other parameter
    in the same switch-list is currently set.
    
    For toggle params: only checks conflict when setting to True (enabling).
                       Setting to False is allowed (disabling doesn't conflict).
    For other types: checks conflict if value is not None (setting any value).
    
    Args:
        param_definition: Parameter definition dict to check for conflicts
        value_to_set: The value that will be set for this parameter
    
    Raises:
        ValueError: If a conflicting parameter is already set
    """
    bind_name = _get_bind_name(param_definition)
    xor_params = get_xor_params(bind_name)
    
    if not xor_params:
        return
    
    # For toggles being set to False, skip XOR check (disabling doesn't conflict)
    if _is_toggle_param(param_definition):
        if not value_to_set:
            return  # Setting to False - no conflict possible
        # Setting to True - check if any XOR toggle is already True
        for xor_param_bind_name in xor_params:
            if xor_param_bind_name == bind_name:
                continue
            existing_value = config.get_config_value(xor_param_bind_name)
            if existing_value is True:
                raise ValueError(
                    "Cannot set '{}', conflicts with '{}'".format(bind_name, xor_param_bind_name)
                )
    else:
        # For non-toggle params, check if any XOR param is already set (not None)
        for xor_param_bind_name in xor_params:
            if xor_param_bind_name == bind_name:
                continue
            existing_value = config.get_config_value(xor_param_bind_name)
            if existing_value is not None:
                raise ValueError(
                    "Conflicting parameters provided: {} and {}".format(bind_name, xor_param_bind_name)
                )


def set_param(param_name=None, bind_name=None, alias=None, value=None):
    """
    Set parameter value with flexible resolution and type validation.
    
    Resolves parameter using param_name, bind_name, or alias with failover logic,
    validates the value against parameter type, checks XOR conflicts for toggles,
    and stores the validated value in configuration.
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        value: Value to set (required)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
        
        XOR validation can be disabled globally using _set_xor_validation_enabled(False)
        when loading defaults or configuration files.
    
    Raises:
        ValueError: If parameter not found, validation fails, or XOR conflict detected
    """
    param_definition = _resolve_param_definition(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias
    )
    
    if param_definition is None:
        raise ValueError("Unknown parameter: '{}'".format(param_name or bind_name or alias))
    
    # Check immutability - allow initial set, block modification
    _check_immutable(param_definition)
    
    # Apply input filter if value is a non-None string
    if value is not None and isinstance(value, str) and PARAM_INPUT_FILTER in param_definition:
        input_filter = param_definition[PARAM_INPUT_FILTER]
        value = input_filter(value)
    
    # Handle toggle parameters: use provided value directly for programmatic setting
    # (CLI layer passes True when toggle is present, we use that value as-is)
    if _is_toggle_param(param_definition):
        # If value is explicitly provided, use it; otherwise flip the default
        if value is None:
            validated_value = not bool(param_definition.get(PARAM_DEFAULT, False))
        else:
            validated_value = bool(value)
    else:
        # Validate and coerce value according to parameter type
        validated_value = _validate_param_value(param_definition, value, strict=True)
    
    # If param is in a switch list, check for XOR conflicts BEFORE setting value
    # This check respects the global _skip_xor_validation flag set via _set_xor_validation_enabled()
    if not _skip_xor_validation and len(param_definition.get(PARAM_SWITCH_LIST, [])) > 0:
        _validate_xor_conflicts(param_definition, validated_value)
    
    # Log the parameter setting at DEBUG level
    param_name_for_log = param_definition[PARAM_NAME]
    logging.log_debug(_message="Set param '{}' = {}".format(param_name_for_log, validated_value))
    
    # Store value using bind name as config key
    config_key = _get_bind_name(param_definition)
    config.set_config_value(config_key, validated_value)
    
    # Notify persistence layer about the change
    notify_persistence_change(param_definition[PARAM_NAME], validated_value)


def _join_string_value(existing, new, separator):
    """
    Join string values with separator.
    
    Concatenates string values using the specified separator. If no existing value,
    returns the new value as-is.
    
    Args:
        existing: Existing string value or None
        new: New string value to join
        separator: Separator string to use
    
    Returns:
        Concatenated string or new value if existing is None
    """
    if existing is None:
        return str(new)
    return str(existing) + separator + str(new)


def _join_list_value(existing, new):
    """
    Join list values by appending or extending.
    
    If new value is a list, extends existing list. If new value is single value,
    appends to existing list. Creates new list if existing is None.
    
    Args:
        existing: Existing list value or None
        new: New value to join (single value or list)
    
    Returns:
        Updated list with new values appended/extended
    """
    if existing is None:
        existing = []
    
    # Ensure existing is a list (might be string from validation)
    if not isinstance(existing, list):
        existing = [existing]
    
    if isinstance(new, list):
        existing.extend(new)
    else:
        existing.append(new)
    
    return existing


def _deep_merge_dicts(dict1, dict2, override_strategy):
    """
    Recursively merge two dictionaries with override strategy.
    
    Merges nested dictionaries at all levels, applying the override strategy
    when keys conflict. If both values are dicts, recurses. Otherwise applies
    strategy to determine which value to keep.
    
    Args:
        dict1: First dictionary (existing)
        dict2: Second dictionary (new)
        override_strategy: One of DICT_OVERRIDE_RECENT, DICT_OVERRIDE_OLDEST, DICT_OVERRIDE_ERROR
    
    Returns:
        Merged dictionary
    
    Raises:
        ValueError: If override_strategy is ERROR and keys conflict
    """
    result = dict1.copy()
    
    for key, value2 in dict2.items():
        if key in result:
            value1 = result[key]
            
            # If both values are dicts, recurse
            if isinstance(value1, dict) and isinstance(value2, dict):
                result[key] = _deep_merge_dicts(value1, value2, override_strategy)
            else:
                # Apply override strategy for non-dict conflicts
                if override_strategy == DICT_OVERRIDE_ERROR:
                    raise ValueError("Dict key collision on key '{}'".format(key))
                elif override_strategy == DICT_OVERRIDE_OLDEST:
                    # Keep existing value (value1), do nothing
                    pass
                else:  # DICT_OVERRIDE_RECENT (default)
                    result[key] = value2
        else:
            # No conflict, add new key
            result[key] = value2
    
    return result


def _join_dict_value(existing, new, param_definition):
    """
    Join dict values with configurable merge strategy.
    
    Merges dictionaries using either shallow or deep merge based on
    PARAM_DICT_MERGE_TYPE configuration. Applies override strategy from
    PARAM_DICT_OVERRIDE_STRATEGY when keys conflict.
    
    Args:
        existing: Existing dict value or None
        new: New dict value to merge
        param_definition: Parameter definition with merge configuration
    
    Returns:
        Merged dictionary
    
    Raises:
        ValueError: If override strategy is ERROR and keys conflict
    """
    if existing is None:
        return new
    
    merge_type = param_definition.get(PARAM_DICT_MERGE_TYPE, DICT_MERGE_SHALLOW)
    override_strategy = param_definition.get(PARAM_DICT_OVERRIDE_STRATEGY, DICT_OVERRIDE_RECENT)
    
    if merge_type == DICT_MERGE_DEEP:
        return _deep_merge_dicts(existing, new, override_strategy)
    else:  # DICT_MERGE_SHALLOW (default)
        # Shallow merge with override strategy
        result = existing.copy()
        
        for key, value in new.items():
            if key in result:
                if override_strategy == DICT_OVERRIDE_ERROR:
                    raise ValueError("Dict key collision on key '{}'".format(key))
                elif override_strategy == DICT_OVERRIDE_OLDEST:
                    # Keep existing value, do nothing
                    pass
                else:  # DICT_OVERRIDE_RECENT (default)
                    result[key] = value
            else:
                # No conflict, add new key
                result[key] = value
        
        return result


def join_param(param_name=None, bind_name=None, alias=None, value=None):
    """
    Join/accumulate parameter value with type-specific logic.
    
    Resolves parameter using param_name, bind_name, or alias with failover logic,
    then accumulates the value using type-specific joining:
    - String: concatenates with separator
    - List: appends or extends
    - Dict: merges with configurable strategy
    
    Args:
        param_name: Parameter's PARAM_NAME (use this in application code)
        bind_name: Parameter's PARAM_CONFIG_NAME (advanced use, for internal config key)
        alias: Any of the parameter's PARAM_ALIASES without prefix (advanced use)
        value: Value to join/append (required)
    
    Note:
        At least one of param_name, bind_name, or alias must be provided.
        In most cases, use param_name with the parameter's PARAM_NAME.
    
    Raises:
        ValueError: If parameter not found or type doesn't support joining (number/toggle)
    """
    param_definition = _resolve_param_definition(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias
    )
    
    if param_definition is None:
        raise ValueError("Unknown parameter: '{}'".format(param_name or bind_name or alias))
    
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # For dict params, check for multiple JSON blocks BEFORE applying filter
    if param_type == PARAM_TYPE_DICT and isinstance(value, str):
        json_blocks = _split_top_level_json_objects(value)
        
        # If multiple JSON blocks detected, recurse for each
        if len(json_blocks) > 1:
            for block in json_blocks:
                join_param(param_name=param_name, bind_name=bind_name, alias=alias, value=block)
            return
    
    # Apply input filter if value is a non-None string
    if value is not None and isinstance(value, str) and PARAM_INPUT_FILTER in param_definition:
        input_filter = param_definition[PARAM_INPUT_FILTER]
        value = input_filter(value)
    
    # Validate that type supports joining
    if param_type == PARAM_TYPE_NUMBER:
        raise ValueError("Cannot join values for number parameter")
    if param_type == PARAM_TYPE_TOGGLE:
        raise ValueError("Cannot join values for toggle parameter")
    
    # Get config key and current value
    config_key = _get_bind_name(param_definition)
    existing_value = config.get_config_value(config_key)
    
    # Validate/parse the new value according to type
    if param_type == PARAM_TYPE_DICT:
        value = _validate_dict(value)
        joined_value = _join_dict_value(existing_value, value, param_definition)
    elif param_type == PARAM_TYPE_LIST:
        value = _validate_list(value)
        joined_value = _join_list_value(existing_value, value)
    elif param_type == PARAM_TYPE_TEXT:
        value = _validate_text(value)
        separator = param_definition.get(PARAM_JOIN_SEPARATOR, SEPARATOR_SPACE)
        joined_value = _join_string_value(existing_value, value, separator)
    else:
        joined_value = value
    
    # Store updated value
    config.set_config_value(config_key, joined_value)


def _check_immutable(param_def):
    """Check if parameter is immutable and has a value, raise error if so.
    
    Private helper for set_param() and unset_param() to enforce immutability.
    Blocks modification/removal only if parameter is immutable AND value exists.
    
    Args:
        param_def: Parameter definition dict.
    
    Raises:
        ValueError: If parameter is immutable and value already exists.
    """
    if not param_def.get(PARAM_IMMUTABLE, False):
        return  # Not immutable, allow operation
    
    # Check if value exists
    config_bind_name = _get_bind_name(param_def)
    if not config.has_config_value(config_bind_name):
        return  # No value yet, allow initial assignment
    
    # Immutable and has value - block operation
    param_display_name = param_def.get(PARAM_NAME)
    raise ValueError(f"Cannot modify immutable parameter '{param_display_name}'")


def unset_param(param_name=None, bind_name=None, alias=None):
    """Unset (remove) a parameter value from config.
    
    Completely removes the parameter value from the config dictionary.
    Respects PARAM_IMMUTABLE flag - raises ValueError if param is immutable.
    
    Args:
        param_name: Parameter name to unset.
        bind_name: Config bind name to unset.
        alias: Parameter alias to unset.
    
    Raises:
        ValueError: If parameter not found or parameter is immutable.
    
    Example:
        unset_param(param_name='temp-value')
        unset_param(bind_name='runtime_state')
        unset_param(alias='--debug')
    """
    # Resolve param definition using existing helper
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    
    if not param_def:
        # Build error message with what was provided
        identifier = param_name or bind_name or alias
        raise ValueError(f"Parameter '{identifier}' not found")
    
    # Check immutability immediately after resolution
    _check_immutable(param_def)
    
    # Get config bind name
    config_bind_name = _get_bind_name(param_def)
    
    # Remove from config dict
    config.remove_config_value(config_bind_name)


def reset_param(param_name=None, bind_name=None, alias=None):
    """Reset a parameter to its default value, or unset it if no default exists.
    
    If the parameter has a PARAM_DEFAULT defined, sets the value to that default.
    If no default exists, removes the parameter value from config (same as unset).
    Respects PARAM_IMMUTABLE flag - raises ValueError if param is immutable.
    
    Args:
        param_name: Parameter name to reset.
        bind_name: Config bind name to reset.
        alias: Parameter alias to reset.
    
    Raises:
        ValueError: If parameter not found or parameter is immutable.
    
    Example:
        reset_param(param_name='counter')  # Resets to PARAM_DEFAULT or unsets
        reset_param(bind_name='log_level')  # Resets to default log level
        reset_param(alias='--verbose')  # Resets verbose flag to default
    """
    # Resolve param definition using existing helper
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    
    if not param_def:
        # Build error message with what was provided
        identifier = param_name or bind_name or alias
        raise ValueError(f"Parameter '{identifier}' not found")
    
    # Reset the parameter - set to default or unset if no default
    # Note: Immutability check done by _check_immutable() via set_param/unset_param
    if PARAM_DEFAULT in param_def:
        # Has default - use set_param to set default value
        default_value = param_def[PARAM_DEFAULT]
        set_param(param_name=param_name, bind_name=bind_name, alias=alias, value=default_value)
    else:
        # No default - use unset_param to remove
        unset_param(param_name=param_name, bind_name=bind_name, alias=alias)
