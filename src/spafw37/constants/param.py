"""Parameter definition constants.

These constants are used as keys in parameter definition dictionaries
to specify parameter properties such as name, type, aliases, persistence, etc.
"""

# Param Definitions
PARAM_NAME = 'name'  # Name of the param
PARAM_DESCRIPTION = 'description'  # Long description of the param
PARAM_CONFIG_NAME = 'config-name'  # The internal name this param is bound to in the config dict. Defaults to PARAM_NAME if not specified.
PARAM_TYPE = 'type'  # The data type of this param (one of PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE, PARAM_TYPE_LIST)
PARAM_ALIASES = 'aliases'  # List of identifiers for this param on the CLI (e.g. --verbose, -v). Params without aliases cannot be set from the command line.
PARAM_REQUIRED = 'required'  # Whether this param always needs to be set, either by the user or in the config file.
PARAM_PERSISTENCE = 'persistence'  # Identifies how/if the param is persisted between runs. PARAM_PERSISTENCE_ALWAYS means always saved to the main config file, PARAM_PERSISTENCE_NEVER means never saved to any config file. Blank or unset means that this param is only saved to User Config files.
PARAM_SWITCH_LIST = 'switch-list'  # Identifies a list of params that are mutually exclusive with this one - only one param in this list can be set at a time.
PARAM_DEFAULT = 'default-value'  # Default value for the param if not set. A param with a default value will always be considered "set" (will be present in config)
PARAM_HAS_VALUE = 'has-value'  # DEPRECATED: Use PARAM_TYPE to determine if param is toggle. For pre-parse params: True if param takes a value, False if toggle
PARAM_RUNTIME_ONLY = 'runtime-only'  # Not persisted, only for runtime use, not checked at start of queue, but checked when a command that uses them is run
PARAM_GROUP = 'param-group'  # Group name for organising parameters in help display

# Param Persistence Options
PARAM_PERSISTENCE_ALWAYS = 'always'  # Param is always persisted to main config file
PARAM_PERSISTENCE_NEVER = 'never'  # Param is never persisted to any config file
PARAM_PERSISTENCE_USER_ONLY = None  # Param is only persisted to user config files

# Param Types
PARAM_TYPE_TEXT = 'text'
PARAM_TYPE_NUMBER = 'number'
PARAM_TYPE_TOGGLE = 'toggle'
PARAM_TYPE_LIST = 'list'
PARAM_TYPE_DICT = 'dict'

# Param Join Configuration
PARAM_JOIN_SEPARATOR = 'join-separator'  # Separator for joining string values in join_param(). Defaults to SEPARATOR_SPACE.

# Input filter - callable to convert string values to proper type
PARAM_INPUT_FILTER = 'input-filter'  # Function to convert CLI string values to proper type before validation

# Default input filters by param type - maps PARAM_TYPE values to filter function names
# These are resolved in param.py to actual functions
PARAM_DEFAULT_INPUT_FILTERS = {
    # Keys are PARAM_TYPE_* values, values are function names in param module
    'text': '_default_filter_text',
    'number': '_default_filter_number',
    'toggle': '_default_filter_toggle',
    'list': '_default_filter_list',
    'dict': '_default_filter_dict',
}

# Dict Merge Type Options (for join_param with dicts)
DICT_MERGE_SHALLOW = 'shallow'  # Only merge top-level keys (default)
DICT_MERGE_DEEP = 'deep'  # Recursively merge nested dicts

# Dict Merge Type Configuration
PARAM_DICT_MERGE_TYPE = 'dict-merge-type'  # Controls dict merge behavior: DICT_MERGE_SHALLOW (default) or DICT_MERGE_DEEP

# Dict Override Strategy Options (for join_param with dicts)
DICT_OVERRIDE_RECENT = 'recent'  # New value overwrites existing (default)
DICT_OVERRIDE_OLDEST = 'oldest'  # Existing value kept, new value ignored
DICT_OVERRIDE_ERROR = 'error'  # Raise error on key collision

# Dict Override Strategy Configuration
PARAM_DICT_OVERRIDE_STRATEGY = 'dict-override-strategy'  # Controls collision handling: DICT_OVERRIDE_RECENT (default), DICT_OVERRIDE_OLDEST, or DICT_OVERRIDE_ERROR

# Common Separator Constants (for convenience)
SEPARATOR_SPACE = ' '
SEPARATOR_COMMA = ','
SEPARATOR_COMMA_SPACE = ', '
SEPARATOR_PIPE = '|'
SEPARATOR_PIPE_PADDED = ' | '
SEPARATOR_NEWLINE = '\n'
SEPARATOR_TAB = '\t'
