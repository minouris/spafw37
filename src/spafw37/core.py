"""
Core facade for the spafw37 application framework.

This module provides a high-level interface for interacting with the
spafw37 application framework, including configuration management,
command registration, and parameter handling.
"""

# Deprecation tracking
_deprecated_warnings_shown = set()
_suppress_deprecation_warnings = False


def _deprecated(message):
    """
    Decorator to mark functions as deprecated with one-time warning.
    
    Args:
        message: Deprecation message explaining the alternative.
    
    Returns:
        Decorator function that wraps the deprecated function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not _suppress_deprecation_warnings:
                func_name = func.__name__
                if func_name not in _deprecated_warnings_shown:
                    _deprecated_warnings_shown.add(func_name)
                    from spafw37 import logging as spafw37_logging
                    spafw37_logging.warning(f"{func_name}() is deprecated. {message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def suppress_deprecation(suppress=True):
    """
    Control deprecation warning display.
    
    Allows developers to suppress deprecation warnings during migration.
    Useful for large codebases migrating to new API gradually.
    
    Args:
        suppress: If True, suppress deprecation warnings. If False, enable them.
    
    Example:
        import spafw37
        spafw37.suppress_deprecation(True)  # Silence warnings during migration
        # ... migration code ...
        spafw37.suppress_deprecation(False)  # Re-enable warnings
    """
    global _suppress_deprecation_warnings
    _suppress_deprecation_warnings = suppress


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

def _default_output_handler(message):
    print(message)

_output_handler = _default_output_handler

def set_output_handler(_handler=_default_output_handler):
    """
    Set a custom output handler for framework output.
    
    Args:
        _handler: A callable that takes a message string. Defaults to built-in print().
    """
    global _output_handler
    _output_handler = _handler

def output(message="", verbose=False, output_handler=None):
    """
    Output a message respecting silent/verbose modes.
    
    Args:
        message: The message to output.
        verbose: If True, only outputs when verbose mode is enabled.
        output_handler: Optional custom handler for this call. If None, uses global handler.
    """
    from spafw37 import config
    if config.is_silent():
        return
    if verbose and not config.is_verbose():
        return
    handler = output_handler if output_handler is not None else _output_handler
    handler(message)


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

def get_max_cycle_nesting_depth():
    """Get the maximum allowed nesting depth for cycles.
    
    Returns:
        Maximum nesting depth (default: 5)
    """
    from spafw37 import config
    return config.get_max_cycle_nesting_depth()


def set_max_cycle_nesting_depth(depth):
    """Set the maximum allowed nesting depth for cycles.
    
    This controls how deeply cycles can be nested within each other.
    The default value of 5 is sufficient for most use cases. Increase
    this value if you need deeply nested cycle structures.
    
    Args:
        depth: Maximum nesting depth (must be positive integer)
        
    Raises:
        ValueError: If depth is not a positive integer
    """
    from spafw37 import config
    config.set_max_cycle_nesting_depth(depth)

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


def get_config_dict(config_key, default=None):
    """
    Get a configuration value as dictionary.
    
    Args:
        config_key: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Dictionary configuration value or default (empty dict if default is None).
    """
    from spafw37 import config
    return config.get_config_dict(config_key, default)


def set_config_value(config_key, value):
    """
    Set a configuration value.
    """
    from spafw37 import config
    config.set_config_value(config_key, value)


def is_verbose():
    """Check if verbose mode is enabled.
    
    Returns:
        True if verbose logging is enabled, False otherwise.
    """
    from spafw37 import config
    return config.is_verbose()


def is_silent():
    """Check if silent mode is enabled.
    
    Returns:
        True if silent mode is enabled, False otherwise.
    """
    from spafw37 import config
    return config.is_silent()


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
