from __future__ import annotations
import sys

from typing import Callable

from .config import set_config_value
from .param import _params, get_param_default, is_alias, is_long_alias_with_value, get_param_by_alias, _parse_value, is_toggle_param, param_has_default

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
            command()
        except Exception as e:
            # TODO: Log error
            pass

def _parse_command_line(args: list[str]):
    _capture_value_mode = False
    _current_param = None
    _idx = 0
    for arg in args:
        if is_long_alias_with_value(arg):
            param_alias, value = arg.split('=', 1)
            _param = get_param_by_alias(param_alias)
            if not _param:
                raise ValueError(f"Unknown parameter alias: {param_alias}")
            set_config_value(_param, _parse_value(_param, value))
            continue
        if is_alias(arg):
            _param = get_param_by_alias(arg)
            if not _param:
                raise ValueError(f"Unknown parameter alias: {arg}")
            if is_toggle_param(_param):
                set_config_value(_param, _parse_value(_param, None))
            _current_param = _param
        if _param:
            set_config_value(_param, True)

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
