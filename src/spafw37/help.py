import sys
import os

from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_GROUP,
    PARAM_CONFIG_NAME,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_HELP,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_EXCLUDE_HELP,
)
from spafw37 import cycle


def _get_all_commands():
    """Get all registered commands.
    
    Returns:
        dict: Dictionary of all registered commands.
    """
    from spafw37 import command
    return command._commands


def _get_all_params():
    """Get all registered parameters.
    
    Returns:
        dict: Dictionary of all registered parameters.
    """
    from spafw37 import param
    return param._params


def _get_command_params(command_name):
    """Get parameter names required by a command.
    
    Args:
        command_name: Name of the command.
        
    Returns:
        List of parameter bind names required by the command.
    """
    commands = _get_all_commands()
    cmd = commands.get(command_name, {})
    return cmd.get(COMMAND_REQUIRED_PARAMS, [])


def _get_param_by_bind_name(bind_name):
    """Get parameter definition by bind name.
    
    Args:
        bind_name: The bind_to value of the parameter.
        
    Returns:
        Parameter definition dict or None if not found.
    """
    all_params = _get_all_params()
    for param in all_params.values():
        if param.get(PARAM_CONFIG_NAME, param.get(PARAM_NAME)) == bind_name:
            return param
    return None


def _format_param_table_row(param):
    """Format a single parameter as a table row.
    
    Args:
        param: Parameter definition dict.
        
    Returns:
        Formatted string representing the parameter.
    """
    aliases = param.get(PARAM_ALIASES, [])
    aliases_str = ', '.join(aliases) if aliases else ''
    name = param.get(PARAM_NAME, '')
    description = param.get(PARAM_DESCRIPTION, '')
    return f"  {aliases_str:<20} {name:<25} {description}"


def _get_non_command_params():
    """Get parameters that are not directly tied to any command.
    
    Returns:
        List of parameter dicts that are not required by any command.
    """
    all_params = _get_all_params()
    commands = _get_all_commands()
    
    # Collect all bind names used by commands
    command_param_binds = set()
    for cmd in commands.values():
        required_params = cmd.get(COMMAND_REQUIRED_PARAMS, [])
        command_param_binds.update(required_params)
    
    # Filter params not used by commands
    non_command_params = []
    for param in all_params.values():
        bind_name = param.get(PARAM_CONFIG_NAME, param.get(PARAM_NAME))
        if bind_name not in command_param_binds:
            non_command_params.append(param)
    
    return non_command_params


def _group_params(params):
    """Group parameters by their param-group value.
    
    Args:
        params: List of parameter dicts.
        
    Returns:
        Dict mapping group names to lists of params. None key for ungrouped params.
    """
    grouped = {}
    for param in params:
        group = param.get(PARAM_GROUP)
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(param)
    return grouped


def display_all_help():
    """Display help for all commands and parameters."""
    commands = _get_all_commands()
    non_command_params = _get_non_command_params()
    
    script_name = os.path.basename(sys.argv[0]) if sys.argv else '<app>'
    print()
    print(f"Usage: python {script_name} <command> [<command> ...] [params]")
    print("Note: Commands must come before params.")
    print()
    
    # Display commands
    if commands:
        print("Available Commands:")
        print(f"  {'Command':<25} {'Description'}")
        print(f"  {'-' * 25} {'-' * 50}")
        for cmd_name in sorted(commands.keys()):
            cmd = commands[cmd_name]
            if not cmd.get(COMMAND_EXCLUDE_HELP, False) and cycle.is_command_invocable(cmd):
                description = cmd.get(COMMAND_DESCRIPTION, '')
                print(f"  {cmd_name:<25} {description}")
        print()
    
    # Display non-command parameters grouped
    if non_command_params:
        print("Available Parameters:")
        print(f"  {'Aliases':<20} {'Name':<25} {'Description'}")
        print(f"  {'-' * 20} {'-' * 25} {'-' * 50}")
        
        grouped_params = _group_params(non_command_params)
        
        # Display ungrouped params first (group == None)
        if None in grouped_params:
            for param in sorted(grouped_params[None], key=lambda p: p.get(PARAM_NAME, '')):
                print(_format_param_table_row(param))
        
        # Display grouped params
        for group_name in sorted(k for k in grouped_params.keys() if k is not None):
            print()
            print(f"  {group_name}:")
            for param in sorted(grouped_params[group_name], key=lambda p: p.get(PARAM_NAME, '')):
                print(_format_param_table_row(param))
        
        print()


def display_command_help(command_name):
    """Display help for a specific command.
    
    Args:
        command_name: Name of the command to display help for.
    """
    commands = _get_all_commands()
    cmd = commands.get(command_name)
    
    if not cmd:
        print(f"Unknown command: {command_name}")
        print()
        display_all_help()
        return
    
    print(f"Command: {command_name}")
    print()
    
    description = cmd.get(COMMAND_DESCRIPTION, '')
    if description:
        print(f"Description: {description}")
        print()
    
    command_help = cmd.get(COMMAND_HELP, '')
    if command_help:
        print(command_help)
        print()
    
    # Display parameters for this command
    param_binds = cmd.get(COMMAND_REQUIRED_PARAMS, [])
    if param_binds:
        print("Parameters:")
        print(f"  {'Aliases':<20} {'Name':<25} {'Description'}")
        print(f"  {'-' * 20} {'-' * 25} {'-' * 50}")
        for bind_name in param_binds:
            param = _get_param_by_bind_name(bind_name)
            if param:
                print(_format_param_table_row(param))
        print()
    
    # Display cycle commands if this command has a cycle
    cycle_commands = cycle.get_cycle_commands(cmd)
    if cycle_commands:
        commands = _get_all_commands()
        print("Cycle Commands:")
        print("  (Use 'help <command>' to see full details for nested commands)")
        print()
        print(f"  {'Command':<25} {'Description'}")
        print(f"  {'-' * 25} {'-' * 50}")
        _display_cycle_commands_recursive(cycle_commands, commands, indent=2)
        print()


def _display_cycle_commands_recursive(cycle_cmd_names, commands, indent=2):
    """Display cycle commands recursively with indentation for nested cycles.
    
    Args:
        cycle_cmd_names: List of command names in the cycle
        commands: Dict of all registered commands
        indent: Current indentation level (spaces)
    """
    indent_str = ' ' * indent
    
    for cycle_cmd_name in cycle_cmd_names:
        cycle_cmd = commands.get(cycle_cmd_name)
        if cycle_cmd:
            desc = cycle_cmd.get(COMMAND_DESCRIPTION, '')
            # Calculate available space for command name (accounting for indent)
            name_width = 25 - indent
            print(f"{indent_str}{cycle_cmd_name:<{name_width}} {desc}")
            
            # Check if this command has nested cycles
            nested_cycle_cmds = cycle.get_cycle_commands(cycle_cmd)
            if nested_cycle_cmds:
                _display_cycle_commands_recursive(nested_cycle_cmds, commands, indent + 2)


def show_help_command():
    """Command action to display general help."""
    display_all_help()


def handle_help_with_arg(args):
    """Handle help command with optional command argument.
    
    Args:
        args: Command line arguments, where args[0] might be 'help'.
        
    Returns:
        True if help was displayed, False otherwise.
    """
    if len(args) > 0 and args[0] == 'help':
        if len(args) > 1:
            # help <command>
            command_name = args[1]
            display_command_help(command_name)
        else:
            # just "help" with no args
            display_all_help()
        return True
    return False
