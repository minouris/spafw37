#!/usr/bin/env python3
"""Demonstration script for spafw37 logging functionality.

Run this script from the project root directory:
    python3 demo_logging.py
"""
from __future__ import annotations

from spafw37 import logging, param, command, config_func as config
import spafw37.config
from spafw37.logging import LOGGING_PARAMS
from spafw37.constants.command import (
    COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE,
)
from spafw37.constants.phase import (
    PHASE_SETUP, PHASE_EXECUTION, PHASE_CLEANUP,
)

def setup_command():
    """Setup command action."""
    logging.log_info(_message="Running setup tasks...")
    logging.log_debug(_message="Setup details: initializing resources")

def execute_command():
    """Execute command action."""
    logging.log_info(_message="Running main execution...")
    logging.log_debug(_message="Processing data...")
    logging.log_trace(_message="Detailed trace information")

def cleanup_command():
    """Cleanup command action."""
    logging.log_info(_message="Running cleanup tasks...")
    logging.log_debug(_message="Cleanup details: releasing resources")

def main():
    """Main demonstration function."""
    print("=== spafw37 Logging Demonstration ===\n")
    
    # Set up logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set up commands
    command.set_phases_order([PHASE_SETUP, PHASE_EXECUTION, PHASE_CLEANUP])
    
    commands = [
        {
            COMMAND_NAME: 'setup',
            COMMAND_ACTION: setup_command,
            COMMAND_PHASE: PHASE_SETUP,
        },
        {
            COMMAND_NAME: 'execute',
            COMMAND_ACTION: execute_command,
            COMMAND_PHASE: PHASE_EXECUTION,
        },
        {
            COMMAND_NAME: 'cleanup',
            COMMAND_ACTION: cleanup_command,
            COMMAND_PHASE: PHASE_CLEANUP,
        },
    ]
    
    command.add_commands(commands)
    
    # Parse demonstration arguments (verbose mode)
    verbose_param = param.get_param_by_name('log-verbose')
    config.set_config_value(verbose_param, True)
    
    # Apply logging configuration
    logging.apply_logging_config()
    config.set_app_name("demo-app")
    
    # Get actual log directory from config
    log_dir = spafw37.config.get_config_value('log-dir') or 'logs/'
    
    print("Logging configuration applied:")
    print(f"  - Log directory: {log_dir}")
    print(f"  - Console level: DEBUG (verbose mode)")
    print(f"  - File level: DEBUG")
    print("\nExecuting commands...\n")
    
    # Queue and run commands
    command.queue_command('setup')
    command.queue_command('execute')
    command.queue_command('cleanup')
    
    command.run_command_queue()
    
    print("\n=== Demonstration Complete ===")
    print("\nCheck the logs/ directory for detailed log files.")
    print("Log file format: log-{yyyy-MM-dd-hh.mm.ss}.log")

if __name__ == '__main__':
    main()
