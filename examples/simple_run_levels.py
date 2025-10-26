"""Simple example of buffered parameter registration with run-levels.

This demonstrates how modules can register parameters as dictionaries
and how run-levels can be used to provide different default configurations.
Run-levels are executed automatically in registration order.
"""

from spafw37.param import add_param, register_run_level
from spafw37.cli import handle_cli_args
from spafw37.config import get_config_value
from spafw37.config_consts import (
    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE
)


def main():
    """Example application entry point."""
    
    # Register parameters as dictionaries (structs)
    add_param({
        PARAM_NAME: 'host',
        PARAM_ALIASES: ['--host', '-h'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'localhost'
    })
    
    add_param({
        PARAM_NAME: 'port',
        PARAM_ALIASES: ['--port', '-p'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 8000
    })
    
    add_param({
        PARAM_NAME: 'debug',
        PARAM_ALIASES: ['--debug', '-d'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False
    })
    
    # Register run-levels
    # These will be executed in registration order (dev, then prod)
    # Later run-levels override earlier ones
    register_run_level('dev', {
        'host': 'dev.local',
        'port': 3000,
        'debug': True
    })
    
    register_run_level('prod', {
        'host': 'prod.example.com',
        'port': 443,
        'debug': False
    })
    
    # Parse command-line arguments
    # Run-levels are automatically processed in registration order
    # CLI arguments override run-level defaults
    import sys
    handle_cli_args(sys.argv[1:])
    
    # Get configuration values (after run-level merging and CLI overrides)
    # Since 'prod' is registered after 'dev', prod defaults will be used
    # unless overridden by CLI args
    print("Configuration:")
    print(f"  host: {get_config_value('host')}")
    print(f"  port: {get_config_value('port')}")
    print(f"  debug: {get_config_value('debug')}")


if __name__ == '__main__':
    main()
