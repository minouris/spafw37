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


def _parse_file_value(value):
    """Replace @file references in value with file contents.
    
    Scans the value string for @file tokens and replaces each with the
    contents of the referenced file. Multiple @file references in a single
    value are all replaced.
    
    Distinguishes between file references (@filepath) and email addresses
    (user@domain.com) by checking that @ is not preceded by alphanumeric chars.
    Stops at structural characters like }, ], ), or whitespace.
    
    Args:
        value: String potentially containing @file references
        
    Returns:
        String with @file tokens replaced by file contents
        
    Raises:
        FileNotFoundError: If any referenced file doesn't exist
        PermissionError: If any referenced file isn't readable
        ValueError: If any referenced file is binary
    """
    import re
    
    # Pattern to match @file references but not email addresses:
    # - Negative lookbehind (?<!\w) ensures @ is not preceded by word char
    # - @ symbol
    # - Capture group for filepath: chars that aren't whitespace or JSON/shell delimiters
    # This matches @path/to/file.txt but not user@example.com
    # Stops at }, ], ), comma, or whitespace to work inside JSON structures
    file_pattern = r'(?<!\w)@([^\s\}\]\),]+)'
    
    def replace_file_token(match):
        """Replace a single @file token with its contents."""
        file_path = match.group(1)
        # Use the file module's read function (includes @ prefix handling)
        return spafw37_file._read_file_raw('@' + file_path)
    
    # Replace all @file tokens with their contents
    return re.sub(file_pattern, replace_file_token, value)


def _do_pre_parse_actions():
    for action in _pre_parse_actions:
        try:
            action()
        except Exception as e:
            logging_module.log_error(_scope='cli', _message=f'Pre-parse action failed: {e}')
            pass

def _tokenise_cli_args(args):
    """Tokenize command-line arguments using regex pattern matching.
    
    Uses a comprehensive regex pattern to extract aliases and their values
    from the joined args string.
    
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
            "params": [{"alias": "--name", "value": "val1"}]
        }
    """
    parsed = {
        "commands": [],
        "params": []
    }
    
    # Join args into single string for regex processing
    args_string = ' '.join(args)
    remaining_string = args_string
    
    # Pattern matches alias and captures everything until next alias or end
    # Group 1: alias (--name or -n) - must start after word boundary
    # Group 2: value with = separator (e.g., --name=value)
    # Group 3: value with space separator, capturing all non-dash-prefixed tokens
    #          (e.g., --files a.txt b.txt captures "a.txt b.txt")
    pattern = r'''(?:^|\s)((?:-{1,2})[\w][\w-]*)(?:=([^\s]+)|(?:\s+([^-\s][^\s]*(?:\s+[^-\s][^\s]*)*))?)?'''
    
    matches = re.finditer(pattern, args_string)
    
    for match in matches:
        alias = match.group(1)
        # Value can be in group 2 (=value) or group 3 (space-separated)
        value = match.group(2) if match.group(2) else (match.group(3) if match.group(3) else None)
        
        # Create new param entry for each occurrence
        parsed["params"].append({
            "alias": alias,
            "value": value
        })
        
        # Remove this match from the remaining string
        remaining_string = remaining_string[:match.start()] + ' ' * (match.end() - match.start()) + remaining_string[match.end():]
    
    # Extract command tokens from remaining string
    parsed["commands"] = remaining_string.split()
    
    return parsed

def _parse_command_line(tokens):
    """Parse command-line arguments and execute commands.
    
    Iterates through tokenized arguments, handling commands and parameters.
    
    Args:
        tokens: Pre-tokenized dict from _tokenise_cli_args() with structure:
                {"commands": [...], "params": [{"alias": "--name", "value": "val1"}]}
    """
    for command_name in tokens["commands"]:
        command.queue_command(command_name)
    for _param in tokens["params"]:
        alias = _param["alias"]
        value = _param["value"]
        
        # Replace @file references with file contents
        # Use regex check to avoid false positives with email addresses
        if value and re.search(r'(?<!\w)@\S+', value):
            value = _parse_file_value(value)
        
        # For list and dict params, accumulate values; for all others, set directly
        if param.is_list_param(alias=alias) or param.is_dict_param(alias=alias):
            param.join_param_value(alias=alias, value=value)
        else:
            param.set_param_value(alias=alias, value=value)


def _set_defaults():
    """Set default values for all registered parameters."""
    # Disable XOR validation while setting defaults to avoid false conflicts
    param._set_xor_validation_enabled(False)
    try:
        for param_definition in param.get_all_param_definitions():
            param_name = param_definition.get(PARAM_NAME)
            if param._is_toggle_param(param_definition):
                _def = param._get_param_default(param_definition, False)
                print(f"Setting default for toggle param '{param_name}'= {_def}")
                param.set_param_value(param_name=param_name, value=_def)
            else:
                if param._param_has_default(param_definition):
                    _def = param._get_param_default(param_definition, None)
                    logging.log_trace(_message=f"Setting default for param '{param_name}'= {_def}")
                    param.set_param_value(param_name=param_name, value=_def)
    finally:
        # Always re-enable XOR validation after setting defaults
        param._set_xor_validation_enabled(True)

def _pre_parse_params(tokenized_args):
    """Silently parse pre-registered params before main CLI parsing.
    
    This allows certain params (e.g., logging/verbosity) to be parsed
    early so they can control behavior during main parsing.
    
    Args:
        tokenized_args: Pre-tokenized dict from _tokenise_cli_args() with structure:
                        {"commands": [...], "params": [{"alias": "--name", "value": "val1"}]}
    """
    preparse_definitions = param.get_pre_parse_args()
    if not preparse_definitions:
        return
    
    # Build a map of preparse param names for quick lookup
    preparse_names = {param_def.get(PARAM_NAME) for param_def in preparse_definitions}
    
    # Process params from tokenized args
    for param_entry in tokenized_args["params"]:
        alias = param_entry["alias"]
        value = param_entry["value"]
        
        # Get param definition for this alias
        param_def = param.get_param_by_alias(alias)
        if not param_def:
            continue
        
        param_name = param_def.get(PARAM_NAME)
        
        # Only process if this is a preparse param
        if param_name not in preparse_names:
            continue
        
        # Set the value
        param.set_param_value(param_name=param_name, value=value)


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
    tokenized_args = _tokenise_cli_args(args)
    
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

    # Parse command line arguments using regex tokenizer
    _parse_command_line(tokenized_args)
    
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
