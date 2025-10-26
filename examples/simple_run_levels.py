"""Simple example of buffered parameter registration with run-levels.

This demonstrates how run-levels sandbox parts of configuration to run
in isolation with defined sets of params, commands, and preset config values.
For example, a 'help' run-level can process help requests before the main
application runs.
"""

from spafw37.param import add_param, add_run_level
from spafw37.cli import handle_cli_args
from spafw37.config import get_config_value
from spafw37.config_consts import (
    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE,
    RUN_LEVEL_NAME, RUN_LEVEL_PARAMS, RUN_LEVEL_COMMANDS, RUN_LEVEL_CONFIG
)


def main():
    """Example application entry point."""
    
    # Register parameters as dictionaries (structs)
    add_param({
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose', '-v'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False
    })
    
    add_param({
        PARAM_NAME: 'log_level',
        PARAM_ALIASES: ['--log-level', '-l'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'info'
    })
    
    add_param({
        PARAM_NAME: 'port',
        PARAM_ALIASES: ['--port', '-p'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 8000
    })
    
    # Define run-levels to sandbox configuration
    # 'init' run-level: process logging params first
    add_run_level({
        RUN_LEVEL_NAME: 'init',
        RUN_LEVEL_PARAMS: ['verbose', 'log_level'],  # Only these params are active
        RUN_LEVEL_COMMANDS: [],  # Could queue logging setup commands
        RUN_LEVEL_CONFIG: {
            'verbose': True,  # Override defaults for this level
            'log_level': 'debug'
        }
    })
    
    # 'main' run-level: process remaining params and run main app
    add_run_level({
        RUN_LEVEL_NAME: 'main',
        RUN_LEVEL_PARAMS: ['port'],  # Only port param active in this level
        RUN_LEVEL_COMMANDS: [],  # App commands would go here
        RUN_LEVEL_CONFIG: {
            'port': 3000
        }
    })
    
    # Parse command-line arguments
    # Run-levels execute automatically in registration order (init, then main)
    # Each run-level activates only its params and executes its commands
    # CLI arguments override run-level config values
    import sys
    handle_cli_args(sys.argv[1:])
    
    # Get configuration values
    # Since run-levels executed in order, we see the cumulative effect
    print("Configuration after run-level processing:")
    print(f"  verbose: {get_config_value('verbose')}")
    print(f"  log_level: {get_config_value('log_level')}")
    print(f"  port: {get_config_value('port')}")


if __name__ == '__main__':
    main()
