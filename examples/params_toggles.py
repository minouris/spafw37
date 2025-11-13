"""Toggle Parameters Example - Boolean flags and switch lists.

This example shows:
- Toggle parameters (boolean flags)
- Switch lists (mutually exclusive parameters)
- Using toggles to control application behavior
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_TOGGLE,
    PARAM_SWITCH_LIST,
    PARAM_DEFAULT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Define parameters with toggles and switch lists
params = [
    {
        PARAM_NAME: 'input-file',
        PARAM_DESCRIPTION: 'Input file path',
        PARAM_ALIASES: ['--input', '-i'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
    # Toggle parameters - mutually exclusive output formats
    {
        PARAM_NAME: 'json-output',
        PARAM_DESCRIPTION: 'Output results in JSON format',
        PARAM_ALIASES: ['--json', '-j'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['csv-output', 'xml-output'],
    },
    {
        PARAM_NAME: 'csv-output',
        PARAM_DESCRIPTION: 'Output results in CSV format',
        PARAM_ALIASES: ['--csv', '-c'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['json-output', 'xml-output'],
    },
    {
        PARAM_NAME: 'xml-output',
        PARAM_DESCRIPTION: 'Output results in XML format',
        PARAM_ALIASES: ['--xml', '-x'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['json-output', 'csv-output'],
    },
]

def process_command():
    """Process with toggle parameters."""
    input_file = spafw37.get_config_str('input-file')
    
    # Check which output format is selected
    json_output = spafw37.get_config_bool('json-output')
    csv_output = spafw37.get_config_bool('csv-output')
    xml_output = spafw37.get_config_bool('xml-output')
    
    # Determine format
    if json_output:
        format_name = 'JSON'
    elif csv_output:
        format_name = 'CSV'
    elif xml_output:
        format_name = 'XML'
    else:
        format_name = 'TEXT (default)'
    
    spafw37.output(f"Processing: {input_file}")
    spafw37.output(f"Output format: {format_name}")
    spafw37.output()
    
    # Generate sample data
    data = [
        {'id': 1, 'name': 'Item A', 'value': 100},
        {'id': 2, 'name': 'Item B', 'value': 200},
        {'id': 3, 'name': 'Item C', 'value': 300},
    ]
    
    # Output in selected format
    if json_output:
        import json
        spafw37.output(json.dumps(data, indent=2))
    elif csv_output:
        spafw37.output("ID,Name,Value")
        for item in data:
            spafw37.output(f"{item['id']},{item['name']},{item['value']}")
    elif xml_output:
        spafw37.output('<?xml version="1.0"?>')
        spafw37.output('<items>')
        for item in data:
            spafw37.output(f'  <item id="{item["id"]}">')
            spafw37.output(f'    <name>{item["name"]}</name>')
            spafw37.output(f'    <value>{item["value"]}</value>')
            spafw37.output('  </item>')
        spafw37.output('</items>')
    else:
        for item in data:
            spafw37.output(f"  [{item['id']}] {item['name']}: {item['value']}")

# Define command
commands = [
    {
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process with output format toggle',
        COMMAND_ACTION: process_command,
    }
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('params-toggles-demo')

if __name__ == '__main__':
    spafw37.run_cli()
