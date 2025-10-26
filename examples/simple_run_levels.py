"""Simple example of buffered registration and run-levels.

This demonstrates the basic usage pattern for the new buffered registration API.
"""

from spafw37 import register_param, register_run_level, build_parser, get_effective_config


def main():
    """Example application entry point."""
    
    register_param(
        name='timeout',
        aliases=['--timeout', '-t'],
        type='number',
        default=30,
        description='Request timeout in seconds'
    )
    
    register_param(
        name='log-level',
        aliases=['--log-level', '-l'],
        type='text',
        default='info',
        description='Logging level'
    )
    
    register_run_level('dev', {
        'timeout': 10,
        'log-level': 'debug'
    })
    
    register_run_level('prod', {
        'timeout': 60,
        'log-level': 'error'
    })
    
    build_parser()
    
    import sys
    effective = get_effective_config(sys.argv[1:])
    
    print("Configuration:")
    for key, value in sorted(effective.items()):
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
