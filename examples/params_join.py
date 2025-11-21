"""Join Parameter Example - Accumulating parameter values.

This example demonstrates join_param() for accumulating values with type-specific behavior:
- Strings: Concatenate with configurable separator
- Lists: Append or extend
- Dicts: Merge with configurable strategy

Run this example:
    python examples/params_join.py demo-string
    python examples/params_join.py demo-list
    python examples/params_join.py demo-dict
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
    PARAM_JOIN_SEPARATOR,
    PARAM_DICT_MERGE_TYPE,
    PARAM_DICT_OVERRIDE_STRATEGY,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_PIPE_PADDED,
    DICT_MERGE_SHALLOW,
    DICT_MERGE_DEEP,
    DICT_OVERRIDE_RECENT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def demo_string_join():
    """Demonstrate string concatenation with join_param()."""
    spafw37.output("String Join Demo - Building a message with custom separator")
    spafw37.output()
    
    # Join strings with default space separator
    spafw37.set_param(param_name='message', value='')  # Start fresh
    spafw37.join_param(param_name='message', value='Hello')
    spafw37.join_param(param_name='message', value='World')
    spafw37.join_param(param_name='message', value='from')
    spafw37.join_param(param_name='message', value='spafw37')
    
    message = spafw37.get_param('message')
    spafw37.output(f"Default separator (space): '{message}'")
    spafw37.output()
    
    # Join tags with comma-space separator
    spafw37.set_param(param_name='tags', value='')  # Start fresh
    spafw37.join_param(param_name='tags', value='python')
    spafw37.join_param(param_name='tags', value='cli')
    spafw37.join_param(param_name='tags', value='framework')
    
    tags = spafw37.get_param('tags')
    spafw37.output(f"Comma-space separator: '{tags}'")
    spafw37.output()
    
    # Join path components with pipe separator
    spafw37.set_param(param_name='path', value='')  # Start fresh
    spafw37.join_param(param_name='path', value='home')
    spafw37.join_param(param_name='path', value='user')
    spafw37.join_param(param_name='path', value='documents')
    
    path = spafw37.get_param('path')
    spafw37.output(f"Pipe-padded separator: '{path}'")


def demo_list_join():
    """Demonstrate list accumulation with join_param()."""
    spafw37.output("List Join Demo - Building lists by appending values")
    spafw37.output()
    
    # Start with empty list
    spafw37.set_param(param_name='items', value=[])
    
    # Append single values
    spafw37.join_param(param_name='items', value='item1')
    spafw37.join_param(param_name='items', value='item2')
    spafw37.join_param(param_name='items', value='item3')
    
    items = spafw37.get_param('items')
    spafw37.output(f"After appending singles: {items}")
    spafw37.output()
    
    # Extend with a list
    spafw37.join_param(param_name='items', value=['item4', 'item5', 'item6'])
    
    items = spafw37.get_param('items')
    spafw37.output(f"After extending with list: {items}")
    spafw37.output()
    
    spafw37.output(f"Total items: {len(items)}")


def demo_dict_join():
    """Demonstrate dictionary merging with join_param()."""
    spafw37.output("Dict Join Demo - Merging dictionaries with different strategies")
    spafw37.output()
    
    # Shallow merge (default) - top-level keys only
    spafw37.output("1. Shallow Merge (top-level keys):")
    spafw37.set_param(param_name='config', value={})
    spafw37.join_param(param_name='config', value={'database': 'postgres', 'port': 5432})
    spafw37.join_param(param_name='config', value={'database': 'mysql', 'host': 'localhost'})
    
    config = spafw37.get_param('config')
    import json
    spafw37.output(f"   Result: {json.dumps(config, indent=6)}")
    spafw37.output(f"   Note: 'database' was overwritten (recent wins)")
    spafw37.output()
    
    # Deep merge - recursively merge nested dicts
    spafw37.output("2. Deep Merge (recursive):")
    spafw37.set_param(param_name='settings', value={})
    spafw37.join_param(param_name='settings', value={
        'api': {'timeout': 30, 'retries': 3},
        'cache': {'enabled': True}
    })
    spafw37.join_param(param_name='settings', value={
        'api': {'timeout': 60, 'max_connections': 100},
        'logging': {'level': 'INFO'}
    })
    
    settings = spafw37.get_param('settings')
    spafw37.output(f"   Result: {json.dumps(settings, indent=6)}")
    spafw37.output(f"   Note: Nested 'api' dict merged (timeout updated, retries kept)")
    spafw37.output()
    
    # Show the difference
    spafw37.output("Key Difference:")
    spafw37.output("   - Shallow: Replaces entire nested dict")
    spafw37.output("   - Deep: Merges keys within nested dict")


# Define parameters
params = [
    # String with default space separator
    {
        PARAM_NAME: 'message',
        PARAM_DESCRIPTION: 'Message built with space separator',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        # Default PARAM_JOIN_SEPARATOR is space
    },
    # String with comma-space separator
    {
        PARAM_NAME: 'tags',
        PARAM_DESCRIPTION: 'Tags joined with comma-space',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_JOIN_SEPARATOR: SEPARATOR_COMMA_SPACE,
    },
    # String with pipe separator
    {
        PARAM_NAME: 'path',
        PARAM_DESCRIPTION: 'Path components with pipe separator',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_JOIN_SEPARATOR: SEPARATOR_PIPE_PADDED,
    },
    # List parameter
    {
        PARAM_NAME: 'items',
        PARAM_DESCRIPTION: 'List of items',
        PARAM_TYPE: PARAM_TYPE_LIST,
    },
    # Dict with shallow merge (default)
    {
        PARAM_NAME: 'config',
        PARAM_DESCRIPTION: 'Configuration with shallow merge',
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_DICT_MERGE_TYPE: DICT_MERGE_SHALLOW,
        PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_RECENT,
    },
    # Dict with deep merge
    {
        PARAM_NAME: 'settings',
        PARAM_DESCRIPTION: 'Settings with deep merge',
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP,
        PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_RECENT,
    },
]

# Define commands
commands = [
    {
        COMMAND_NAME: 'demo-string',
        COMMAND_DESCRIPTION: 'Demonstrate string concatenation with custom separators',
        COMMAND_ACTION: demo_string_join,
    },
    {
        COMMAND_NAME: 'demo-list',
        COMMAND_DESCRIPTION: 'Demonstrate list accumulation',
        COMMAND_ACTION: demo_list_join,
    },
    {
        COMMAND_NAME: 'demo-dict',
        COMMAND_DESCRIPTION: 'Demonstrate dictionary merging (shallow vs deep)',
        COMMAND_ACTION: demo_dict_join,
    },
]

if __name__ == '__main__':
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    spafw37.run_cli()
