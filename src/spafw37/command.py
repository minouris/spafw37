# Constants used as keys in command definitions (tests use these constants as keys).
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_PHASE,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_ACTION,
    COMMAND_GOES_AFTER,
    COMMAND_GOES_BEFORE,
    COMMAND_NEXT_COMMANDS,
    COMMAND_REQUIRE_BEFORE,
    COMMAND_TRIGGER_PARAM,
    COMMAND_FRAMEWORK,
)
from spafw37.constants.phase import (
    PHASE_DEFAULT,
)
from spafw37 import config as config
from spafw37 import param
from spafw37 import logging
from spafw37 import cycle

class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected in command definitions."""
    pass


class CommandParameterError(ValueError):
    """Raised when a command is missing required parameters.
    
    Attributes:
        command_name: Name of the command that is missing parameters.
    """
    def __init__(self, message, command_name=None):
        super().__init__(message)
        self.command_name = command_name


# Module state
# NOTE: Thread Safety - These module-level variables are not thread-safe.
# This framework is designed for single-threaded CLI applications. If using
# in a multi-threaded context, external synchronization is required.
_commands = {}
_finished_commands = []
_phase_order = [ PHASE_DEFAULT]
_phases = { PHASE_DEFAULT: [] }
_phases_completed = []
_command_queue = []
_current_phase = None


# Helper functions for inline object definitions
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


def _register_inline_command(command_def):
    """Register an inline command definition.
    
    If command_def is a dict (inline definition), fully registers it using add_command.
    If it's a string (name reference), does nothing.
    
    Args:
        command_def: Command definition dict or string name
        
    Returns:
        Command name as string
    """
    if isinstance(command_def, dict):
        cmd_name = command_def.get(COMMAND_NAME)
        if cmd_name and cmd_name not in _commands:
            # Fully register the command (this will recursively process any nested inline defs)
            add_command(command_def)
        return cmd_name
    return command_def


# Delegate logging functions that automatically pass the current phase as scope
def log_trace(_message=''):
    """Log a TRACE level message with current phase as scope."""
    logging.log_trace(_scope=_current_phase, _message=_message)


def log_debug(_message=''):
    """Log a DEBUG level message with current phase as scope."""
    logging.log_debug(_scope=_current_phase, _message=_message)


def log_info(_message=''):
    """Log an INFO level message with current phase as scope."""
    logging.log_info(_scope=_current_phase, _message=_message)


def log_warning(_message=''):
    """Log a WARNING level message with current phase as scope."""
    logging.log_warning(_scope=_current_phase, _message=_message)


def log_error(_message=''):
    """Log an ERROR level message with current phase as scope."""
    logging.log_error(_scope=_current_phase, _message=_message)


def set_phases_order(phase_order):
    global _phase_order
    _phase_order = phase_order
    _current_phase = phase_order[0] if phase_order else config.get_default_phase()
    for _phase in _phase_order:
        if _phase not in _phases:
            _phases[_phase] = []

def _is_command_finished(command_name):
    return command_name in _finished_commands


def get_command(name):
    """Return the command dict for name or None if missing."""
    return _commands.get(name)


def get_all_commands():
    """Return all registered commands.
    
    Returns:
        Dictionary of all registered commands {command_name: command_dict}.
    """
    return dict(_commands)


def is_command(arg):
    if arg not in _commands.keys():
        return False
    cmd = _commands[arg]
    return cycle.is_command_invocable(cmd)


def has_app_commands_queued():
    """Check if any app-defined (non-framework) commands are queued or executed.
    
    Returns:
        True if any app-defined commands are in the queue, phases, or finished.
    """
    # Check finished commands for app commands
    for cmd_name in _finished_commands:
        cmd = get_command(cmd_name)
        if cmd and not cmd.get(COMMAND_FRAMEWORK, False):
            return True
    
    # Check all phases for app commands
    for phase_name in _phase_order:
        if phase_name not in _phases_completed:
            for cmd in _phases.get(phase_name, []):
                if not cmd.get(COMMAND_FRAMEWORK, False):
                    return True
    return False


def get_first_queued_command_name():
    """Get the name of the first queued command across all phases.
    
    Returns:
        Command name string, or None if no commands are queued.
    """
    for phase_name in _phase_order:
        if phase_name not in _phases_completed:
            phase_cmds = _phases.get(phase_name, [])
            if phase_cmds:
                return phase_cmds[0].get(COMMAND_NAME)
    return None


def add_commands(command_list):
    """
    Register a list of command dictionaries into the module registry.

    This also collects required params into the module-level _required_params
    list (avoiding duplicates).
    """
    for cmd in command_list:
        add_command(cmd)

def add_command(cmd):
    name = cmd.get(COMMAND_NAME)
    if not name:
        raise ValueError("Command name cannot be empty")
    if not cmd.get(COMMAND_ACTION):
        raise ValueError("Command action is required")
    if name in _commands:
        return
    
    # Process inline parameter definitions in COMMAND_REQUIRED_PARAMS
    required_params = cmd.get(COMMAND_REQUIRED_PARAMS, [])
    if required_params:
        normalized_params = []
        for param_def in required_params:
            param_name = param._register_inline_param(param_def)
            normalized_params.append(param_name)
        cmd[COMMAND_REQUIRED_PARAMS] = normalized_params
    
    # Process inline parameter definition in COMMAND_TRIGGER_PARAM
    trigger_param = cmd.get(COMMAND_TRIGGER_PARAM)
    if trigger_param:
        param_name = param._register_inline_param(trigger_param)
        cmd[COMMAND_TRIGGER_PARAM] = param_name
    
    # Process inline command definitions in dependency/sequencing fields
    for field in [COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE, COMMAND_NEXT_COMMANDS, COMMAND_REQUIRE_BEFORE]:
        cmd_list = cmd.get(field, [])
        if cmd_list:
            normalized_cmds = []
            for cmd_def in cmd_list:
                cmd_name = _register_inline_command(cmd_def)
                normalized_cmds.append(cmd_name)
            cmd[field] = normalized_cmds
        
    # Check for self-references
    for ref_list in [COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE, COMMAND_NEXT_COMMANDS, COMMAND_REQUIRE_BEFORE]:
        refs = cmd.get(ref_list, []) or []
        if name in refs:
            raise ValueError(f"Command '{name}' cannot reference itself")
        
    # Check for conflicting constraints
    goes_before = set(cmd.get(COMMAND_GOES_BEFORE, []) or [])
    goes_after = set(cmd.get(COMMAND_GOES_AFTER, []) or [])
    if goes_before & goes_after:
        conflicting = goes_before & goes_after
        raise ValueError(f"Command '{name}' has conflicting constraints with: {list(conflicting)}")
    if not cmd.get(COMMAND_PHASE):
        cmd[COMMAND_PHASE] = config.get_default_phase()
    _commands[name] = cmd
    
    # Register cycle if present
    cycle.register_cycle(cmd, _commands)


def _execute_command(cmd):
    """Execute a single command's action function.
    
    Args:
        cmd: Command definition dict
    """
    cmd_name = cmd.get(COMMAND_NAME)
    action = cmd.get(COMMAND_ACTION)
    if not callable(action):
        raise ValueError("Command '{}' has no valid action to execute.".format(cmd_name))
    action()


def _queue_add(name, queued):
    """
    Recursively add a command and its related commands to the queue in the
    correct order. Uses queued set to avoid duplicates and infinite cycles.
    """
    if name in queued:
        return
    if _is_command_finished(name):
        return
    cmd = get_command(name)
    if not cmd:
        raise KeyError(f"Command '{name}' not found in registry.")

    # Append this command if not already queued
    if name not in queued:
        _command_queue.append(cmd)
        queued.add(name)
    if cmd.get(COMMAND_PHASE):
        _phase = cmd.get(COMMAND_PHASE)
        if _phase not in _phases:
            raise KeyError(f"Phase '{_phase}' not recognised.")
        if _phase in _phases_completed:
            raise ValueError(f"Cannot add command '{name}' to completed phase '{_phase}'.") 
        if cmd not in _phases[_phase]:
            _phases[_phase].append(cmd)

    # Ensure commands that this command must come after are queued
    for dep in cmd.get(COMMAND_GOES_AFTER, []) or []:
        if dep not in _commands:
            raise KeyError(f"Command '{dep}' not found in registry.")
        _queue_add(dep, queued)

    # REQUIRE_BEFORE for this command means these prerequisites must be present
    # before this command — queue those first.
    for prereq in cmd.get(COMMAND_REQUIRE_BEFORE, []) or []:
        if prereq not in _commands:
            raise KeyError(f"Command '{prereq}' not found in registry.")
        _queue_add(prereq, queued)

    # If this command must come before certain commands, ensure they are queued
    # after this command.
    for after_target in cmd.get(COMMAND_GOES_BEFORE, []) or []:
        if after_target not in _commands:
            raise KeyError(f"Command '{after_target}' not found in registry.")
        _queue_add(after_target, queued)

    # NEXT_COMMANDS should be queued after the current command.
    for next_name in cmd.get(COMMAND_NEXT_COMMANDS, []) or []:
        if next_name not in _commands:
            raise KeyError(f"Command '{next_name}' not found in registry.")
        _queue_add(next_name, queued)


def queue_command(name):
    """Public helper to queue a single command by name."""    
    _queue_add(name, set())


def queue_commands(names):
    """
    Queue multiple commands in the order provided (while respecting
    dependency relations which may reorder or add other commands).
    """
    queued = set()
    for n in names:
        _queue_add(n, queued)
    
    # Check for circular dependencies after queuing
    try:
        _sort_command_queue(_command_queue)
    except CircularDependencyError as e:
        # Convert to ValueError to match test expectations
        raise ValueError(f"Detected circular dependency: {e}")


def _detect_cycle(graph):
    """
    Detect cycles in a directed graph using DFS.
    Returns the first cycle found as a list of nodes, or None if no cycle.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    colors = {node: WHITE for node in graph}
    parent = {}
    
    def dfs(node, path):
        if colors[node] == GRAY:
            # Found a back edge, extract the cycle
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        if colors[node] == BLACK:
            return None
            
        colors[node] = GRAY
        path.append(node)
        
        for neighbor in graph[node]:
            cycle = dfs(neighbor, path)
            if cycle:
                return cycle
                
        path.pop()
        colors[node] = BLACK
        return None
    
    for node in graph:
        if colors[node] == WHITE:
            cycle = dfs(node, [])
            if cycle:
                return cycle
    return None


