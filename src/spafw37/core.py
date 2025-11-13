"""
Core facade for the spafw37 application framework.

This module provides a high-level interface for interacting with the
spafw37 application framework, including configuration management,
command registration, and parameter handling.
"""


def run_cli():
    """
    Run the command-line interface for the application.

    Import this function and call it in your main application 
    file to handle CLI arguments to set params and run commands.
    """
    import sys
    import spafw37.configure  # Ensure configuration is set up
    import spafw37.cli as cli
    from spafw37.command import CommandParameterError
    from spafw37 import help
    
    # Pass user-provided command-line arguments (excluding program name)
    try:
        cli.handle_cli_args(sys.argv[1:])
    except CommandParameterError as e:
        # On command parameter error, display help for that specific command
        print(f"Error: {e}")
        print()
        if e.command_name:
            help.display_command_help(e.command_name)
        else:
            help.display_all_help()
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        print()
        # display_all_help()
        sys.exit(1)


def set_config_file(file_path):
    """
    Set the configuration file.
    """
    from spafw37 import config_func
    config_func.set_config_file(file_path)


def set_app_name(name):
    """
    Set the application name.
    
    Args:
        name: Application name.
    """
    from spafw37 import config_func
    config_func.set_app_name(name)


def get_app_name():
    """
    Get the application name.
    
    Returns:
        Application name.
    """
    from spafw37 import config_func
    return config_func.get_app_name()


def add_params(params):
    """
    Add parameters.
    """
    from spafw37 import param
    param.add_params(params)

def add_param(_param):
    """
    Add a single parameter.
    """
    from spafw37 import param
    param.add_param(_param)

def add_commands(commands):
    """
    Add commands.
    """
    from spafw37 import command 
    command.add_commands(commands)

def add_command(_command):
    """
    Add a single command.
    """
    from spafw37 import command 
    command.add_command(_command)

def set_phases_order(phase_order):
    """
    Set the execution order for phases.
    
    Args:
        phase_order: List of phase names in execution order.
    """
    from spafw37 import config
    config.set_phases_order(phase_order)

def set_default_phase(default_phase):
    """
    Set the default phase for commands that don't specify a phase.
    
    Args:
        default_phase: The phase name to use as default.
    """
    from spafw37 import config
    config.set_default_phase(default_phase)

def get_config_value(config_key):
    """
    Get a configuration value.
    """
    from spafw37 import config
    return config.get_config_value(config_key)


def get_config_int(config_key, default=0):
    """
    Get a configuration value as integer.
    
    Args:
        config_key: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Integer configuration value or default.
    """
    from spafw37 import config
    return config.get_config_int(config_key, default)


def get_config_str(config_key, default=''):
    """
    Get a configuration value as string.
    
    Args:
        config_key: Configuration key name.
        default: Default value if not found.
        
    Returns:
        String configuration value or default.
    """
    from spafw37 import config
    return config.get_config_str(config_key, default)


def get_config_bool(config_key, default=False):
    """
    Get a configuration value as boolean.
    
    Args:
        config_key: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Boolean configuration value or default.
    """
    from spafw37 import config
    return config.get_config_bool(config_key, default)


def get_config_float(config_key, default=0.0):
    """
    Get a configuration value as float.
    
    Args:
        config_key: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Float configuration value or default.
    """
    from spafw37 import config
    return config.get_config_float(config_key, default)


def get_config_list(config_key, default=None):
    """
    Get a configuration value as list.
    
    Args:
        config_key: Configuration key name.
        default: Default value if not found.
        
    Returns:
        List configuration value or default (empty list if default is None).
    """
    from spafw37 import config
    return config.get_config_list(config_key, default)


def set_config_value(config_key, value):
    """
    Set a configuration value.
    """
    from spafw37 import config
    config.set_config_value(config_key, value)


# Logging delegates

def set_log_dir(log_dir):
    """
    Set the log directory.
    
    Args:
        log_dir: Directory path for log files.
    """
    from spafw37 import logging
    logging.set_log_dir(log_dir)


def log_trace(_scope=None, _message=''):
    """
    Log a message at TRACE level.
    
    Args:
        _scope: Optional scope for the log message.
        _message: The message to log.
    """
    from spafw37 import logging
    logging.log_trace(_scope=_scope, _message=_message)


def log_debug(_scope=None, _message=''):
    """
    Log a message at DEBUG level.
    
    Args:
        _scope: Optional scope for the log message.
        _message: The message to log.
    """
    from spafw37 import logging
    logging.log_debug(_scope=_scope, _message=_message)


def log_info(_scope=None, _message=''):
    """
    Log a message at INFO level.
    
    Args:
        _scope: Optional scope for the log message.
        _message: The message to log.
    """
    from spafw37 import logging
    logging.log_info(_scope=_scope, _message=_message)


def log_warning(_scope=None, _message=''):
    """
    Log a message at WARNING level.
    
    Args:
        _scope: Optional scope for the log message.
        _message: The message to log.
    """
    from spafw37 import logging
    logging.log_warning(_scope=_scope, _message=_message)


def log_error(_scope=None, _message=''):
    """
    Log a message at ERROR level.
    
    Args:
        _scope: Optional scope for the log message.
        _message: The message to log.
    """
    from spafw37 import logging
    logging.log_error(_scope=_scope, _message=_message)


def set_current_scope(scope):
    """
    Set the current logging scope.
    
    Args:
        scope: The scope name to use for subsequent log messages.
    """
    from spafw37 import logging
    logging.set_current_scope(scope)
