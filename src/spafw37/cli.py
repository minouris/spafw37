import sys

from .command import run_command_queue, get_command, is_command, queue_command, has_app_commands_queued, CommandParameterError
from .config import list_config_params, set_config_value, set_config_value_from_cmdline
from .param import (
    _has_xor_with, _params, get_bind_name, get_param_default, is_alias, 
    is_list_param, is_long_alias_with_value, get_param_by_alias, _parse_value, 
    is_param_alias, is_toggle_param, param_has_default, build_params_for_run_level,
    get_all_run_levels, apply_run_level_config, assign_orphans_to_default_run_level,
    get_pre_parse_args, param_in_args
)
from .config_consts import RUN_LEVEL_NAME, RUN_LEVEL_COMMANDS, RUN_LEVEL_PARAMS, PARAM_NAME, PARAM_HAS_VALUE

# Functions to run before parsing the command line
_pre_parse_actions = []

# Functions to run after parsing the command line
_post_parse_actions = []

def add_pre_parse_action(action):
    _pre_parse_actions.append(action)

def add_pre_parse_actions(actions):
    for action in actions:
        _pre_parse_actions.append(action)

def add_post_parse_action(action):
    _post_parse_actions.append(action)

def add_post_parse_actions(actions):
    for action in actions:
        _post_parse_actions.append(action)

def _do_post_parse_actions():
    for action in _post_parse_actions:
        try:
            action()
        except Exception as e:
            # TODO: Log error
            raise e

def _do_pre_parse_actions():
    for action in _pre_parse_actions:
        try:
            action()
        except Exception as e:
            # TODO: Log error
            pass

def capture_param_values(args, param_definition):
    """Capture parameter values from argument list.
    
    Args:
        args: Remaining arguments to process.
        param_definition: Parameter definition dictionary.
        
    Returns:
        Tuple of (offset, value) where offset is args consumed, value is parsed result.
    """
    if is_toggle_param(param_definition):
        return 1, True
    
    values = []
    argument_index = 0
    base_offset = 1
    arguments_count = len(args)
    
    while argument_index < arguments_count:
        argument = args[argument_index]
        
        if is_command(argument) or is_long_alias_with_value(argument):
            break  # Done processing values
        
        if is_alias(argument):
            if not is_param_alias(param_definition, argument):
                break  # Done processing values for this param
            # We are capturing for the correct param, values start on next arg
            argument_index += 1
            continue
        
        if not is_list_param(param_definition):
            return base_offset + argument_index, argument
        
        values.extend([argument])
        argument_index += 1
    
    return base_offset + argument_index, values

# Module-level variable to hold original args for conflict checking
_current_args = []

def test_switch_xor(param_definition, args):
    """Test for mutually exclusive parameter conflicts.
    
    Only raises error if BOTH conflicting params were explicitly provided
    in the command-line args (not just defaults).
    
    Args:
        param_definition: Parameter definition to check for XOR conflicts.
        args: Command-line arguments list.
        
    Raises:
        ValueError: If conflicting parameters are both in args.
    """
    current_param_name = get_bind_name(param_definition)
    
    # Only check for conflicts if this param is in the args
    if not param_in_args(current_param_name, args):
        return
    
    for bind_name in list_config_params():
        if _has_xor_with(current_param_name, bind_name):
            # Only raise error if the conflicting param is also in args
            if param_in_args(bind_name, args):
                param_name = param_definition.get('name')
                raise ValueError(f"Conflicting parameters provided: {param_name} and {bind_name}")

def _parse_command_line(args):
    """Parse command-line arguments and execute commands.
    
    Iterates through arguments, handling commands and parameters.
    
    Args:
        args: List of command-line argument strings.
    """
    global _current_args
    _current_args = args  # Store for conflict checking
    
    argument_index = 0
    arguments_count = len(args)
    param_definition = None
    param_value = None
    
    while argument_index < arguments_count:
        argument = args[argument_index]
        
        if is_command(argument):
            _handle_command(argument)
            argument_index += 1
        else:
            if is_long_alias_with_value(argument):
                param_value, param_definition = _handle_long_alias_param(argument)
                argument_index += 1
            elif is_alias(argument):
                argument_index, param_definition, param_value = _handle_alias_param(args, argument_index, argument)
                # argument_index already updated by _handle_alias_param
            else:
                raise ValueError(f"Unknown argument or command: {argument}")
            
            if param_definition and param_value is not None:
                set_config_value_from_cmdline(param_definition, param_value)

