"""
spafw37 - A minimal Python 3.7 framework for CLI applications.

This module provides parameter registration, run-level parsing, command execution,
and configuration management capabilities.
"""

from .param import register_param, register_run_level, add_param, add_params
from .cli import build_parser, parse_args, get_effective_config, handle_cli_args
from .command import add_command, add_commands
from .config import set_config_file, get_config_value, set_config_value

__all__ = [
    'register_param',
    'register_run_level',
    'add_param',
    'add_params',
    'build_parser',
    'parse_args',
    'get_effective_config',
    'handle_cli_args',
    'add_command',
    'add_commands',
    'set_config_file',
    'get_config_value',
    'set_config_value',
]
