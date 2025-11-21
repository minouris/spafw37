import sys
import json
import shlex
import re

from spafw37 import command, logging
from spafw37 import config_func as config
from spafw37 import logging as logging_module
from spafw37 import param
from spafw37 import file as spafw37_file
import spafw37.config
from spafw37.constants.param import (
    PARAM_ALIASES,
    PARAM_HAS_VALUE,
    PARAM_NAME,
)

# Functions to run before parsing the command line
_pre_parse_actions = []

# Functions to run after parsing the command line
_post_parse_actions = []

def add_pre_parse_action(action):
    _pre_parse_actions.append(action)

def add_pre_parse_actions(actions):
    for action in actions:
        _pre_parse_actions.append(action)

def add_post_parse_action(action):
    _post_parse_actions.append(action)

def add_post_parse_actions(actions):
    for action in actions:
        _post_parse_actions.append(action)

def _do_post_parse_actions():
    for action in _post_parse_actions:
        try:
            action()
        except Exception as e:
            logging_module.log_error(_scope='cli', _message=f'Post-parse action failed: {e}')
            raise e

def _do_pre_parse_actions():
    for action in _pre_parse_actions:
        try:
            action()
        except Exception as e:
            logging_module.log_error(_scope='cli', _message=f'Pre-parse action failed: {e}')
            pass

def _parse_cli_args(args):
    """Parse command-line arguments into structured dict.
    
    Tokenizes args into commands and parameters with their values.
    
    Args:
        args: List of command-line argument strings.
        
    Returns:
        Dict with structure:
        {
            "commands": [command_names],
            "params": {"--alias": [captured_tokens]}
        }
    """
    parsed = {
        "commands": [],
        "params": []
    }
    
    argument_index = 0
    arguments_count = len(args)
    current_capture_alias = None
    
    while argument_index < arguments_count:
        token = args[argument_index].strip()
        if not _is_quoted_token(token) and command.is_command(token):
            current_capture_alias = None
            parsed["commands"].append(token)
            is_accumulating_value = False
            argument_index += 1
            continue
        if not _is_quoted_token(token) and (param.is_alias(token) or param.is_long_alias_with_value(token)):
            current_capture_alias = None
            if not param.is_long_alias_with_value(token):
                # Simple alias without embedded value
                parsed["params"].append({ "alias": token, "values": []})
                current_capture_alias = token
                argument_index += 1
                continue
            # If it's a long alias with embedded value (--param=value), split it,
            #  assign the alias to current_capture_alias, and treat the value as token,
            #  and fall through to capture the value.
            alias, raw_value = token.split('=', 1)
            parsed["params"].append({ "alias": alias, "values": []})
            current_capture_alias = alias
            token = raw_value
        # If we have a current param that we're capturing values for...
        if current_capture_alias:               
            if token.startswith('@'):
                token = spafw37_file._read_file_raw(token)
                # Check if content looks like JSON object (dict param)
                prefix = token[:10].lstrip()
                if not prefix.startswith('{'):
                    parsed["params"][-1]["values"].extend(shlex.split(token))
                else:
                    parsed["params"][-1]["values"].append(token)
            else:
                parsed["params"][-1]["values"].append(token)
            argument_index += 1
            continue
        raise ValueError(f"Unknown argument or command: {token}")
    return parsed


