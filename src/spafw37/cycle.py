"""
Cycle execution system for running repeated sequences of commands.

This module provides functionality for defining and executing command cycles:
- Cycles can have initialization, loop condition, and finalization functions
- Cycle commands are validated upfront (params merged into parent command)
- Nested cycles are supported via recursive param collection
- All commands within a cycle must be in the same phase
- Cycle commands are not directly invocable from CLI
"""

from spafw37.constants.command import (
    COMMAND_CYCLE,
    COMMAND_INVOCABLE,
    COMMAND_NAME,
    COMMAND_PHASE,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_ACTION,
    COMMAND_GOES_AFTER,
    COMMAND_GOES_BEFORE,
    COMMAND_NEXT_COMMANDS,
    COMMAND_REQUIRE_BEFORE,
)
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.phase import PHASE_DEFAULT
from spafw37 import logging


class CycleValidationError(ValueError):
    """Raised when cycle definition is invalid."""
    pass


class CycleExecutionError(RuntimeError):
    """Raised when cycle execution encounters an error."""
    pass


# Module state
_active_cycle = None
_max_nesting_depth = 5


def _get_command_name(command_def):
    """Extract command name from command definition.
    
    Args:
        command_def: Command definition dict or string name
        
    Returns:
        Command name as string
    """
    if isinstance(command_def, str):
        return command_def
    return command_def.get(COMMAND_NAME, '')


def _get_cycle_from_command(command_def):
    """Extract cycle definition from command.
    
    Args:
        command_def: Command definition dict
        
    Returns:
        Cycle definition dict or None
    """
    return command_def.get(COMMAND_CYCLE, None)


def _is_cycle_command(command_def):
    """Check if command definition includes a cycle.
    
    Args:
        command_def: Command definition dict
        
    Returns:
        True if command has cycle definition
    """
    return _get_cycle_from_command(command_def) is not None


def _collect_cycle_params_recursive(cycle_def, commands_dict, depth=0):
    """Recursively collect all required params from cycle commands.
    
    Traverses cycle commands and any nested cycles to gather all
    required parameters. Includes depth limit to prevent infinite recursion.
    
    Args:
        cycle_def: Cycle definition dict
        commands_dict: Dict mapping command names to command definitions
        depth: Current nesting depth (for recursion limit)
        
    Returns:
        Set of all required parameter names
        
    Raises:
        CycleValidationError: If nesting depth exceeds maximum
    """
    if depth > _max_nesting_depth:
        cycle_name = cycle_def.get(CYCLE_NAME, 'unknown')
        raise CycleValidationError(
            'Cycle nesting depth exceeds maximum of {}: {}'.format(
                _max_nesting_depth, cycle_name
            )
        )
    
    all_params = set()
    cycle_commands = cycle_def.get(CYCLE_COMMANDS, [])
    
    for cmd_def in cycle_commands:
        cmd_name = _get_command_name(cmd_def)
        
        # Get command definition from dict if reference by name
        if isinstance(cmd_def, str):
            if cmd_name not in commands_dict:
                raise CycleValidationError(
                    'Cycle command not found: {}'.format(cmd_name)
                )
            cmd_def = commands_dict[cmd_name]
        
        # Collect params from this command
        cmd_params = cmd_def.get(COMMAND_REQUIRED_PARAMS, [])
        all_params.update(cmd_params)
        
        # If this command has a nested cycle, recurse
        if _is_cycle_command(cmd_def):
            nested_cycle = _get_cycle_from_command(cmd_def)
            nested_params = _collect_cycle_params_recursive(
                nested_cycle, commands_dict, depth + 1
            )
            all_params.update(nested_params)
    
    return all_params


def _validate_cycle_phase_consistency(cycle_def, commands_dict, parent_phase):
    """Validate all cycle commands are in same phase as parent.
    
    Args:
        cycle_def: Cycle definition dict
        commands_dict: Dict mapping command names to command definitions
        parent_phase: Phase of parent command
        
    Raises:
        CycleValidationError: If any command has different phase
    """
    cycle_commands = cycle_def.get(CYCLE_COMMANDS, [])
    cycle_name = cycle_def.get(CYCLE_NAME, 'unknown')
    
    for cmd_def in cycle_commands:
        cmd_name = _get_command_name(cmd_def)
        
        # Get full command definition
        if isinstance(cmd_def, str):
            if cmd_name not in commands_dict:
                # Skip validation for inline commands or missing refs
                continue
            cmd_def = commands_dict[cmd_name]
        
        # Check phase consistency
        cmd_phase = cmd_def.get(COMMAND_PHASE, PHASE_DEFAULT)
        if cmd_phase != parent_phase:
            raise CycleValidationError(
                'Cycle command {} has phase {} but parent has phase {}'.format(
                    cmd_name, cmd_phase, parent_phase
                )
            )


