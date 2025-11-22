"""
Example demonstrating parameter unset and reset functionality.

This example showcases parameter lifecycle management:
- unset_param() - Remove parameter values completely
- reset_param() - Reset to default value or unset if no default

Also demonstrates how immutable parameters interact with unset and reset.
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT,
    PARAM_IMMUTABLE,
    PARAM_DESCRIPTION,
)

# Configure application
spafw37.set_app_name('Param Lifecycle Demo')
spafw37.set_output_handler(print)


def demo_basic_unset():
    """Demonstrate basic unset functionality."""
    print("\n=== Basic Unset Demo ===\n")
    
    # Define a temporary parameter
    temp_param = {
        PARAM_NAME: 'temp-data',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DESCRIPTION: 'Temporary data for processing',
    }
    spafw37.add_param(temp_param)
    
    # Set a value
    spafw37.set_param(param_name='temp-data', value='temporary value')
    print(f"After set: temp-data = {spafw37.get_param('temp-data')}")
    
    # Unset removes the value completely
    spafw37.unset_param(param_name='temp-data')
    print(f"After unset: temp-data = {spafw37.get_param('temp-data', default='<not set>')}")


def demo_basic_reset():
    """Demonstrate basic reset functionality."""
    print("\n=== Basic Reset Demo ===\n")
    
    # Parameter with default value
    counter_param = {
        PARAM_NAME: 'counter',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 0,
        PARAM_DESCRIPTION: 'Counter with default value',
    }
    spafw37.add_param(counter_param)
    
    # Modify the value
    spafw37.set_param(param_name='counter', value=42)
    print(f"After modification: counter = {spafw37.get_param('counter')}")
    
    # Reset restores default value
    spafw37.reset_param(param_name='counter')
    print(f"After reset: counter = {spafw37.get_param('counter')}")


def demo_reset_without_default():
    """Demonstrate reset behavior when no default exists."""
    print("\n=== Reset Without Default Demo ===\n")
    
    # Parameter without default value
    runtime_state = {
        PARAM_NAME: 'runtime-state',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DESCRIPTION: 'Runtime state without default',
    }
    spafw37.add_param(runtime_state)
    
    # Set a value
    spafw37.set_param(param_name='runtime-state', value='processing')
    print(f"After set: runtime-state = {spafw37.get_param('runtime-state')}")
    
    # Reset without default unsets the parameter
    spafw37.reset_param(param_name='runtime-state')
    print(f"After reset: runtime-state = {spafw37.get_param('runtime-state', default='<not set>')}")
    print("(Reset without default behaves like unset)")


def demo_immutable_protection():
    """Demonstrate that immutable parameters block unset and reset."""
    print("\n=== Immutability Protection ===\n")
    
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
    print(f"Initial value: app-version = {spafw37.get_param('app-version')}")
    
    # Unset blocked
    print("\nAttempting unset_param():")
    try:
        spafw37.unset_param(param_name='app-version')
        print("  ✗ ERROR: Unset should have been blocked!")
    except ValueError as error:
        print(f"  ✓ Blocked: {error}")
    
    # Reset blocked
    print("\nAttempting reset_param():")
    try:
        spafw37.reset_param(param_name='app-version')
        print("  ✗ ERROR: Reset should have been blocked!")
    except ValueError as error:
        print(f"  ✓ Blocked: {error}")
    
    print("\nImmutable parameters cannot be unset or reset once set.")
    print("See params_immutable.py for full immutability documentation.")


def demo_runtime_cleanup_pattern():
    """Demonstrate using unset for runtime state cleanup."""
    print("\n=== Runtime State Cleanup Pattern ===\n")
    
    # Define runtime state parameters
    processing_params = [
        {
            PARAM_NAME: 'current-file',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_DESCRIPTION: 'Currently processing file',
        },
        {
            PARAM_NAME: 'progress',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_DESCRIPTION: 'Processing progress',
        },
        {
            PARAM_NAME: 'processing-active',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_DESCRIPTION: 'Processing active flag',
        },
    ]
    spafw37.add_params(processing_params)
    
    # Simulate processing
    print("Starting processing...")
    spafw37.set_param(param_name='current-file', value='data.txt')
    spafw37.set_param(param_name='progress', value=0)
    spafw37.set_param(param_name='processing-active', value=True)
    
    print(f"  current-file: {spafw37.get_param('current-file')}")
    print(f"  progress: {spafw37.get_param('progress')}")
    print(f"  processing-active: {spafw37.get_param('processing-active')}")
    
    # Clean up after processing
    print("\nCleaning up runtime state...")
    spafw37.unset_param(param_name='current-file')
    spafw37.unset_param(param_name='progress')
    spafw37.reset_param(param_name='processing-active')  # Reset to default (False)
    
    print(f"  current-file: {spafw37.get_param('current-file', default='<not set>')}")
    print(f"  progress: {spafw37.get_param('progress', default='<not set>')}")
    print(f"  processing-active: {spafw37.get_param('processing-active')}")


def demo_unset_vs_reset_comparison():
    """Compare unset and reset behaviors side-by-side."""
    print("\n=== Unset vs Reset Comparison ===\n")
    
    # Two similar parameters - one with default, one without
    params = [
        {
            PARAM_NAME: 'setting-with-default',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_DEFAULT: 'default-value',
            PARAM_DESCRIPTION: 'Setting with default',
        },
        {
            PARAM_NAME: 'setting-without-default',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_DESCRIPTION: 'Setting without default',
        },
    ]
    spafw37.add_params(params)
    
    # Set both to modified values
    spafw37.set_param(param_name='setting-with-default', value='modified')
    spafw37.set_param(param_name='setting-without-default', value='modified')
    
    print("Initial state:")
    print(f"  with-default: {spafw37.get_param('setting-with-default')}")
    print(f"  without-default: {spafw37.get_param('setting-without-default')}")
    
    # Reset both
    print("\nAfter reset_param():")
    spafw37.reset_param(param_name='setting-with-default')
    spafw37.reset_param(param_name='setting-without-default')
    print(f"  with-default: {spafw37.get_param('setting-with-default')}")
    print(f"  without-default: {spafw37.get_param('setting-without-default', default='<not set>')}")
    print("  → reset() restores default or unsets if no default")
    
    # Set again and unset
    spafw37.set_param(param_name='setting-with-default', value='modified-again')
    spafw37.set_param(param_name='setting-without-default', value='modified-again')
    
    print("\nAfter unset_param():")
    spafw37.unset_param(param_name='setting-with-default')
    spafw37.unset_param(param_name='setting-without-default')
    print(f"  with-default: {spafw37.get_param('setting-with-default', default='<not set>')}")
    print(f"  without-default: {spafw37.get_param('setting-without-default', default='<not set>')}")
    print("  → unset() removes value regardless of default")


if __name__ == '__main__':
    print("=" * 60)
    print("Parameter Unset and Reset Demo")
    print("Managing parameter lifecycle with unset_param() and reset_param()")
    print("=" * 60)
    
    # Basic operations
    demo_basic_unset()
    demo_basic_reset()
    demo_reset_without_default()
    
    # Immutability interaction
    demo_immutable_protection()
    
    # Practical patterns
    demo_runtime_cleanup_pattern()
    demo_unset_vs_reset_comparison()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