def _build_dependency_graph(names):
    """
    Build a directed graph (adjacency list) for the provided command names.
    Edge A -> B means A must come before B.
    Raises CircularDependencyError if cycles are detected.
    
    TODO: Improve error message to show the actual cycle path rather than
    just listing remaining nodes when circular dependencies are detected.
    """
    
    graph = {n: set() for n in names}
    for n in names:
        cmd = get_command(n)
        if not cmd:
            continue
        # GOES_AFTER: dep must come before this command -> dep -> n
        for dep in cmd.get(COMMAND_GOES_AFTER, []) or []:
            if dep in graph:
                graph[dep].add(n)
        # REQUIRE_BEFORE: prereq must come before this command -> prereq -> n
        for prereq in cmd.get(COMMAND_REQUIRE_BEFORE, []) or []:
            if prereq in graph:
                graph[prereq].add(n)
        # GOES_BEFORE: this command must come before target -> n -> target
        for target in cmd.get(COMMAND_GOES_BEFORE, []) or []:
            if target in graph:
                graph[n].add(target)
        # NEXT_COMMANDS: this command must come before next -> n -> next
        for nxt in cmd.get(COMMAND_NEXT_COMMANDS, []) or []:
            if nxt in graph:
                graph[n].add(nxt)

    # Check for circular dependencies
    cycle = _detect_cycle(graph)
    if cycle:
        cycle_str = " -> ".join(cycle)
        raise CircularDependencyError(f"Circular dependency detected: {cycle_str}")
    
    return graph