def _parse_cli_args_regex(args):
    """Parse command-line arguments using regex pattern matching.
    
    Alternative implementation that uses a comprehensive regex pattern to extract
    aliases and their values from the joined args string. Produces the same output
    format as _parse_cli_args().
    
    Pattern matches:
    - Aliases: --long-name, -s (1-2 dashes followed by word chars/hyphens)
    - Values: Any of @file, quoted strings, JSON objects/arrays, or unquoted values
    
    Commands are identified by removing all matched param patterns from the
    args string - what remains are command tokens.
    
    Args:
        args: List of command-line argument strings.
        
    Returns:
        Dict with structure:
        {
            "commands": [command_names],
            "params": [{"alias": "--name", "values": ["val1", "val2"]}]
        }
    """
    parsed = {
        "commands": [],
        "params": []
    }
    
    # Join args into single string for regex processing
    args_string = ' '.join(args)
    remaining_string = args_string
    
    # Comprehensive pattern to match alias and optional value
    # Group 1: alias (--name or -n) - must start after word boundary
    # Group 2: value (optional - anything: @file, quoted, JSON, or unquoted)
    pattern = r'''(?:^|[\s])((?:-{1,2})[\w][\w-]*)(?:(?:=|[\s]+)((?:@[\w.\-_/]+|['"][^'"]*['"]|\{[^}]*\}|\[[^\]]*\]|[^\s]+)))?'''
    
    matches = re.finditer(pattern, args_string)
    
    for match in matches:
        alias = match.group(1)
        value = match.group(2)
        
        # Create new param entry for each occurrence
        parsed["params"].append({
            "alias": alias,
            "values": [value] if value else []
        })
        
        # Remove this match from the remaining string
        remaining_string = remaining_string[:match.start()] + ' ' * (match.end() - match.start()) + remaining_string[match.end():]
    
    # Extract command tokens from remaining string
    parsed["commands"] = remaining_string.split()
    
    return parsed

def _parse_command_line(args):
    """Parse command-line arguments and execute commands.
    
    Iterates through arguments, handling commands and parameters.
    
    Args:
        args: List of command-line argument strings.
    """
    tokens = _parse_cli_args(args)
    for command_name in tokens["commands"]:
        command.queue_command(command_name)
    for _param in tokens["params"]:
        alias = _param["alias"]
        values = _param["values"]
        # First check if the alias is registered
        if not param.get_param_by_alias(alias):
            raise ValueError(f"Unknown parameter alias: {alias}")
        if param.is_toggle_param(alias=alias):
            # Toggles should not have any values assigned
            if len(values) > 0:
                raise ValueError(f"Toggle param does not take values: {alias}")
            param.set_param_value(alias=alias, value=None)
        elif param.is_number_param(alias=alias):
            # These params should have one arg value per assignment
            if len(values) != 1:
                raise ValueError(f"Number params can only have a single value: {alias}")
            param.set_param_value(alias=alias, value=values[-1])
        elif param.is_text_param(alias=alias):
            # Strings should be joined with spaces if multiple args given
            param.set_param_value(alias=alias, value=' '.join(values))
        elif param.is_dict_param(alias=alias):
            # Join all tokens and pass as string - param layer will parse and validate
            param.join_param_value(alias=alias, value=''.join(values))
        elif param.is_list_param(alias=alias):
            # Just append the values to the list
            param.join_param_value(alias=alias, value=values)
        else:
            raise ValueError(f"Unknown param type for alias: {alias}")


def _set_defaults():
    """Set default values for all registered parameters."""
    for param_definition in param.get_all_param_definitions():  # Updated function name
        if param._is_toggle_param(param_definition):
            _def = param._get_param_default(param_definition, False)
            print(f"Setting default for toggle param '{param_definition.get(PARAM_NAME)}'= {_def}")
            config.set_config_value(param_definition, param._get_param_default(param_definition, False))
        else:
            if param._param_has_default(param_definition):
                _def = param._get_param_default(param_definition, None)
                logging.log_trace(_message=f"Setting default for param '{param_definition.get(PARAM_NAME)}'= {_def}")
                config.set_config_value(param_definition, param._get_param_default(param_definition))

def _pre_parse_params(tokenized_args):
    """Silently parse pre-registered params before main CLI parsing.
    
    This allows certain params (e.g., logging/verbosity) to be parsed
    early so they can control behavior during main parsing.
    
    Args:
        tokenized_args: Pre-tokenized dict from _parse_cli_args_regex() with structure:
                        {"commands": [...], "params": [{"alias": "--name", "values": [...]}]}
    """
    preparse_definitions = param.get_pre_parse_args()
    if not preparse_definitions:
        return
    
    # Build a map of preparse param names for quick lookup
    preparse_names = {param_def.get(PARAM_NAME) for param_def in preparse_definitions}
    
    # Process params from tokenized args
    for param_entry in tokenized_args["params"]:
        alias = param_entry["alias"]
        values = param_entry["values"]
        
        # Get param definition for this alias
        param_def = param.get_param_by_alias(alias)
        if not param_def:
            continue
        
        param_name = param_def.get(PARAM_NAME)
        
        # Only process if this is a preparse param
        if param_name not in preparse_names:
            continue
        
        # Set the value based on param type
        if param.is_toggle_param(alias=alias):
            param.set_param_value(param_name=param_name, value=None)
        else:
            # For non-toggle params, use the first value
            if values:
                param.set_param_value(param_name=param_name, value=values[0])
            else:
                # No value provided for non-toggle param
                param.set_param_value(param_name=param_name, value=None)


