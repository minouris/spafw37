"""Example demonstrating buffered parameter registration and run-level parsing.

This example shows how to use the new buffered registration API to define
parameters and run-levels, then parse command-line arguments with run-level
merging.
"""

from spafw37.param import register_param, register_run_level
from spafw37.cli import build_parser, parse_args, get_effective_config


def setup_parameters():
    """Register parameters using buffered registration API."""
    
    register_param(
        name='host',
        aliases=['--host', '-h'],
        type='text',
        default='localhost',
        description='Server host address'
    )
    
    register_param(
        name='port',
        aliases=['--port', '-p'],
        type='number',
        default=8000,
        description='Server port number'
    )
    
    register_param(
        name='debug',
        aliases=['--debug', '-d'],
        type='toggle',
        default=False,
        description='Enable debug mode'
    )
    
    register_param(
        name='log_level',
        aliases=['--log-level', '-l'],
        type='text',
        default='info',
        description='Logging level'
    )
    
    register_param(
        name='workers',
        aliases=['--workers', '-w'],
        type='number',
        default=4,
        description='Number of worker processes'
    )


def setup_run_levels():
    """Define run-levels with different default configurations."""
    
    register_run_level('dev', {
        'host': 'dev.local',
        'port': 3000,
        'debug': True,
        'log_level': 'debug',
        'workers': 1
    })
    
    register_run_level('staging', {
        'host': 'staging.example.com',
        'port': 8080,
        'debug': False,
        'log_level': 'info',
        'workers': 2
    })
    
    register_run_level('prod', {
        'host': 'prod.example.com',
        'port': 443,
        'debug': False,
        'log_level': 'error',
        'workers': 8
    })


def print_config(config_dict, label):
    """Pretty print configuration."""
    print(f"\n{label}:")
    print("=" * 50)
    for key, value in sorted(config_dict.items()):
        print(f"  {key:15s} = {value}")
    print()


def demo_scenario(scenario_name, args):
    """Run a demonstration scenario."""
    print(f"\n{'*' * 60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"Command: {' '.join(args) if args else '(no arguments)'}")
    print('*' * 60)
    
    effective = get_effective_config(args)
    print_config(effective, "Effective Configuration")


if __name__ == '__main__':
    print("=" * 60)
    print("Buffered Registration and Run-Level Demo")
    print("=" * 60)
    
    setup_parameters()
    setup_run_levels()
    
    count = build_parser()
    print(f"\nRegistered {count} parameters from buffer")
    
    print("\n" + "=" * 60)
    print("Available Run-Levels:")
    print("=" * 60)
    print("  - dev:     Development configuration")
    print("  - staging: Staging/test configuration")
    print("  - prod:    Production configuration")
    
    demo_scenario(
        "Default Configuration (no run-levels)",
        []
    )
    
    demo_scenario(
        "Development Run-Level",
        ['-R', 'dev']
    )
    
    demo_scenario(
        "Production Run-Level",
        ['-R', 'prod']
    )
    
    demo_scenario(
        "Multiple Run-Levels (dev then prod)",
        ['-R', 'dev,prod']
    )
    
    demo_scenario(
        "Run-Level with CLI Override",
        ['-R', 'prod', '--port', '9000', '--debug']
    )
    
    demo_scenario(
        "Multiple Run-Levels with CLI Overrides",
        ['-R', 'dev', '-R', 'staging', '--host', 'custom.host', '--workers', '16']
    )
    
    print("\n" + "=" * 60)
    print("Demonstration Complete")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  1. Parameters can be registered before parser construction")
    print("  2. Run-levels provide named configuration sets")
    print("  3. Later run-levels override earlier ones")
    print("  4. CLI arguments always have highest precedence")
    print("  5. Both -R and --run-levels work for specifying run-levels")
    print("  6. Comma-separated and multiple flags are both supported")
    print()