def _sort_command_queue(_command_queue=_command_queue):
    """
    Reorder _command_queue according to dependency relations using a stable
    topological sort (Kahn's algorithm). Only sorts commands that are already
    present in _command_queue.
    Raises CircularDependencyError if cycles are detected.
    """
    if not _command_queue:
        return
    # Work with names for sorting
    names = [c.get(COMMAND_NAME) for c in _command_queue if c.get(COMMAND_NAME)]
    graph = _build_dependency_graph(names)

    # compute in-degrees
    indeg = {n: 0 for n in names}
    for src, targets in graph.items():
        for t in targets:
            indeg[t] += 1

    # Kahn's algorithm, keep stable order by selecting nodes in the order they
    # originally appeared in the queue when indeg == 0.
    result = []
    zero_nodes = [n for n in names if indeg[n] == 0]

    # Preserve original ordering for zero_nodes by sorting according to original index
    name_index = {n: i for i, n in enumerate(names)}
    zero_nodes.sort(key=lambda x: name_index.get(x, 0))

    while zero_nodes:
        n = zero_nodes.pop(0)
        result.append(n)
        for m in sorted(graph.get(n, []), key=lambda x: name_index.get(x, 0)):
            indeg[m] -= 1
            if indeg[m] == 0:
                inserted = False
                for i, z in enumerate(zero_nodes):
                    if name_index.get(m, 0) < name_index.get(z, 0):
                        zero_nodes.insert(i, m)
                        inserted = True
                        break
                if not inserted:
                    zero_nodes.append(m)

    # If there is a cycle, the result will be incomplete
    if len(result) != len(names):
        remaining_names = [n for n in names if n not in result]
        raise CircularDependencyError(f"Circular dependency prevents proper ordering. Remaining commands: {remaining_names}")

    # Rebuild _command_queue with dicts in final_order
    name_to_cmd = {c.get(COMMAND_NAME): c for c in _command_queue if c.get(COMMAND_NAME)}
    new_queue = []
    final_order = result
    for n in final_order:
        cmd = name_to_cmd.get(n)
        if cmd is not None:
            new_queue.append(cmd)

    # replace module queue in-place
    del _command_queue[:]
    _command_queue.extend(new_queue)