def _mark_cycle_commands_not_invocable(cycle_def, commands_dict):
    """Mark all cycle commands as not invocable from CLI.
    
    Also registers nested cycles for inline command definitions.
    
    Args:
        cycle_def: Cycle definition dict
        commands_dict: Dict mapping command names to command definitions
    """
    cycle_commands = cycle_def.get(CYCLE_COMMANDS, [])
    
    for cmd_def in cycle_commands:
        cmd_name = _get_command_name(cmd_def)
        
        # Register inline command definition
        if not isinstance(cmd_def, str):
            commands_dict[cmd_name] = cmd_def
        
        # Get command definition
        if isinstance(cmd_def, str):
            if cmd_name not in commands_dict:
                continue
            cmd_def = commands_dict[cmd_name]
        
        # Mark as not invocable
        cmd_def[COMMAND_INVOCABLE] = False
        
        # Recursively mark nested cycle commands
        if _is_cycle_command(cmd_def):
            nested_cycle = _get_cycle_from_command(cmd_def)
            _mark_cycle_commands_not_invocable(nested_cycle, commands_dict)


def register_cycle(command_def, commands_dict):
    """Register a cycle and merge its params into parent command.
    
    Validates cycle definition, collects all required params from cycle
    commands (including nested cycles), merges them into parent command,
    and marks cycle commands as not invocable.
    
    Args:
        command_def: Parent command definition dict
        commands_dict: Dict mapping command names to command definitions
        
    Raises:
        CycleValidationError: If cycle definition is invalid
    """
    cycle_def = _get_cycle_from_command(command_def)
    if not cycle_def:
        return
    
    cycle_name = cycle_def.get(CYCLE_NAME, 'unknown')
    parent_name = command_def.get(COMMAND_NAME, 'unknown')
    parent_phase = command_def.get(COMMAND_PHASE, PHASE_DEFAULT)
    
    # Validate required fields
    if not cycle_def.get(CYCLE_LOOP):
        raise CycleValidationError(
            'Cycle {} missing required field: {}'.format(
                cycle_name, CYCLE_LOOP
            )
        )
    
    cycle_commands = cycle_def.get(CYCLE_COMMANDS, [])
    if not cycle_commands:
        raise CycleValidationError(
            'Cycle {} has no commands'.format(cycle_name)
        )
    
    # Validate phase consistency
    _validate_cycle_phase_consistency(cycle_def, commands_dict, parent_phase)
    
    # Collect all params from cycle commands (including nested)
    cycle_params = _collect_cycle_params_recursive(cycle_def, commands_dict)
    
    # Merge params into parent command
    parent_params = set(command_def.get(COMMAND_REQUIRED_PARAMS, []))
    parent_params.update(cycle_params)
    command_def[COMMAND_REQUIRED_PARAMS] = list(parent_params)
    
    # Mark cycle commands as not invocable
    _mark_cycle_commands_not_invocable(cycle_def, commands_dict)
    
    logging.log_debug(
        _scope='cycle',
        _message='Registered cycle {} for command {}'.format(
            cycle_name, parent_name
        )
    )


def _build_cycle_queue(cycle_def, commands_dict, queue_add_func, sort_queue_func):
    """Build execution queue for cycle commands.
    
    Uses existing command queueing infrastructure to handle dependencies
    and topological sorting within the cycle.
    
    Args:
        cycle_def: Cycle definition dict
        commands_dict: Dict mapping command names to command definitions
        queue_add_func: Function to add commands to queue with dependencies
        sort_queue_func: Function to sort queue topologically
        
    Returns:
        Sorted list of command names to execute
    """
    temp_queue = []
    cycle_commands = cycle_def.get(CYCLE_COMMANDS, [])
    
    for cmd_def in cycle_commands:
        cmd_name = _get_command_name(cmd_def)
        
        # Get full command definition
        if isinstance(cmd_def, str):
            if cmd_name in commands_dict:
                cmd_def = commands_dict[cmd_name]
        
        # Queue command with its dependencies
        queue_add_func(cmd_def, temp_queue, commands_dict)
    
    # Sort queue to respect dependencies
    sorted_queue = sort_queue_func(temp_queue, commands_dict)
    
    return sorted_queue


