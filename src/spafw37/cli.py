from __future__ import annotations
import sys

from typing import Callable

from .command import run_command_queue, get_command, is_command, queue_command, has_app_commands_queued, CommandParameterError
from .config import list_config_params, set_config_value, get_config_value
from .param import (
    _has_xor_with, _params, get_bind_name, get_param_default, is_alias, 
    is_list_param, is_long_alias_with_value, get_param_by_alias, _parse_value, 
    is_param_alias, is_toggle_param, param_has_default, flush_buffered_registrations,
    get_run_level, list_run_levels
)
from .config_consts import (
    RUN_LEVELS_PARAM, RUN_LEVELS_ALIAS_LONG, RUN_LEVELS_ALIAS_SHORT,
    PARAM_NAME, PARAM_ALIASES, PARAM_DEFAULT, PARAM_BIND_TO
)

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
    # Check for help command before processing
    from .help import handle_help_with_arg, display_all_help
    if handle_help_with_arg(args):
        return
    
    _set_defaults()
    _do_pre_parse_actions()
    _parse_command_line(args)
    _do_post_parse_actions()
    
    # Display help if no app-defined commands were queued
    if not has_app_commands_queued():
        display_all_help()
        return
    
    run_command_queue()


def build_parser():
    """Flush buffered parameter registrations and prepare for parsing.
    
    This function processes all buffered parameter registrations
    and adds them to the parameter registry. It should be called
    before parsing command-line arguments when using buffered registration.
    
    Returns:
        Number of parameters registered from buffer.
    """
    return flush_buffered_registrations()


def _normalize_run_levels_input(run_levels_raw):
    """Normalize run-levels input into a flat list.
    
    Handles both comma-separated strings and lists of strings.
    
    Args:
        run_levels_raw: Single string, list of strings, or None.
        
    Returns:
        List of run-level names in order.
    """
    if not run_levels_raw:
        return []
    
    if isinstance(run_levels_raw, str):
        run_levels_raw = [run_levels_raw]
    
    normalized = []
    for item in run_levels_raw:
        if ',' in item:
            normalized.extend([level.strip() for level in item.split(',')])
        else:
            normalized.append(item.strip())
    
    return [level for level in normalized if level]


def _merge_run_levels(run_levels_list, base_defaults):
    """Merge run-level defaults in order over base defaults.
    
    Args:
        run_levels_list: List of run-level names to merge in order.
        base_defaults: Base default values dictionary.
        
    Returns:
        Dictionary with merged values.
    """
    import warnings
    
    effective = dict(base_defaults)
    
    for level_name in run_levels_list:
        level_defaults = get_run_level(level_name)
        if level_defaults is None:
            warnings.warn(f"Unknown run-level '{level_name}', ignoring")
            continue
        
        effective.update(level_defaults)
    
    return effective


def _extract_cli_overrides(args):
    """Extract explicitly provided CLI parameter values.
    
    This parses the arguments to identify which parameters were
    explicitly set on the command line (not from defaults).
    
    Args:
        args: List of command-line argument strings.
        
    Returns:
        Dictionary mapping bind names to explicitly provided values.
    """
    cli_overrides = {}
    idx = 0
    size = len(args)
    
    while idx < size:
        arg = args[idx]
        
        if is_command(arg):
            idx += 1
            continue
        
        if arg in [RUN_LEVELS_ALIAS_LONG, RUN_LEVELS_ALIAS_SHORT]:
            idx += 2
            continue
        
        if is_long_alias_with_value(arg):
            param_alias, value = arg.split('=', 1)
            param_def = get_param_by_alias(param_alias)
            if param_def:
                bind_name = get_bind_name(param_def)
                cli_overrides[bind_name] = _parse_value(param_def, value)
            idx += 1
            continue
        
        if is_alias(arg):
            param_def = get_param_by_alias(arg)
            if param_def:
                bind_name = get_bind_name(param_def)
                if is_toggle_param(param_def):
                    cli_overrides[bind_name] = _parse_value(param_def, None)
                    idx += 1
                else:
                    offset, value = capture_param_values(args[idx:], param_def)
                    if value:
                        cli_overrides[bind_name] = _parse_value(param_def, value)
                    idx += offset
                continue
        
        idx += 1
    
    return cli_overrides


def _get_base_defaults():
    """Extract base defaults from registered parameters.
    
    Returns:
        Dictionary mapping bind names to default values.
    """
    base_defaults = {}
    for param_def in _params.values():
        bind_name = get_bind_name(param_def)
        if param_has_default(param_def):
            base_defaults[bind_name] = get_param_default(param_def)
        elif is_toggle_param(param_def):
            base_defaults[bind_name] = get_param_default(param_def, False)
    return base_defaults


def get_effective_config(args):
    """Compute effective configuration from run-levels and CLI args.
    
    Merges configuration in this order:
    1. Base parameter defaults
    2. Run-levels in specified order (later overrides earlier)
    3. Explicit CLI arguments (highest precedence)
    
    Args:
        args: List of command-line argument strings.
        
    Returns:
        Dictionary with effective configuration values.
    """
    run_levels_raw = []
    idx = 0
    
    while idx < len(args):
        if args[idx] in [RUN_LEVELS_ALIAS_LONG, RUN_LEVELS_ALIAS_SHORT]:
            if idx + 1 < len(args):
                run_levels_raw.append(args[idx + 1])
                idx += 2
            else:
                idx += 1
        else:
            idx += 1
    
    run_levels_list = _normalize_run_levels_input(run_levels_raw)
    base_defaults = _get_base_defaults()
    effective = _merge_run_levels(run_levels_list, base_defaults)
    cli_overrides = _extract_cli_overrides(args)
    effective.update(cli_overrides)
    
    return effective


def parse_args(args, merge_run_levels=True):
    """Parse command-line arguments with run-level support.
    
    This is a convenience function that handles the complete parsing flow:
    - Extracts run-levels if merge_run_levels is True
    - Computes effective configuration
    - Returns both the parsed namespace-like dict and effective config
    
    Args:
        args: List of command-line argument strings, or None for sys.argv[1:].
        merge_run_levels: Whether to apply run-level merging.
        
    Returns:
        Tuple of (namespace_dict, effective_config_dict).
    """
    if args is None:
        args = sys.argv[1:]
    
    if merge_run_levels:
        effective = get_effective_config(args)
    else:
        effective = _get_base_defaults()
        cli_overrides = _extract_cli_overrides(args)
        effective.update(cli_overrides)
    
    return effective, effective

