from __future__ import annotations
import sys

from typing import Callable

from .command import run_command_queue, get_command, is_command, queue_command, has_app_commands_queued, CommandParameterError
from .config import list_config_params, set_config_value
from .param import (
    _has_xor_with, _params, get_bind_name, get_param_default, is_alias, 
    is_list_param, is_long_alias_with_value, get_param_by_alias, _parse_value, 
    is_param_alias, is_toggle_param, param_has_default, build_params_for_run_level,
    get_all_run_levels, apply_run_level_config
)
from .config_consts import RUN_LEVEL_NAME, RUN_LEVEL_COMMANDS, RUN_LEVEL_PARAMS

# Functions to run before parsing the command line
_pre_parse_actions: list[Callable] = []

# Functions to run after parsing the command line
_post_parse_actions: list[Callable] = []

def add_pre_parse_action(action: Callable):
    _pre_parse_actions.append(action)

def add_pre_parse_actions(actions: list[Callable]):
    for action in actions:
        _pre_parse_actions.append(action)

def add_post_parse_action(action: Callable):
    _post_parse_actions.append(action)

def add_post_parse_actions(actions: list[Callable]):
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

def capture_param_values(args: list[str], _param):
    if is_toggle_param(_param):
        return 1, True
    _values = []
    _idx = 0
    _offset = 1
    _size = len(args)
    while _idx < _size:
        arg = args[_idx]
        if is_command(arg) or is_long_alias_with_value(arg):
            break # Done processing values
        if is_alias(arg):
            if not is_param_alias(_param, arg):
                break # Done processing values for this param
            # We are capturing for the correct param, values start on next arg
            _idx += 1
            continue            
        if not is_list_param(_param):
            return _offset + _idx, arg
        _values.extend([arg])
        _idx += 1
    return _offset + _idx, _values

def test_switch_xor(_param):
    for bind_name in list_config_params():
        if _has_xor_with(get_bind_name(_param), bind_name):
            # Remove conflicting param from config
            raise ValueError(f"Conflicting parameters provided: {_param.get('name')} and {bind_name}")

def _parse_command_line(args: list[str]):
    _idx = 0
    _size = len(args)
    _param = None
    _value = None
    while _idx < _size:
        arg = args[_idx]
        if is_command(arg):
            _handle_command(arg)
        else:
            if is_long_alias_with_value(arg):
                _value, _param = _handle_long_alias_param(arg)
            elif is_alias(arg):
                _idx, _param, _value = _handle_alias_param(args, _idx, arg)
            else:
                raise ValueError(f"Unknown argument or command: {arg}")
            if _param and _value is not None:
                set_config_value(_param, _value)
        _idx += 1

def _handle_alias_param(args, _idx, arg):
    _param = get_param_by_alias(arg)
    if not _param:
        raise ValueError(f"Unknown parameter alias: {arg}")
    test_switch_xor(_param)
    if is_toggle_param(_param):
        _value = _parse_value(_param, None)
    else:
        _offset, _value = capture_param_values(args[_idx:], _param)
        _idx += _offset
    return _idx, _param, _value

def _handle_long_alias_param(arg):
    param_alias, value = arg.split('=', 1)
    _param = get_param_by_alias(param_alias)
    test_switch_xor(_param)
    if not _param:
        raise ValueError(f"Unknown parameter alias: {param_alias}")
    return _parse_value(_param, value), _param

def _handle_command(arg):
    if not is_command(arg):
        raise ValueError(f"Unknown command alias: {arg}")
    queue_command(arg)

def _set_defaults():
    for _param in _params.values():
        if is_toggle_param(_param):
            set_config_value(_param, get_param_default(_param, False))
        else:
            if param_has_default(_param):
                set_config_value(_param, get_param_default(_param))

def handle_cli_args(args: list[str]):
    """Handle command-line arguments with run-level processing.
    
    Processes run-levels in registration order. Each run-level activates
    a subset of params/commands and can set config values.
    """
    # Check for help command before processing
    from .help import handle_help_with_arg, display_all_help
    if handle_help_with_arg(args):
        return
    
    # Process run-levels in registration order
    run_levels = get_all_run_levels()
    
    if run_levels:
        # Process each run-level
        for run_level in run_levels:
            run_level_name = run_level.get(RUN_LEVEL_NAME)
            
            # Register params for this run-level
            build_params_for_run_level(run_level_name)
            
            # Set defaults from run-level config
            apply_run_level_config(run_level_name)
            
            _set_defaults()
            
            # Parse command line for this run-level's params
            _parse_command_line(args)
            
            # Queue commands for this run-level
            if RUN_LEVEL_COMMANDS in run_level:
                for cmd_name in run_level[RUN_LEVEL_COMMANDS]:
                    if is_command(cmd_name):
                        queue_command(cmd_name)
            
            # Execute this run-level's command queue
            run_command_queue()
        
        # After all run-levels, display help if no app-defined commands were queued
        if not has_app_commands_queued():
            display_all_help()
            return
    else:
        # No run-levels defined - process everything normally
        build_params_for_run_level()
        
        _set_defaults()
        _do_pre_parse_actions()
        _parse_command_line(args)
        _do_post_parse_actions()
        
        # Display help if no app-defined commands were queued
        if not has_app_commands_queued():
            display_all_help()
            return
        
        run_command_queue()