def _handle_alias_param(args, argument_index, argument):
    """Handle a parameter alias argument.
    
    Args:
        args: List of all arguments.
        argument_index: Current position in args list.
        argument: The alias argument being processed.
        
    Returns:
        Tuple of (updated_index, param_definition, param_value).
    """
    param_definition = get_param_by_alias(argument)
    if not param_definition:
        raise ValueError(f"Unknown parameter alias: {argument}")
    
    test_switch_xor(param_definition, _current_args)
    
    if is_toggle_param(param_definition):
        param_value = _parse_value(param_definition, None)
        argument_index += 1  # Move past the toggle flag
    else:
        offset, param_value = capture_param_values(args[argument_index:], param_definition)
        argument_index += offset
    
    return argument_index, param_definition, param_value

def _handle_long_alias_param(argument):
    """Handle a long alias with embedded value (--param=value).
    
    Args:
        argument: The argument string containing param=value.
        
    Returns:
        Tuple of (parsed_value, param_definition).
    """
    param_alias, raw_value = argument.split('=', 1)
    param_definition = get_param_by_alias(param_alias)
    
    if not param_definition:
        raise ValueError(f"Unknown parameter alias: {param_alias}")
    
    test_switch_xor(param_definition, _current_args)
    
    return _parse_value(param_definition, raw_value), param_definition

def _handle_command(argument):
    """Handle a command argument.
    
    Args:
        argument: The command name.
    """
    if not is_command(argument):
        raise ValueError(f"Unknown command alias: {argument}")
    queue_command(argument)

def _set_defaults():
    """Set default values for all registered parameters."""
    for param_definition in _params.values():
        if is_toggle_param(param_definition):
            set_config_value(param_definition, get_param_default(param_definition, False))
        else:
            if param_has_default(param_definition):
                set_config_value(param_definition, get_param_default(param_definition))

def _build_preparse_map(preparse_definitions):
    """Build map of param names to their pre-parse definitions.
    
    Args:
        preparse_definitions: List of pre-parse param definition dicts.
    
    Returns:
        Dict mapping param names to their definitions.
    """
    return {definition[PARAM_NAME]: definition for definition in preparse_definitions}

def _extract_alias_from_argument(argument):
    """Extract the alias portion from a command-line argument.
    
    Handles both --param and --param=value formats.
    
    Args:
        argument: Command-line argument string.
    
    Returns:
        The alias portion (before '=' if present, otherwise the full argument).
    """
    return argument.split('=')[0] if '=' in argument else argument

def _parse_long_alias_with_embedded_value(argument, preparse_map):
    """Parse a long-alias argument with embedded value (--param=value).
    
    Args:
        argument: Argument string in --param=value format.
        preparse_map: Map of param names to pre-parse definitions.
    
    Returns:
        Tuple of (param_definition, parsed_value) or (None, None) if not a pre-parse param.
    """
    alias, raw_value = argument.split('=', 1)
    param = get_param_by_alias(alias)
    if not param:
        return None, None
    
    param_name = param.get(PARAM_NAME)
    if param_name not in preparse_map:
        return None, None
    
    param_definition = preparse_map[param_name]
    parsed_value = _parse_value(param, raw_value)
    return param_definition, parsed_value

def _extract_param_value_from_next_argument(param, arguments, current_index, arguments_count):
    """Extract param value from the next command-line argument.
    
    Args:
        param: Parameter definition dict.
        arguments: Full list of command-line arguments.
        current_index: Current position in arguments list.
        arguments_count: Total count of arguments.
    
    Returns:
        Tuple of (parsed_value, index_increment) where index_increment is 1 if value was consumed, 0 otherwise.
    """
    next_index = current_index + 1
    if next_index < arguments_count:
        next_argument = arguments[next_index]
        if not is_alias(next_argument) and not is_command(next_argument):
            parsed_value = _parse_value(param, next_argument)
            return parsed_value, 1
    
    # No value provided, use default
    default_value = get_param_default(param, None)
    return default_value, 0

