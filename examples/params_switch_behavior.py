#!/usr/bin/env python3
"""Demonstrate switch param change behaviour control.

This example shows how to control what happens to other parameters in a switch
group when one parameter is set. Three behaviours are available:

- SWITCH_REJECT (default): Raise error if another switch is already set
- SWITCH_UNSET: Automatically unset other switches in the group
- SWITCH_RESET: Reset other switches to their default values

Added in v1.1.0
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME, PARAM_TYPE, PARAM_TYPE_TOGGLE, PARAM_ALIASES, PARAM_DEFAULT,
    PARAM_SWITCH_LIST, PARAM_SWITCH_CHANGE_BEHAVIOR,
    SWITCH_UNSET, SWITCH_RESET, SWITCH_REJECT
)


def demo_switch_reject():
    """Demonstrate SWITCH_REJECT - strict validation (default behaviour)."""
    print("\n=== Example 1: SWITCH_REJECT (Strict Validation) ===")
    print("Reject conflicts - only one switch can be set at a time.\n")
    
    # Define params with SWITCH_REJECT behaviour (or omit the property - it's the default)
    spafw37.add_params([
        {
            PARAM_NAME: 'mode_read',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--read'],
            PARAM_SWITCH_LIST: ['mode_write'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'mode_write',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--write'],
            PARAM_SWITCH_LIST: ['mode_read'],
            # PARAM_SWITCH_CHANGE_BEHAVIOR omitted - defaults to SWITCH_REJECT
        },
    ])
    
    # Set first param successfully
    spafw37.set_param('mode_read', True)
    print(f"Set mode_read=True")
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
    
    # Attempt to set conflicting param - this will raise ValueError
    print("\nAttempting to set mode_write=True (will fail)...")
    try:
        spafw37.set_param('mode_write', True)
    except ValueError as e:
        print(f"  Error (as expected): {e}")


def demo_switch_unset():
    """Demonstrate SWITCH_UNSET - automatic mode switching."""
    print("\n=== Example 2: SWITCH_UNSET (Mode Switching) ===")
    print("Unset conflicts - setting one switch automatically unsets others.\n")
    
    # Define params with SWITCH_UNSET behaviour
    spafw37.add_params([
        {
            PARAM_NAME: 'mode_read',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--read'],
            PARAM_SWITCH_LIST: ['mode_write', 'mode_append'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'mode_write',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--write'],
            PARAM_SWITCH_LIST: ['mode_read', 'mode_append'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'mode_append',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--append'],
            PARAM_SWITCH_LIST: ['mode_read', 'mode_write'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    # Set read mode
    spafw37.set_param('mode_read', True)
    print(f"Set mode_read=True")
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
    print(f"  mode_append={spafw37.get_param('mode_append')}")
    
    # Switch to write mode - read should be automatically unset
    print("\nSwitching to mode_write=True...")
    spafw37.set_param('mode_write', True)
    print(f"  mode_read={spafw37.get_param('mode_read')} (automatically unset)")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
    print(f"  mode_append={spafw37.get_param('mode_append')}")
    
    # Switch to append mode - write should be automatically unset
    print("\nSwitching to mode_append=True...")
    spafw37.set_param('mode_append', True)
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')} (automatically unset)")
    print(f"  mode_append={spafw37.get_param('mode_append')}")


def demo_switch_reset():
    """Demonstrate SWITCH_RESET - restore conflicting switches to defaults."""
    print("\n=== Example 3: SWITCH_RESET (State Restoration) ===")
    print("Reset conflicts - setting one switch resets others to defaults.\n")
    
    # Define params with SWITCH_RESET behaviour and meaningful defaults
    spafw37.add_params([
        {
            PARAM_NAME: 'priority_high',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--high'],
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_low'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'priority_low',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--low'],
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_high'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    # Set high priority
    spafw37.set_param('priority_high', True)
    print(f"Set priority_high=True")
    print(f"  priority_high={spafw37.get_param('priority_high')}")
    print(f"  priority_low={spafw37.get_param('priority_low')}")
    
    # Switch to low priority - high should be reset to default (False)
    print("\nSwitching to priority_low=True...")
    spafw37.set_param('priority_low', True)
    print(f"  priority_high={spafw37.get_param('priority_high')} (reset to default)")
    print(f"  priority_low={spafw37.get_param('priority_low')}")
    
    # Switch back to high priority - low should be reset to default (False)
    print("\nSwitching back to priority_high=True...")
    spafw37.set_param('priority_high', True)
    print(f"  priority_high={spafw37.get_param('priority_high')}")
    print(f"  priority_low={spafw37.get_param('priority_low')} (reset to default)")


if __name__ == '__main__':
    demo_switch_reject()
    demo_switch_unset()
    demo_switch_reset()
    
    print("\n=== All demonstrations complete ===")
