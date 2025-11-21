"""
Dict Parameter Example

This example demonstrates dict (dictionary/object) parameters that accept
JSON-formatted data. Dict parameters are useful for:
- API request payloads
- Database query filters
- JSON schema validation
- Structured test data

Dict parameters can receive JSON in multiple ways:
1. Inline JSON string on the command line
2. Multi-token JSON (when shell splits it)
3. Loading from a file using @file syntax
4. Multiple JSON blocks (v1.1.0) - automatically merged
5. File references within JSON (v1.1.0) - e.g., {"data": @file.json}

Run this example:
    python examples/params_dict.py api-call --payload '{"user":"alice","action":"login"}'
    python examples/params_dict.py api-call --payload @examples/sample_payload.json
    python examples/params_dict.py query-db --filter '{"status":"active","age":{"$gt":18}}'
    python examples/params_dict.py validate --schema '{"type":"object","required":["id"]}'
    
    # v1.1.0 features:
    python examples/params_dict.py api-call --payload '{"user":"alice"}' '{"action":"login"}'
    python examples/params_dict.py api-call --payload '{"data": @examples/sample_payload.json}'
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_DICT,
    PARAM_GROUP,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def api_call():
    """Make an API call with JSON payload from dict parameter."""
    payload = spafw37.get_param('payload')
    
    spafw37.output("API Call Details:")
    spafw37.output(f"  Payload type: {type(payload)}")
    
    # Pretty print the payload
    import json
    formatted = json.dumps(payload, indent=2)
    spafw37.output(f"\nRequest payload:\n{formatted}")
    
    # Simulate API call
    if 'user' in payload:
        spafw37.output(f"\nCalling API for user: {payload['user']}")
    if 'action' in payload:
        spafw37.output(f"Action: {payload['action']}")
    
    spafw37.output("\n✓ API call successful (simulated)")


def query_database():
    """Query database with filter criteria from dict parameter."""
    filter_criteria = spafw37.get_param('filter')
    
    spafw37.output("Database Query:")
    
    import json
    formatted = json.dumps(filter_criteria, indent=2)
    spafw37.output(f"Filter criteria:\n{formatted}")
    
    # Simulate query
    spafw37.output("\nExecuting query with filters:")
    for key, value in filter_criteria.items():
        if isinstance(value, dict):
            spafw37.output(f"  {key}: {value}")
        else:
            spafw37.output(f"  {key} = {value}")
    
    spafw37.output("\n✓ Query executed (simulated)")


def validate_data():
    """Validate data against a JSON schema from dict parameter."""
    schema = spafw37.get_param('schema')
    
    import json
    formatted = json.dumps(schema, indent=2)
    spafw37.output("JSON Schema for Validation:")
    spafw37.output(formatted)
    
    # Extract and display schema info
    if 'type' in schema:
        spafw37.output(f"\nSchema type: {schema['type']}")
    if 'required' in schema:
        spafw37.output(f"Required fields: {', '.join(schema['required'])}")
    if 'properties' in schema:
        spafw37.output(f"Properties: {', '.join(schema['properties'].keys())}")
    
    spafw37.output("\n✓ Schema loaded and ready for validation")


# Define dict parameters
params = [
    {
        PARAM_NAME: 'payload',
        PARAM_DESCRIPTION: 'API request payload (JSON object)',
        PARAM_ALIASES: ['--payload', '-p'],
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_GROUP: 'API',
    },
    {
        PARAM_NAME: 'filter',
        PARAM_DESCRIPTION: 'Database query filter criteria (JSON object)',
        PARAM_ALIASES: ['--filter', '-f'],
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_GROUP: 'Database',
    },
    {
        PARAM_NAME: 'schema',
        PARAM_DESCRIPTION: 'JSON schema for validation',
        PARAM_ALIASES: ['--schema'],
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_GROUP: 'Validation',
    },
]

# Define commands
commands = [
    {
        COMMAND_NAME: 'api-call',
        COMMAND_DESCRIPTION: 'Make an API call with JSON payload',
        COMMAND_ACTION: api_call,
    },
    {
        COMMAND_NAME: 'query-db',
        COMMAND_DESCRIPTION: 'Query database with filter criteria',
        COMMAND_ACTION: query_database,
    },
    {
        COMMAND_NAME: 'validate',
        COMMAND_DESCRIPTION: 'Validate data against JSON schema',
        COMMAND_ACTION: validate_data,
    },
]

if __name__ == '__main__':
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    spafw37.run_cli()