def _parse_short_alias_argument(argument, arguments, current_index, arguments_count, preparse_map):
    """Parse a short-alias argument (--param or -p).
    
    Args:
        argument: Argument string (alias without value).
        arguments: Full list of command-line arguments.
        current_index: Current position in arguments list.
        arguments_count: Total count of arguments.
        preparse_map: Map of param names to pre-parse definitions.
    
    Returns:
        Tuple of (param_definition, parsed_value, index_increment).
        Returns (None, None, 0) if not a pre-parse param.
    """
    param = get_param_by_alias(argument)
    if not param:
        return None, None, 0
    
    param_name = param.get(PARAM_NAME)
    if param_name not in preparse_map:
        return None, None, 0
    
    param_definition = preparse_map[param_name]
    
    if param_definition.get(PARAM_HAS_VALUE, True):
        parsed_value, index_increment = _extract_param_value_from_next_argument(
            param, arguments, current_index, arguments_count
        )
        return param_definition, parsed_value, index_increment
    else:
        # Toggle param, no value needed
        parsed_value = _parse_value(param, None)
        return param_definition, parsed_value, 0

def _apply_preparse_value_to_config(argument, param_definition, parsed_value):
    """Apply a pre-parsed parameter value to configuration.
    
    Args:
        argument: Original command-line argument.
        param_definition: Pre-parse parameter definition dict.
        parsed_value: Value to apply.
    """
    alias = _extract_alias_from_argument(argument)
    param = get_param_by_alias(alias)
    if param:
        set_config_value_from_cmdline(param, parsed_value)

def _pre_parse_params(arguments):
    """Silently parse pre-registered params before main CLI parsing.
    
    This allows certain params (e.g., logging/verbosity) to be parsed
    early so they can control behavior during main parsing.
    
    Args:
        arguments: Command-line arguments list.
    """
    global _current_args
    _current_args = arguments  # Store for conflict checking
    
    preparse_definitions = get_pre_parse_args()
    if not preparse_definitions:
        return
    
    preparse_map = _build_preparse_map(preparse_definitions)
    
    argument_index = 0
    arguments_count = len(arguments)
    while argument_index < arguments_count:
        argument = arguments[argument_index]
        
        if is_command(argument):
            argument_index += 1
            continue
        
        param_definition = None
        parsed_value = None
        index_increment = 0
        
        if is_long_alias_with_value(argument):
            param_definition, parsed_value = _parse_long_alias_with_embedded_value(
                argument, preparse_map
            )
        elif is_alias(argument):
            param_definition, parsed_value, index_increment = _parse_short_alias_argument(
                argument, arguments, argument_index, arguments_count, preparse_map
            )
        
        if param_definition and parsed_value is not None:
            _apply_preparse_value_to_config(argument, param_definition, parsed_value)
        
        argument_index += 1 + index_increment


def handle_cli_args(args):
    """Handle command-line arguments with run-level processing.
    
    Processes run-levels in registration order. Each run-level activates
    a subset of params/commands and can set config values.
    """
    # Check for help command before processing
    from .help import handle_help_with_arg, display_all_help
    if handle_help_with_arg(args):
        return
    
    # Execute pre-parse actions (e.g., load persistent config)
    _do_pre_parse_actions()
    
    # Pre-parse specific params (e.g., logging/verbosity controls)
    # before main parsing to configure behavior
    _pre_parse_params(args)
    
    # Pre-parse: assign orphan params/commands to default run-level
    # and create bidirectional relationships
    assign_orphans_to_default_run_level()
    
    # Process run-levels in registration order
    run_levels = get_all_run_levels()
    
    # If no run levels defined, create a default one for processing
    if not run_levels:
        run_levels = [{}]
    
    # Process each run-level
    for run_level in run_levels:
        run_level_name = run_level.get(RUN_LEVEL_NAME)
        
        # Register params for this run-level
        build_params_for_run_level(run_level_name)
        
        # Set defaults first
        _set_defaults()
        
        # Then apply run-level config (can override defaults)
        if run_level_name:
            apply_run_level_config(run_level_name)
        
        # Queue commands specified in run-level definition
        if RUN_LEVEL_COMMANDS in run_level:
            cmd_list = run_level[RUN_LEVEL_COMMANDS]
            if cmd_list:  # Only process if list is not empty
                for cmd_name in cmd_list:
                    if is_command(cmd_name):
                        queue_command(cmd_name)
        
        # Parse command line for this run-level's params and commands
        _parse_command_line(args)
        
        # Execute this run-level's command queue
        run_command_queue()
    
    # Execute post-parse actions (e.g., save persistent config)
    _do_post_parse_actions()
    
    # After all run-levels, display help if no app-defined commands were queued
    if not has_app_commands_queued():
        display_all_help()
        return
