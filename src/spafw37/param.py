import re
from typing import List, Dict, Any, Optional

from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_RUNTIME_ONLY,
    PARAM_DEFERRED,
    PARAM_RUN_LEVEL,
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
from spafw37.constants.runlevel import (
    RUN_LEVEL_NAME,
    RUN_LEVEL_PARAMS,
    RUN_LEVEL_COMMANDS,
    RUN_LEVEL_CONFIG,
    RUN_LEVEL_ERROR_HANDLER,
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

# Run-level definitions (list to maintain order)
_run_levels = []

# Default error handler for run-level processing
def _default_run_level_error_handler(run_level_name, error):
    """Default error handler for run-level execution.
    
    Logs the error and re-raises it.
    
    Args:
        run_level_name: Name of the run-level being processed.
        error: The exception that occurred.
    """
    import sys
    print(f"Error processing run-level '{run_level_name}': {error}", file=sys.stderr)
    raise error

# Current error handler (can be customized)
_run_level_error_handler = _default_run_level_error_handler


def set_run_level_error_handler(handler):
    """Set a custom error handler for run-level processing.
    
    Args:
        handler: A callable that takes (run_level, error) and handles the error.
    """
    global _run_level_error_handler
    _run_level_error_handler = handler


def get_run_level_error_handler():
    """Get the current run-level error handler.
    
    Returns:
        The current error handler function.
    """
    return _run_level_error_handler


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


def add_run_level(run_level_dict):
    """Register a run-level definition.
    
    A run-level sandboxes parts of configuration to run in isolation with
    defined sets of params, commands, and preset config values.
    
    Args:
        run_level_dict: Dictionary with structure:
            {
                RUN_LEVEL_NAME: 'name',
                RUN_LEVEL_PARAMS: [],  # List of param bind names for this level
                RUN_LEVEL_COMMANDS: [],  # List of commands for this level
                RUN_LEVEL_CONFIG: {},  # Dict of config name-value pairs
                RUN_LEVEL_ERROR_HANDLER: handler_func  # Optional
            }
    """
    if RUN_LEVEL_NAME not in run_level_dict:
        raise ValueError("Run-level definition must include RUN_LEVEL_NAME")
    
    _run_levels.append(dict(run_level_dict))


def get_run_level(name):
    """Get a run-level definition by name.
    
    Args:
        name: Name of the run-level.
        
    Returns:
        Run-level dictionary, or None if not found.
    """
    for run_level in _run_levels:
        if run_level.get(RUN_LEVEL_NAME) == name:
            return run_level
    return None


def list_run_levels():
    """Get list of all registered run-level names in order.
    
    Returns:
        List of run-level names in registration order.
    """
    return [rl.get(RUN_LEVEL_NAME) for rl in _run_levels]


def get_all_run_levels():
    """Get all run-level definitions in order.
    
    Returns:
        List of run-level dictionaries in registration order.
    """
    return list(_run_levels)


def build_params_for_run_level(run_level_name=None):
    """Process buffered parameters and register them.
    
    This flushes the buffered parameter list and adds them to the
    active parameter registry. If a run_level_name is specified, only
    registers params listed in that run-level's RUN_LEVEL_PARAMS.
    
    Args:
        run_level_name: Name of run-level, or None to register all buffered params.
    """
    run_level = get_run_level(run_level_name) if run_level_name else None
    error_handler = _run_level_error_handler
    
    if run_level and RUN_LEVEL_ERROR_HANDLER in run_level:
        error_handler = run_level[RUN_LEVEL_ERROR_HANDLER]
    
    try:
        # Get the list of params to register for this run-level
        allowed_params = None
        if run_level and RUN_LEVEL_PARAMS in run_level:
            param_list = run_level[RUN_LEVEL_PARAMS]
            # Empty list means all params, non-empty list filters
            if param_list:
                allowed_params = set(param_list)
        
        # Note: All params are now activated immediately by add_param,
        # so this function no longer needs to activate buffered params.
        # It only validates run-level configuration.
        
    except Exception as e:
        if run_level_name:
            error_handler(run_level_name, e)
        else:
            raise


def apply_run_level_config(run_level_name):
    """Apply run-level config values to already-registered parameters.
    
    This updates the default values of registered params without
    re-registering them. Only affects params listed in the run-level's
    RUN_LEVEL_PARAMS (if specified).
    
    Args:
        run_level_name: Name of run-level to apply.
    """
    run_level = get_run_level(run_level_name)
    if not run_level:
        return
    
    error_handler = _run_level_error_handler
    if RUN_LEVEL_ERROR_HANDLER in run_level:
        error_handler = run_level[RUN_LEVEL_ERROR_HANDLER]
    
    try:
        config = run_level.get(RUN_LEVEL_CONFIG, {})
        if not config:
            return
        
        allowed_params = set(run_level.get(RUN_LEVEL_PARAMS, [])) if RUN_LEVEL_PARAMS in run_level else None
        
        for param_name, param in _params.items():
            bind_name = param.get(PARAM_CONFIG_NAME, param_name)
            
            # Skip params not in this run-level's param list
            if allowed_params is not None and bind_name not in allowed_params:
                continue
            
            if bind_name in config:
                param[PARAM_DEFAULT] = config[bind_name]
    except Exception as e:
        error_handler(run_level_name, e)


def get_buffered_params():
    """Get the list of buffered parameters.
    
    Note: Buffered params concept has been removed. This function
    now returns an empty list for backwards compatibility.
    
    Returns:
        Empty list.
    """
    return []


def assign_orphans_to_default_run_level():
    """Pre-parse check that assigns orphan params/commands to default run-level.
    
    This function:
    1. Finds the default run-level
    2. For each param without PARAM_RUN_LEVEL, assigns it to default
    3. For each command without COMMAND_RUN_LEVEL, assigns it to default
    4. Creates bidirectional relationships by updating run-level param/command lists
    
    Note: Now that params are activated immediately, this processes already-activated params.
    """
    from .command import get_all_commands
    from .config_func import get_default_run_level
    from .constants.command import COMMAND_NAME, COMMAND_RUN_LEVEL
    
    # Get the default run-level name
    default_run_level_name = get_default_run_level()
    
    # Find the default run-level
    default_run_level = get_run_level(default_run_level_name)
    
    if not default_run_level:
        # No default run-level found, nothing to do
        return
    
    # Get or initialize param/command lists
    if RUN_LEVEL_PARAMS not in default_run_level:
        default_run_level[RUN_LEVEL_PARAMS] = []
    if RUN_LEVEL_COMMANDS not in default_run_level:
        default_run_level[RUN_LEVEL_COMMANDS] = []
    
    default_params = default_run_level[RUN_LEVEL_PARAMS]
    default_commands = default_run_level[RUN_LEVEL_COMMANDS]
    
    # Process all activated params
    for param_name, param in _params.items():
        if PARAM_RUN_LEVEL not in param or not param[PARAM_RUN_LEVEL]:
            # Assign to default run-level
            param[PARAM_RUN_LEVEL] = default_run_level_name
            bind_name = param.get(PARAM_CONFIG_NAME, param.get(PARAM_NAME))
            
            # Add to default run-level's param list if not already there
            if bind_name and bind_name not in default_params:
                default_params.append(bind_name)
        else:
            # Param has explicit run-level - add to that run-level's list
            run_level_name = param[PARAM_RUN_LEVEL]
            run_level = get_run_level(run_level_name)
            if run_level:
                if RUN_LEVEL_PARAMS not in run_level:
                    run_level[RUN_LEVEL_PARAMS] = []
                bind_name = param.get(PARAM_CONFIG_NAME, param.get(PARAM_NAME))
                if bind_name and bind_name not in run_level[RUN_LEVEL_PARAMS]:
                    run_level[RUN_LEVEL_PARAMS].append(bind_name)
    
    # Process commands: assign them to run-levels but don't auto-queue them
    all_commands = get_all_commands()
    for cmd_name, cmd in all_commands.items():
        # Assign commands to a run-level for categorization, but don't add them
        # to RUN_LEVEL_COMMANDS lists (which would cause them to auto-execute).
        # Commands should only execute when explicitly invoked on command line.
        if COMMAND_RUN_LEVEL not in cmd or not cmd[COMMAND_RUN_LEVEL]:
            # Assign to default run-level for categorization
            cmd[COMMAND_RUN_LEVEL] = default_run_level_name
    
    # Validate that commands don't have cross-run-level dependencies
    from .command import validate_no_cross_run_level_dependencies
    validate_no_cross_run_level_dependencies()


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