def handle_cli_args(args):
    """Handle command-line arguments.
    
    Processes command-line arguments, setting config values and executing commands.
    """
    # Check for help command before processing
    from spafw37 import help as help_module
    if help_module.handle_help_with_arg(args):
        return
    
    # Execute pre-parse actions (e.g., load persistent config)
    _do_pre_parse_actions()
    
    # Tokenize arguments once using regex parser
    # This produces a dict that can be used for both pre-parse and main parse
    tokenized_args = _parse_cli_args_regex(args)
    
    # Store original args for conflict checking
    global _current_args
    _current_args = args
    
    # Pre-parse specific params (e.g., logging/verbosity controls)
    # before main parsing to configure behavior
    _pre_parse_params(tokenized_args)
    
    # Apply logging configuration based on pre-parsed params
    logging_module.apply_logging_config()
    
    # Set defaults for all parameters
    _set_defaults()

    # Parse command line arguments (using traditional parser for now)
    _parse_command_line(args)
    
    # Execute queued commands
    command.run_command_queue()
    
    # Execute post-parse actions (e.g., save persistent config)
    _do_post_parse_actions()
    
    # After all run-levels, display help if no app-defined commands were queued
    if not command.has_app_commands_queued():
        help_module.display_all_help()
        return


# Helper functions ---------------------------------------------------------
def _is_quoted_token(token):
    """Return True when a token is a quoted string (e.g. '"value"' or "'value'").

    This helps recognise values that look like aliases but were intentionally
    quoted by the caller. Shells normally strip quotes; this is primarily for
    testing or frontends that preserve quote characters.
    """
    return (isinstance(token, str)
            and len(token) >= 2
            and ((token[0] == token[-1]) and token[0] in ('"', "'")))


def _accumulate_json_for_dict_param(args, start_index, base_offset, arguments_count, param_module, command_module, is_quoted_fn):
    """Accumulate tokens starting at start_index to form a valid JSON object.

    Returns (offset, value) where offset is the total args consumed (base_offset + index)
    and value is the joined JSON string or single-token file reference.
    """
    argument = args[start_index]
    # If it starts with '@' -> file reference single token
    if isinstance(argument, str) and argument.startswith('@'):
        return base_offset + start_index, argument

    # If looks like JSON start, try to accumulate tokens until valid JSON is parsed
    if isinstance(argument, str) and argument.lstrip().startswith('{'):
        token_parts = [argument]
        token_index = start_index + 1
        while token_index < arguments_count:
            next_argument = args[token_index]
            # stop if next token is an alias for another param or a command
            if param_module.is_alias(next_argument) and not is_quoted_fn(next_argument):
                break
            if command_module.is_command(next_argument):
                break
            token_parts.append(next_argument)
            candidate_json = ' '.join(token_parts)
            try:
                json.loads(candidate_json)
                # success
                return base_offset + token_index, candidate_json
            except (json.JSONDecodeError, ValueError):
                token_index += 1
                continue
        # If we fall out without successful parse, try one final join attempt
        candidate_json = ' '.join(token_parts)
        try:
            json.loads(candidate_json)
            return base_offset + (start_index + len(token_parts) - 1), candidate_json
        except (json.JSONDecodeError, ValueError):
            raise ValueError("Could not parse JSON for dict parameter; quote the JSON or use @file")

    # Not JSON start and not file reference: treat single token and let param parser handle it
    return base_offset + start_index, argument
