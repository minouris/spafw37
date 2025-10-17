from __future__ import annotations
import sys
from .config import _persistent_config, _temporary_config_names, config
from typing import Callable

# Params to set on the command line
_params = []

# Commands to run from the command line
_commands = []

# Functions to run before parsing the command line
_pre_parse_actions = []

# Functions to run after parsing the command line
_post_parse_actions = []

_command_queue = []

def add_param(param: dict):
    if (param.get('temporary') is True):
        _temporary_config_names.append(param['name'])
    _params.append(param)

def add_params(params: list[dict]):
    for param in params:
       add_param(param)

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

def do_post_parse_actions():
    for action in _post_parse_actions:
        try:
            action()
        except Exception as e:
            # TODO: Log error
            pass

def do_pre_parse_actions():
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
    raise NotImplementedError

def handle_cli_args(args: list[str]):
    do_pre_parse_actions()
    _parse_command_line(args)
    do_post_parse_actions()
    _run_command_queue()
