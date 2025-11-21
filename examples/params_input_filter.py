"""Input Filter Example - Custom parameter input processing.

This example demonstrates PARAM_INPUT_FILTER for custom transformation
of CLI string values before validation. Input filters are useful for:
- Custom delimiters (CSV, pipes, etc.)
- Domain-specific syntax (connection strings, DSL)
- Input sanitization or normalization
- Format conversion

Run this example:
    python examples/params_input_filter.py parse-csv --tags "python, cli, framework"
    python examples/params_input_filter.py connect --db "host=localhost;port=5432;database=myapp"
    python examples/params_input_filter.py parse-kv --settings "debug=true timeout=30 retries=3"
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
    PARAM_INPUT_FILTER,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def csv_to_list_filter(value):
    """Convert comma-separated values to list.
    
    Input filter for list parameters that allows CSV input.
    """
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(',')]


def connection_string_filter(value):
    """Parse database connection string into dict.
    
    Supports format: "key1=value1;key2=value2;..."
    """
    if isinstance(value, dict):
        return value
    
    result = {}
    parts = value.split(';')
    for part in parts:
        if '=' in part:
            key, val = part.split('=', 1)
            result[key.strip()] = val.strip()
    return result


def key_value_pairs_filter(value):
    """Parse space-separated key=value pairs into dict.
    
    Supports format: "key1=value1 key2=value2 ..."
    """
    if isinstance(value, dict):
        return value
    
    result = {}
    parts = value.split()
    for part in parts:
        if '=' in part:
            key, val = part.split('=', 1)
            result[key.strip()] = val.strip()
    return result


def demo_csv_parsing():
    """Demonstrate CSV parsing with custom input filter."""
    tags = spafw37.get_param('tags')
    
    spafw37.output("CSV Input Filter Demo")
    spafw37.output()
    spafw37.output(f"Input: \"python, cli, framework\"")
    spafw37.output(f"Parsed as list: {tags}")
    spafw37.output(f"Type: {type(tags)}")
    spafw37.output()
    spafw37.output("Benefits:")
    spafw37.output("  - User-friendly CSV input instead of multiple --tags flags")
    spafw37.output("  - Automatic whitespace trimming")
    spafw37.output("  - Still validates as list type")


def demo_connection_string():
    """Demonstrate connection string parsing."""
    db_config = spafw37.get_param('db')
    
    spafw37.output("Connection String Filter Demo")
    spafw37.output()
    spafw37.output("Input: \"host=localhost;port=5432;database=myapp\"")
    spafw37.output()
    spafw37.output("Parsed configuration:")
    
    import json
    formatted = json.dumps(db_config, indent=2)
    spafw37.output(formatted)
    spafw37.output()
    
    # Use the parsed configuration
    host = db_config.get('host', 'unknown')
    port = db_config.get('port', 'unknown')
    database = db_config.get('database', 'unknown')
    
    spafw37.output(f"Connecting to: {database} at {host}:{port}")
    spafw37.output()
    spafw37.output("Benefits:")
    spafw37.output("  - Familiar connection string format")
    spafw37.output("  - Parsed into dict for easy access")
    spafw37.output("  - Type-safe (validates as dict)")


def demo_key_value_pairs():
    """Demonstrate key=value pair parsing."""
    settings = spafw37.get_param('settings')
    
    spafw37.output("Key=Value Pairs Filter Demo")
    spafw37.output()
    spafw37.output("Input: \"debug=true timeout=30 retries=3\"")
    spafw37.output()
    spafw37.output("Parsed settings:")
    
    import json
    formatted = json.dumps(settings, indent=2)
    spafw37.output(formatted)
    spafw37.output()
    
    # Access individual settings
    for key, value in settings.items():
        spafw37.output(f"  {key}: {value}")
    
    spafw37.output()
    spafw37.output("Benefits:")
    spafw37.output("  - Compact command-line syntax")
    spafw37.output("  - No need for JSON quotes")
    spafw37.output("  - Easy to type and remember")


# Define parameters with custom input filters
params = [
    {
        PARAM_NAME: 'tags',
        PARAM_DESCRIPTION: 'Comma-separated list of tags',
        PARAM_ALIASES: ['--tags'],
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_INPUT_FILTER: csv_to_list_filter,
    },
    {
        PARAM_NAME: 'db',
        PARAM_DESCRIPTION: 'Database connection string (key=value;...)',
        PARAM_ALIASES: ['--db'],
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_INPUT_FILTER: connection_string_filter,
    },
    {
        PARAM_NAME: 'settings',
        PARAM_DESCRIPTION: 'Application settings (key=value ...)',
        PARAM_ALIASES: ['--settings'],
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_INPUT_FILTER: key_value_pairs_filter,
    },
]

# Define commands
commands = [
    {
        COMMAND_NAME: 'parse-csv',
        COMMAND_DESCRIPTION: 'Demonstrate CSV to list parsing',
        COMMAND_ACTION: demo_csv_parsing,
    },
    {
        COMMAND_NAME: 'connect',
        COMMAND_DESCRIPTION: 'Demonstrate connection string parsing',
        COMMAND_ACTION: demo_connection_string,
    },
    {
        COMMAND_NAME: 'parse-kv',
        COMMAND_DESCRIPTION: 'Demonstrate key=value pairs parsing',
        COMMAND_ACTION: demo_key_value_pairs,
    },
]

if __name__ == '__main__':
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    spafw37.run_cli()
