"""Cycle Loop Start Example - Preparing each iteration.

This example shows:
- CYCLE_LOOP_START - runs at the start of each iteration
- Setting up iteration-specific state
- Processing collections with cycles
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_CYCLE,
)
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_LIST,
    PARAM_RUNTIME_ONLY,
)

# Runtime parameters
params = [
    {
        PARAM_NAME: 'items',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'index',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'current-item',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True,
    },
]

# Cycle control functions

def init_items():
    """Initialise the items list."""
    items = ['apple', 'banana', 'cherry', 'date', 'elderberry']
    spafw37.set_param(param_name='items', value=items)
    spafw37.set_param(param_name='index', value=0)
    spafw37.output(f"Processing {len(items)} items")
    spafw37.output("=" * 40)

def has_more_items():
    """Check if more items remain."""
    items = spafw37.get_param('items')
    index = spafw37.get_param('index')
    return index < len(items)

def prepare_item():
    """Prepare the current item for this iteration."""
    items = spafw37.get_param('items')
    index = spafw37.get_param('index')
    
    current_item = items[index]
    spafw37.set_param(param_name='current-item', value=current_item)
    
    spafw37.output(f"\n[Item {index + 1}/{len(items)}] {current_item}")

def finalize_items():
    """Finalise the items."""
    index = spafw37.get_param('index')
    spafw37.output()
    spafw37.output("=" * 40)
    spafw37.output(f"Processed {index} items")

# Cycle command actions

def validate_item():
    """Validate the current item."""
    item = spafw37.get_param('current-item')
    spafw37.output(f"  ✓ Validating {item}")

def transform_item():
    """Transform the current item."""
    item = spafw37.get_param('current-item')
    spafw37.output(f"  ✓ Transforming {item} -> {item.upper()}")

def save_item():
    """Save the current item."""
    item = spafw37.get_param('current-item')
    spafw37.output(f"  ✓ Saving {item}")
    
    # Increment index for next iteration
    index = spafw37.get_param('index')
    spafw37.set_param(param_name='index', value=index + 1)

# Define cycle commands
cycle_commands = [
    {
        COMMAND_NAME: 'validate-item',
        COMMAND_DESCRIPTION: 'Validate item',
        COMMAND_ACTION: validate_item,
    },
    {
        COMMAND_NAME: 'transform-item',
        COMMAND_DESCRIPTION: 'Transform item',
        COMMAND_ACTION: transform_item,
    },
    {
        COMMAND_NAME: 'save-item',
        COMMAND_DESCRIPTION: 'Save item',
        COMMAND_ACTION: save_item,
    },
]

# Define main command with cycle
commands = [
    {
        COMMAND_NAME: 'process-items',
        COMMAND_DESCRIPTION: 'Process all items',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: {
            CYCLE_NAME: 'items-cycle',
            CYCLE_INIT: init_items,
            CYCLE_LOOP: has_more_items,
            CYCLE_LOOP_START: prepare_item,
            CYCLE_END: finalize_items,
            CYCLE_COMMANDS: cycle_commands,
        }
    }
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('cycles-loop-start-demo')

if __name__ == '__main__':
    spafw37.run_cli()
