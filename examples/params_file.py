"""
@file Syntax Example

This example demonstrates the @file syntax for loading parameter values from
files. All parameter types (except toggles) support @file:

- Text params: Load entire file content as a string
- Number params: Load numeric value from file
- List params: Split file content on whitespace (respecting quoted strings)
- Dict params: Load JSON object from file

This is useful for:
- Large or complex values unwieldy on the command line
- Reusing values across multiple runs
- Version controlling parameter values
- Separating data from command invocation

Run this example:
    python examples/params_file.py read-query --sql @examples/sample_query.sql
    python examples/params_file.py process-count --count @examples/sample_count.txt
    python examples/params_file.py process-files --files @examples/sample_files.txt
    python examples/params_file.py send-payload --payload @examples/sample_payload.json
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def read_query():
    """Display SQL query loaded from file."""
    sql = spafw37.get_config_value('sql')
    
    spafw37.output("SQL Query loaded from file:")
    spafw37.output("-" * 50)
    spafw37.output(sql)
    spafw37.output("-" * 50)
    spafw37.output(f"Query length: {len(sql)} characters")


def process_count():
    """Process using count loaded from file."""
    count = spafw37.get_config_value('count')
    
    spafw37.output(f"Count loaded from file: {count}")
    spafw37.output(f"Type: {type(count)}")
    spafw37.output(f"\nProcessing {count} items...")
    
    for item_index in range(1, count + 1):
        spafw37.output(f"  Item {item_index} processed")


def process_files():
    """Process files loaded from list in file."""
    files = spafw37.get_config_value('files')
    
    spafw37.output(f"Files loaded from file: {len(files)} total")
    spafw37.output("\nFile list:")
    
    for file_index, filename in enumerate(files, 1):
        spafw37.output(f"  {file_index}. {filename}")
    
    spafw37.output(f"\nNote: Quoted filenames with spaces are preserved as single items")


def send_payload():
    """Send API payload loaded from JSON file."""
    payload = spafw37.get_config_dict('payload')
    
    spafw37.output("API Payload loaded from JSON file:")
    
    import json
    formatted = json.dumps(payload, indent=2)
    spafw37.output(formatted)
    
    spafw37.output(f"\nPayload has {len(payload)} top-level keys")
    
    # Simulate sending
    if 'user' in payload:
        spafw37.output(f"Sending request for user: {payload['user']}")
    if 'action' in payload:
        spafw37.output(f"Action: {payload['action']}")
    
    spafw37.output("\n✓ Payload sent (simulated)")


# Define parameters that support @file syntax
params = [
    {
        PARAM_NAME: 'sql',
        PARAM_DESCRIPTION: 'SQL query (use @file.sql to load from file)',
        PARAM_ALIASES: ['--sql'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
    {
        PARAM_NAME: 'count',
        PARAM_DESCRIPTION: 'Item count (use @file.txt to load from file)',
        PARAM_ALIASES: ['--count'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
    },
    {
        PARAM_NAME: 'files',
        PARAM_DESCRIPTION: 'File list (use @file.txt to load from file, whitespace-separated)',
        PARAM_ALIASES: ['--files'],
        PARAM_TYPE: PARAM_TYPE_LIST,
    },
    {
        PARAM_NAME: 'payload',
        PARAM_DESCRIPTION: 'API payload object (use @file.json to load from file)',
        PARAM_ALIASES: ['--payload'],
        PARAM_TYPE: PARAM_TYPE_DICT,
    },
]

# Define commands
commands = [
    {
        COMMAND_NAME: 'read-query',
        COMMAND_DESCRIPTION: 'Read and display SQL query from file',
        COMMAND_ACTION: read_query,
    },
    {
        COMMAND_NAME: 'process-count',
        COMMAND_DESCRIPTION: 'Process items using count from file',
        COMMAND_ACTION: process_count,
    },
    {
        COMMAND_NAME: 'process-files',
        COMMAND_DESCRIPTION: 'Process file list loaded from file',
        COMMAND_ACTION: process_files,
    },
    {
        COMMAND_NAME: 'send-payload',
        COMMAND_DESCRIPTION: 'Send API payload loaded from JSON file',
        COMMAND_ACTION: send_payload,
    },
]

if __name__ == '__main__':
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    spafw37.run_cli()
