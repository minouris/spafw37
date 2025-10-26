"""Simple example of buffered parameter registration with run-levels.

This demonstrates how run-levels sandbox parts of configuration to run
in isolation with defined sets of params, commands, and preset config values.

Pre-defined run-levels are:
- init: sets up logging, determines output verbosity/silent, log levels, etc
- config: loads/saves configuration in external files
- exec: executes the bulk of application commands (DEFAULT)
- cleanup: does any cleanup tasks
"""

from spafw37.param import add_param
from spafw37.cli import handle_cli_args
from spafw37.config import get_config_value
from spafw37.config_consts import (
    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE,
    PARAM_RUN_LEVEL
)


def main():
    """Example application entry point."""
    
    # Register parameters as dictionaries (structs)
    # These params will be auto-assigned to the 'exec' run-level (default)
    add_param({
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose', '-v'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False
    })
    
    # This param is explicitly assigned to 'init' run-level
    add_param({
        PARAM_NAME: 'log_level',
        PARAM_ALIASES: ['--log-level', '-l'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'info',
        PARAM_RUN_LEVEL: 'init'  # Explicitly assigned to init
    })
    
    add_param({
        PARAM_NAME: 'port',
        PARAM_ALIASES: ['--port', '-p'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 8000
    })
    
    # Parse command-line arguments
    # Run-levels execute automatically in registration order:
    # init → config → exec (default) → cleanup
    # Each param/command belongs to exactly ONE run-level
    # CLI arguments override run-level config values
    import sys
    handle_cli_args(sys.argv[1:])
    
    # Get configuration values
    # Config values are cumulative across all run-levels
    print("Configuration after run-level processing:")
    print(f"  verbose: {get_config_value('verbose')}")
    print(f"  log_level: {get_config_value('log_level')}")
    print(f"  port: {get_config_value('port')}")


if __name__ == '__main__':
    main()
