from __future__ import annotations
import sys

from typing import Callable

from .config import list_config_params, set_config_value
from .param import _has_xor_with, _params, get_bind_name, get_param_default, is_alias, is_list_param, is_long_alias_with_value, get_param_by_alias, _parse_value, is_param_alias, is_toggle_param, param_has_default

# Commands to run from the command line
_commands: list[dict] = []

# Functions to run before parsing the command line
_pre_parse_actions: list[Callable] = []

# Functions to run after parsing the command line
_post_parse_actions: list[Callable] = []

_command_queue: list[dict] = []

def add_command(command: dict):
    _commands.append(command)

def add_commands(commands: list[dict]):
    for command in commands:
        _commands.append(command)

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
            pass

def _do_pre_parse_actions():
    for action in _pre_parse_actions:
        try:
            action()
        except Exception as e:
            # TODO: Log error
            pass

def _run_command_queue():
    for command in _command_queue:
        try:
            command() # type: ignore
        except Exception as e:
            # TODO: Log error
            pass

def is_command(arg):
    # TODO: Implement command check after fixing up add_command()
    return False

def get_command(arg):
    #TODO: Implement command retrieval
    raise NotImplementedError

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
            _command = get_command(arg)
            if not _command:
                raise ValueError(f"Unknown command alias: {arg}")
            _command_queue.append(_command.get('function'))
        elif is_long_alias_with_value(arg):
            param_alias, value = arg.split('=', 1)
            _param = get_param_by_alias(param_alias)
            test_switch_xor(_param)
            if not _param:
                raise ValueError(f"Unknown parameter alias: {param_alias}")
            _value = _parse_value(_param, value)
        elif is_alias(arg):
            _param = get_param_by_alias(arg)
            test_switch_xor(_param)
            if not _param:
                raise ValueError(f"Unknown parameter alias: {arg}")
            _param = get_param_by_alias(arg)
            if is_toggle_param(_param):
                _value = _parse_value(_param, None)
            else:
                _offset, _value = capture_param_values(args[_idx:], _param)
                _idx += _offset
        else:
            raise ValueError(f"Unknown argument or command: {arg}")
        if _param and _value is not None:
            set_config_value(_param, _value)
        _idx += 1

def _set_defaults():
    for _param in _params.values():
        if is_toggle_param(_param):
            set_config_value(_param, get_param_default(_param, False))
        else:
            if param_has_default(_param):
                set_config_value(_param, get_param_default(_param))

def handle_cli_args(args: list[str]):
    _set_defaults()
    _do_pre_parse_actions()
    _parse_command_line(args)
    _do_post_parse_actions()
    _run_command_queue()
