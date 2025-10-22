# Constants used as keys in command definitions (tests use these constants as keys).
from .config_consts import COMMAND_NAME, COMMAND_REQUIRED_PARAMS, COMMAND_ACTION, COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE, COMMAND_NEXT_COMMANDS, COMMAND_REQUIRE_BEFORE
from . import config

class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected in command definitions."""
    pass


# Module state
_commands = {}
_command_queue = []
_required_params = []


def get_command(name):
    """Return the command dict for name or None if missing."""
    return _commands.get(name)

def is_command(arg):
    return arg in _commands.keys()


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
        raise ValueError(f"Duplicate command name: {name}")
        
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
        
    _commands[name] = cmd
        # collect required params
    for p in cmd.get(COMMAND_REQUIRED_PARAMS, []) or []:
        if p not in _required_params:
            _required_params.append(p)


def _queue_add(name, queued):
    """
    Recursively add a command and its related commands to the queue in the
    correct order. Uses queued set to avoid duplicates and infinite cycles.
    """
    if name in queued:
        return
    cmd = get_command(name)
    if not cmd:
        raise KeyError(f"Command '{name}' not found in registry.")

    # Append this command if not already queued
    if name not in queued:
        _command_queue.append(cmd)
        queued.add(name)

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
        _sort_command_queue()
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


def _sort_command_queue():
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

def _verify_required_params():
    for cmd in _command_queue:
        for param in cmd.get(COMMAND_REQUIRED_PARAMS, []):
            if param not in config.list_config_params():
                raise ValueError(f"Missing required parameter '{param}' for command '{cmd.get(COMMAND_NAME)}'")

def run_command_queue():
    """Execute all commands in the _command_queue in order."""
    _verify_required_params()
    for cmd in _command_queue:
        action = cmd.get(COMMAND_ACTION)
        if callable(action):
            action()
        else:
            raise ValueError(f"Command '{cmd.get(COMMAND_NAME)}' has no valid action to execute.")