def _execute_cycle_iteration(command_names, commands_dict, run_command_func,
                            queue_add_func, sort_queue_func):
    """Execute one iteration of cycle commands.
    
    Args:
        command_names: List of command names to execute in order
        commands_dict: Dict mapping command names to command definitions
        run_command_func: Function to execute a single command
        queue_add_func: Function to add commands to queue with dependencies
        sort_queue_func: Function to sort queue topologically
        
    Raises:
        CycleExecutionError: If command execution fails
    """
    for cmd_name in command_names:
        if cmd_name not in commands_dict:
            raise CycleExecutionError(
                'Command not found during cycle execution: {}'.format(cmd_name)
            )
        
        cmd_def = commands_dict[cmd_name]
        
        # Check if this is a nested cycle
        if _is_cycle_command(cmd_def):
            # Execute nested cycle recursively
            execute_cycle(
                cmd_def,
                commands_dict,
                run_command_func,
                queue_add_func,
                sort_queue_func
            )
        else:
            # Execute regular command
            run_command_func(cmd_def)


def execute_cycle(command_def, commands_dict, run_command_func, 
                  queue_add_func, sort_queue_func):
    """Execute a command cycle with init, loop, and finalization.
    
    Runs the cycle initialization function, then repeatedly executes
    cycle commands while loop condition returns True, then runs
    finalization function.
    
    Args:
        command_def: Parent command definition dict
        commands_dict: Dict mapping command names to command definitions
        run_command_func: Function to execute a single command
        queue_add_func: Function to add commands to queue with dependencies
        sort_queue_func: Function to sort queue topologically
        
    Raises:
        CycleExecutionError: If cycle execution fails
    """
    global _active_cycle
    
    cycle_def = _get_cycle_from_command(command_def)
    if not cycle_def:
        return
    
    cycle_name = cycle_def.get(CYCLE_NAME, 'unknown')
    parent_name = command_def.get(COMMAND_NAME, 'unknown')
    
    # Track active cycle for nested cycle detection
    previous_cycle = _active_cycle
    _active_cycle = cycle_name
    
    try:
        logging.log_info(
            _scope='cycle',
            _message='Starting cycle {} for command {}'.format(
                cycle_name, parent_name
            )
        )
        
        # Run initialization function if present
        init_func = cycle_def.get(CYCLE_INIT)
        if init_func and callable(init_func):
            logging.log_debug(
                _scope='cycle',
                _message='Running init function for cycle {}'.format(cycle_name)
            )
            init_func()
        
        # Build command execution queue
        command_queue = _build_cycle_queue(
            cycle_def, commands_dict, queue_add_func, sort_queue_func
        )
        
        # Execute loop
        loop_func = cycle_def.get(CYCLE_LOOP)
        loop_start_func = cycle_def.get(CYCLE_LOOP_START)
        iteration_count = 0
        
        while callable(loop_func) and loop_func():
            iteration_count += 1
            logging.log_debug(
                _scope='cycle',
                _message='Cycle {} iteration {}'.format(
                    cycle_name, iteration_count
                )
            )
            
            # Run loop start function if present
            if loop_start_func and callable(loop_start_func):
                logging.log_debug(
                    _scope='cycle',
                    _message='Running loop start function for cycle {}'.format(cycle_name)
                )
                loop_start_func()
            
            _execute_cycle_iteration(
                command_queue, commands_dict, run_command_func,
                queue_add_func, sort_queue_func
            )
        
        # Run finalization function if present
        end_func = cycle_def.get(CYCLE_END)
        if end_func and callable(end_func):
            logging.log_debug(
                _scope='cycle',
                _message='Running end function for cycle {}'.format(cycle_name)
            )
            end_func()
        
        logging.log_info(
            _scope='cycle',
            _message='Completed cycle {} after {} iterations'.format(
                cycle_name, iteration_count
            )
        )
    
    finally:
        # Restore previous active cycle
        _active_cycle = previous_cycle


def get_cycle_commands(command_def):
    """Get list of commands in a cycle.
    
    Args:
        command_def: Command definition dict or command name string
        
    Returns:
        List of command names in cycle, or empty list if no cycle
    """
    # If given a string, look up the command (requires commands_dict from caller)
    # For now, just check if it's a dict with a cycle
    if not isinstance(command_def, dict):
        return []
    
    cycle_def = _get_cycle_from_command(command_def)
    if not cycle_def:
        return []
    
    cycle_commands = cycle_def.get(CYCLE_COMMANDS, [])
    return [_get_command_name(cmd) for cmd in cycle_commands]


def is_command_invocable(command_def):
    """Check if command can be invoked from CLI.
    
    Args:
        command_def: Command definition dict
        
    Returns:
        True if command is invocable (default), False otherwise
    """
    return command_def.get(COMMAND_INVOCABLE, True)


def get_active_cycle():
    """Get the name of the currently executing cycle.
    
    Returns:
        Name of active cycle or None
    """
    return _active_cycle


def reset_cycle_state():
    """Reset module state for testing."""
    global _active_cycle
    _active_cycle = None

