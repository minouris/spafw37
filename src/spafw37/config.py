from spafw37.constants.phase import PHASE_ORDER, PHASE_DEFAULT

# Import logging parameter names for convenience methods
from spafw37.logging_config import LOG_VERBOSE_PARAM, LOG_SILENT_PARAM

# Import cycle for cycle nesting depth configuration
from spafw37 import cycle as cycle_module

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
                    spafw37_logging.log_warning(_message=f"{func_name}() is deprecated. {message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Config dict to hold runtime parameters
# NOTE: Thread Safety - These module-level variables are not thread-safe.
# This framework is designed for single-threaded CLI applications. If using
# in a multi-threaded context, external synchronization is required.
_config = {
}

_phases_order = PHASE_ORDER
_default_phase = PHASE_DEFAULT

def set_phases_order(phase_order = PHASE_ORDER):
    global _phases_order
    _phases_order = phase_order

def get_phases_order():
    return _phases_order

def set_default_phase(default_phase = PHASE_DEFAULT):
    global _default_phase
    _default_phase = default_phase

def get_default_phase():
    return _default_phase

def get_max_cycle_nesting_depth():
    """Get the maximum allowed nesting depth for cycles.
    
    Returns:
        Maximum nesting depth (default: 5)
    """
    return cycle_module.get_max_cycle_nesting_depth()


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
    cycle_module.set_max_cycle_nesting_depth(depth)

@_deprecated("Use core.get_param_str(), get_param_int(), get_param_bool(), get_param_float(), get_param_list(), or get_param_dict() instead.")
def get_config_value(name):
    """Get configuration value (DEPRECATED).
    
    DEPRECATED: Use core.get_param_str(), get_param_int(), get_param_bool(),
    get_param_float(), get_param_list(), or get_param_dict() instead.
    
    Args:
        name: Configuration key name.
    
    Returns:
        Configuration value or None if not found.
    """
    return _config.get(name)


@_deprecated("Use core.get_param_int() instead.")
def get_config_int(name, default=0):
    """Get configuration value as integer (DEPRECATED).
    
    DEPRECATED: Use core.get_param_int(param_name=name, default=default) instead.
    
    Args:
        name: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Integer configuration value or default.
    """
    value = _config.get(name)
    if value is None:
        return default
    return int(value)


@_deprecated("Use core.get_param_str() instead.")
def get_config_str(name, default=''):
    """Get configuration value as string (DEPRECATED).
    
    DEPRECATED: Use core.get_param_str(param_name=name, default=default) instead.
    
    Args:
        name: Configuration key name.
        default: Default value if not found.
        
    Returns:
        String configuration value or default.
    """
    value = _config.get(name)
    if value is None:
        return default
    return str(value)


@_deprecated("Use core.get_param_bool() instead.")
def get_config_bool(name, default=False):
    """Get configuration value as boolean (DEPRECATED).
    
    DEPRECATED: Use core.get_param_bool(param_name=name, default=default) instead.
    
    Args:
        name: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Boolean configuration value or default.
    """
    value = _config.get(name)
    if value is None:
        return default
    return bool(value)


@_deprecated("Use core.get_param_float() instead.")
def get_config_float(name, default=0.0):
    """Get configuration value as float (DEPRECATED).
    
    DEPRECATED: Use core.get_param_float(param_name=name, default=default) instead.
    
    Args:
        name: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Float configuration value or default.
    """
    value = _config.get(name)
    if value is None:
        return default
    return float(value)


@_deprecated("Use core.get_param_list() instead.")
def get_config_list(name, default=None):
    """Get configuration value as list (DEPRECATED).
    
    DEPRECATED: Use core.get_param_list(param_name=name, default=default) instead.
    
    Args:
        name: Configuration key name.
        default: Default value if not found.
        
    Returns:
        List configuration value or default (empty list if default is None).
    """
    value = _config.get(name)
    if value is None:
        return default if default is not None else []
    if not isinstance(value, list):
        return [value]
    return value


@_deprecated("Use core.get_param_dict() instead.")
def get_config_dict(name, default=None):
    """Get configuration value as dictionary (DEPRECATED).
    
    DEPRECATED: Use core.get_param_dict(param_name=name, default=default) instead.
    
    Args:
        name: Configuration key name.
        default: Default value if not found.
        
    Returns:
        Dictionary configuration value or default (empty dict if default is None).
    """
    value = _config.get(name)
    if value is None:
        return default if default is not None else {}
    if not isinstance(value, dict):
        raise ValueError(f"Configuration value '{name}' is not a dictionary")
    return value


@_deprecated("Use core.set_param() instead.")
def set_config_value(name, value):
    """Set configuration value (DEPRECATED).
    
    DEPRECATED: Use core.set_param(value, param_name=name) instead.
    
    Args:
        name: Configuration key name.
        value: Value to set.
    """
    _config[name] = value


@_deprecated("Use core.join_param() instead.")
def set_config_list_value(value, bind_name):
    """Append value to configuration list (DEPRECATED).
    
    DEPRECATED: Use core.join_param(value, bind_name=bind_name) instead.
    
    Args:
        value: Value to append to the list.
        bind_name: Configuration key name.
    """
    if bind_name not in _config:
        _config[bind_name] = []
    if isinstance(value, list):
        _config[bind_name].extend(value)
    else:
        _config[bind_name].append(value)


def list_config_params():
    return list(_config.keys())

def list_config_items():
    return _config.items()


def update_config(new_config):
    _config.update(new_config)

def is_verbose():
    """Check if verbose mode is enabled.
    
    Returns:
        True if verbose logging is enabled, False otherwise.
    """
    return get_config_bool(LOG_VERBOSE_PARAM, False)


def is_silent():
    """Check if silent mode is enabled.
    
    Returns:
        True if silent mode is enabled, False otherwise.
    """
    return get_config_bool(LOG_SILENT_PARAM, False)
