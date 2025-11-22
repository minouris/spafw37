"""
Example demonstrating immutable parameters.

Immutable parameters provide write-once, read-many semantics to protect
critical configuration values from accidental modification during runtime.
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_IMMUTABLE,
    PARAM_DEFAULT,
    PARAM_DESCRIPTION,
)

# Configure application
spafw37.set_app_name('Immutable Parameters Demo')
spafw37.set_output_handler(print)


def demo_immutable_initial_set():
    """Demonstrate initial assignment to immutable parameter."""
    print("\n=== Initial Assignment ===\n")
    
    # Define immutable parameter
    version_param = {
        PARAM_NAME: 'app-version',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_IMMUTABLE: True,
        PARAM_DEFAULT: '1.0.0',
        PARAM_DESCRIPTION: 'Application version (immutable)',
    }
    spafw37.add_param(version_param)
    
    # Initial set succeeds
    spafw37.set_param(param_name='app-version', value='1.0.0')
    print(f"✓ Initial set succeeded: app-version = {spafw37.get_param('app-version')}")
    print("\nImmutable parameters can be set once when they have no value.")


def demo_immutable_modification_blocked():
    """Demonstrate that immutable parameters cannot be modified."""
    print("\n=== Modification Protection ===\n")
    
    print(f"Current value: app-version = {spafw37.get_param('app-version')}")
    
    try:
        spafw37.set_param(param_name='app-version', value='2.0.0')
        print("✗ ERROR: Modification should have been blocked!")
    except ValueError as error:
        print(f"✓ Modification blocked: {error}")
    
    print("\nOnce set, immutable parameters cannot be changed.")


def demo_use_case_config_lock():
    """Demonstrate using immutability to lock configuration."""
    print("\n=== Use Case: Configuration Lock ===\n")
    
    # Define critical configuration parameters as immutable
    config_params = [
        {
            PARAM_NAME: 'database-url',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_IMMUTABLE: True,
            PARAM_DESCRIPTION: 'Database connection URL (locked at startup)',
        },
        {
            PARAM_NAME: 'api-key',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_IMMUTABLE: True,
            PARAM_DESCRIPTION: 'API authentication key (locked at startup)',
        },
        {
            PARAM_NAME: 'max-connections',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_IMMUTABLE: True,
            PARAM_DEFAULT: 10,
            PARAM_DESCRIPTION: 'Maximum connection pool size (locked at startup)',
        },
    ]
    spafw37.add_params(config_params)
    
    # Initialize configuration (typically from environment or config file)
    print("Initializing configuration...")
    spafw37.set_param(param_name='database-url', value='postgres://localhost/mydb')
    spafw37.set_param(param_name='api-key', value='secret-key-12345')
    spafw37.set_param(param_name='max-connections', value=20)
    
    print(f"  database-url: {spafw37.get_param('database-url')}")
    print(f"  api-key: {spafw37.get_param('api-key')}")
    print(f"  max-connections: {spafw37.get_param('max-connections')}")
    
    # These values are now locked for the application lifetime
    print("\n✓ Configuration locked - safe from accidental modification")
    
    # Attempt to modify fails
    try:
        spafw37.set_param(param_name='database-url', value='postgres://prod/mydb')
    except ValueError:
        print("✓ Attempted modification blocked as expected")


def demo_use_case_runtime_constants():
    """Demonstrate using immutability for runtime constants."""
    print("\n=== Use Case: Runtime Constants ===\n")
    
    # Define runtime constants
    constant_params = [
        {
            PARAM_NAME: 'session-id',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_IMMUTABLE: True,
            PARAM_DESCRIPTION: 'Unique session identifier',
        },
        {
            PARAM_NAME: 'start-time',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_IMMUTABLE: True,
            PARAM_DESCRIPTION: 'Application start timestamp',
        },
    ]
    spafw37.add_params(constant_params)
    
    # Set constants at application start
    import time
    print("Setting runtime constants...")
    spafw37.set_param(param_name='session-id', value='sess-abc-123')
    spafw37.set_param(param_name='start-time', value=int(time.time()))
    
    print(f"  session-id: {spafw37.get_param('session-id')}")
    print(f"  start-time: {spafw37.get_param('start-time')}")
    
    print("\n✓ Runtime constants established - cannot be altered during execution")


def demo_mutable_vs_immutable():
    """Compare mutable and immutable parameter behavior."""
    print("\n=== Mutable vs Immutable Comparison ===\n")
    
    # Define one mutable and one immutable parameter
    params = [
        {
            PARAM_NAME: 'mutable-setting',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_IMMUTABLE: False,  # Explicit, but False is default
            PARAM_DESCRIPTION: 'A mutable setting',
        },
        {
            PARAM_NAME: 'immutable-setting',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_IMMUTABLE: True,
            PARAM_DESCRIPTION: 'An immutable setting',
        },
    ]
    spafw37.add_params(params)
    
    # Set both
    print("Initial values:")
    spafw37.set_param(param_name='mutable-setting', value='initial-mutable')
    spafw37.set_param(param_name='immutable-setting', value='initial-immutable')
    print(f"  mutable-setting: {spafw37.get_param('mutable-setting')}")
    print(f"  immutable-setting: {spafw37.get_param('immutable-setting')}")
    
    # Modify mutable - succeeds
    print("\nModifying mutable parameter:")
    spafw37.set_param(param_name='mutable-setting', value='modified-mutable')
    print(f"  ✓ mutable-setting: {spafw37.get_param('mutable-setting')}")
    
    # Attempt to modify immutable - fails
    print("\nAttempting to modify immutable parameter:")
    try:
        spafw37.set_param(param_name='immutable-setting', value='modified-immutable')
        print("  ✗ ERROR: Should have been blocked!")
    except ValueError as error:
        print(f"  ✓ Blocked: {error}")


def demo_immutable_default_false():
    """Demonstrate that PARAM_IMMUTABLE defaults to False."""
    print("\n=== Default Behavior (Mutable) ===\n")
    
    # Parameter without PARAM_IMMUTABLE specified
    default_param = {
        PARAM_NAME: 'default-behavior',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DESCRIPTION: 'Parameter without PARAM_IMMUTABLE specified',
    }
    spafw37.add_param(default_param)
    
    # Can be set and modified freely
    spafw37.set_param(param_name='default-behavior', value='first-value')
    print(f"Initial: default-behavior = {spafw37.get_param('default-behavior')}")
    
    spafw37.set_param(param_name='default-behavior', value='second-value')
    print(f"Modified: default-behavior = {spafw37.get_param('default-behavior')}")
    
    print("\n✓ By default, parameters are mutable (PARAM_IMMUTABLE defaults to False)")


if __name__ == '__main__':
    print("=" * 60)
    print("Immutable Parameters Demo")
    print("Write-once, read-many protection for critical values")
    print("=" * 60)
    
    # Basic immutability behavior
    demo_immutable_initial_set()
    demo_immutable_modification_blocked()
    
    # Practical use cases
    demo_use_case_config_lock()
    demo_use_case_runtime_constants()
    
    # Comparisons and defaults
    demo_mutable_vs_immutable()
    demo_immutable_default_false()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