def _verify_required_params(_exclude_runtime_only: bool = True) -> None:
    """
    Verify that all required parameters are set before execution.
    
    Args:
        _exclude_runtime_only: If True, skip verification of runtime-only params.
    
    Raises:
        ValueError: If required parameters are missing.
    """
    # Check all phase queues instead of _command_queue
    for phase_name in _phase_order:
        if phase_name not in _phases_completed:
            for cmd in _phases.get(phase_name, []):
                _verify_command_params(cmd, _skip_runtime_only=_exclude_runtime_only)

def _verify_command_params(cmd, _skip_runtime_only=True):
    for _param in cmd.get(COMMAND_REQUIRED_PARAMS, []):
        if (_skip_runtime_only and param.is_runtime_only_param(param.get_param_by_name(_param))):
            continue
        if _param not in config.list_config_params():
            cmd_name = cmd.get(COMMAND_NAME)
            raise CommandParameterError(
                f"Missing required parameter '{_param}' for command '{cmd_name}'",
                command_name=cmd_name
            )

def _record_finished_command(command_name):
    # Run commands should have their names stored so they don't get re-queued
    if command_name not in _finished_commands:
        _finished_commands.append(command_name)

def _trim_queue():
    # Remove finished commands from the queue
    _command_queue[:] = [cmd for cmd in _command_queue if cmd.get(COMMAND_NAME) not in _finished_commands]

def _recalculate_queue(_command_queue=_command_queue):
    # Add any commands triggered by params set before execution
    _add_triggered_commands() 
    # Re-sort the queue after additions
    _sort_command_queue(_command_queue)

def _add_triggered_commands():
    """Add commands to the queue that are triggered by currently set params."""
    for param_name in config.list_config_params():
        param_def = param.get_param_by_name(param_name)
        if not param_def:
            continue
        for cmd in _commands.values():
            trigger_param = cmd.get(COMMAND_TRIGGER_PARAM)
            if trigger_param == param_name:
                if cmd not in _command_queue:
                    _queue_add(cmd.get(COMMAND_NAME), set())

def run_command_queue():
    """Execute commands phase by phase according to _phase_order."""
    global _current_phase
    _recalculate_queue(_phases.get(_phase_order[0]))
    for _current_phase in _phase_order:
        logging.set_current_scope(_current_phase)
        while _phases.get(_current_phase):
            try:
                _recalculate_queue(_phases[_current_phase]) # Recalculate queue order after any additions
            except (CircularDependencyError, ValueError) as e:
                log_error(_message=f"Error in phase {_current_phase}: {e}")
                _phases_completed.append(_current_phase)
                break # Break and go on to next phase
            _verify_command_params(_phases[_current_phase][0], _skip_runtime_only=False)
            cmd = _phases[_current_phase].pop(0)
            cmd_name = cmd.get(COMMAND_NAME)
            log_info(_message=f"Starting command: {cmd_name}")
            action = cmd.get(COMMAND_ACTION)
            if not callable(action):
                raise ValueError(f"Command '{cmd_name}' has no valid action to execute.")
            action()
            log_info(_message=f"Completed command: {cmd_name}")
            _record_finished_command(cmd_name) # Note that this command has finished
            
            # Execute cycle if present - provide simplified wrappers
            def _cycle_queue_add(cmd_def, temp_queue, commands_dict):
                """Build a temp queue for cycle execution."""
                temp_queue.append(cmd_def[COMMAND_NAME])
            
            def _cycle_sort_queue(temp_queue, commands_dict):
                """Sort temp queue based on dependencies."""
                # Convert names back to command defs for sorting
                cmd_list = [commands_dict[name] for name in temp_queue if name in commands_dict]
                _sort_command_queue(cmd_list)
                # cmd_list is sorted in-place, return as names
                return [c.get(COMMAND_NAME) for c in cmd_list]
            
            cycle.execute_cycle(
                cmd, _commands, _execute_command, _cycle_queue_add, _cycle_sort_queue
            )
        _phases_completed.append(_current_phase)
        logging.set_current_scope(None)
    _current_phase = None
