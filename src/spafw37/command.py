from .config_consts import COMMAND_ACTION, COMMAND_NAME, COMMAND_NEXT_COMMANDS, COMMAND_REQUIRE_BEFORE, COMMAND_REQUIRED_PARAMS, COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE
from .config import list_config_params

# Commands to run from the command line, added by configuration
_commands = {}

# Commands queued by passing their name on the CLI, or by REQUIRE_BEFORE/NEXT_COMMANDS
_command_queue = []

# Required params across all queued commands
_required_params = []

def _run_command(command):
    # 1. Verify required params are present in _config
    required_params = command.get(COMMAND_REQUIRED_PARAMS, [])
    for req_param in required_params:
        if req_param not in list_config_params():
            raise ValueError(f"Required parameter '{req_param}' not provided for command '{command.get(COMMAND_NAME)}'")
    # 2. Run command action
    action = command.get(COMMAND_ACTION)
    if action:
        try:
            action()
        except Exception as e:
            # TODO: Log error
            raise e

def run_command_queue():
    # Verify all required params are present
    for req_param in _required_params:
        if req_param not in list_config_params():
            raise ValueError(f"Required parameter '{req_param}' not provided for queued commands")
    # Run each command in the queue
    for command in _command_queue:
        try:
            _run_command(command)
        except Exception as e:
            # TODO: Log error
            raise e

def is_command(arg):
    return arg in _commands.keys()

def get_command(command_name):
    return _commands.get(command_name, {})

def add_commands(commands):
    for command in commands:
        add_command(command)

def add_command(_command):
    _command_name = _command.get(COMMAND_NAME)
    # Ensure that anything in REQUIRED_BEFORE is added to SEQUENCE_BEFORE
    _handle_add_command_require_before(_command)
    # Ensure that anything in NEXT_COMMANDS is added to SEQUENCE_AFTER
    _handle_add_command_next_commands(_command) 
    _commands[_command_name] = _command

def _handle_add_command_next_commands(_command):
    next_commands = _command.get(COMMAND_NEXT_COMMANDS, [])
    if next_commands:
        if _command.get(COMMAND_GOES_AFTER) is None:
            _command[COMMAND_GOES_AFTER] = []
        for next_command in next_commands:
            if next_command not in _command[COMMAND_GOES_AFTER]:
                _command[COMMAND_GOES_AFTER].append(next_command)

def _handle_add_command_require_before(_command):
    require_before = _command.get(COMMAND_REQUIRE_BEFORE, [])
    if require_before:
        if _command.get(COMMAND_GOES_BEFORE) is None:
            _command[COMMAND_GOES_BEFORE] = []
        for req_command in require_before:
            if req_command not in _command[COMMAND_GOES_BEFORE]:
                _command[COMMAND_GOES_BEFORE].append(req_command)

def queue_commands(_command_names):
    for command_name in _command_names:
        queue_command(command_name)
    _sort_command_queue()

def queue_command(command_name):
    _command = get_command(command_name)
    if not _command:
        raise ValueError(f"Command '{command_name}' not found")
    _queue_command(_command)

def _queue_command(_command):
    # Make sure anything in REQUIRED_PARAMS is tracked
    _handle_required_params(_command)
    # Make sure any REQUIRE_BEFORE commands are queued first
    _handle_require_before(_command)
    # Queue this command
    if _command not in _command_queue:
        _command_queue.append(_command)
    # Make sure any NEXT_COMMANDS are queued last
    _handle_queue_next_commands(_command)

def _handle_queue_next_commands(_command):
    next_commands = _command.get(COMMAND_NEXT_COMMANDS, [])
    for next_command_name in next_commands:
        next_command = get_command(next_command_name)
        if next_command and next_command not in _command_queue:
            _queue_command(next_command)

def _handle_require_before(_command):
    req_before_commands = _command.get(COMMAND_REQUIRE_BEFORE, [])
    for req_command_name in req_before_commands:
        req_command = get_command(req_command_name)
        if req_command and req_command not in _command_queue:
            _queue_command(req_command)

def _handle_required_params(_command):
    req_params = _command.get(COMMAND_REQUIRED_PARAMS, [])
    for _param in req_params:
        if _param not in _required_params:
            _required_params.append(_param)

def _sort_command_queue():
    global _command_queue
    _resolve_queue_relationships()
    # Simple topological sort based on GOES_BEFORE and GOES_AFTER
    sorted_queue = []
    temp_queue = _command_queue.copy()
    while temp_queue:
        for command in temp_queue:
            goes_before = command.get(COMMAND_GOES_BEFORE, [])
            if all(get_command(name) in sorted_queue for name in goes_before):
                sorted_queue.append(command)
                temp_queue.remove(command)
                break
    _reversed = sorted_queue[::-1]
    _command_queue = _reversed

def _resolve_queue_relationships():
    for _command in _command_queue:
        _add_reciprocal_relationship(_command, COMMAND_GOES_BEFORE, COMMAND_GOES_AFTER)
        _add_reciprocal_relationship(_command, COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE)

def _add_reciprocal_relationship(_command, _target_name_field, _target_ref_field):
    _target_list = _command.get(_target_name_field, [])
    for _target_name in _target_list:
        _target_command = get_command(_target_name)
        if _target_command:
            if _target_command.get(_target_ref_field) is None:
                _target_command[_target_ref_field] = []
            if _command.get(COMMAND_NAME) not in _target_command[_target_ref_field]:
                _target_command[_target_ref_field].append(_command.get(COMMAND_NAME))
