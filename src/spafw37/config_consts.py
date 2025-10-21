# Param Definitions
PARAM_NAME          = 'name'
PARAM_DESCRIPTION   = 'description'
PARAM_BIND_TO       = 'bind_to'
PARAM_TYPE          = 'type'
PARAM_ALIASES       = 'aliases'
PARAM_REQUIRED      = 'required'
PARAM_PERSISTENCE   = 'persistence'
PARAM_SWITCH_LIST   = 'switch-list'
PARAM_ALWAYS_SET    = 'always-set'
PARAM_DEFAULT       = 'default-value'

PARAM_PERSISTENCE_ALWAYS    = 'always'
PARAM_PERSISTENCE_NEVER     = 'never'

# Param Types
PARAM_TYPE_TEXT     = 'text'
PARAM_TYPE_NUMBER   = 'number'
PARAM_TYPE_TOGGLE   = 'toggle'
PARAM_TYPE_LIST     = 'list'

CONFIG_INFILE_PARAM='config-infile'
CONFIG_OUTFILE_PARAM='config-outfile'

# Command Definitions
COMMAND_NAME = "command-name" # Used on the CLI to queue the command
COMMAND_REQUIRED_PARAMS = "required-params" # List of param bind names that are required for this command
COMMAND_DESCRIPTION = "description" # Description of the command
COMMAND_ACTION = "function" # Function to call when the command is run
COMMAND_GOES_BEFORE = "sequence-before" # List of command names that will be sequenced before this in a queue - user queued
COMMAND_GOES_AFTER = "sequence-after" # List of command names that will be sequenced after this in a queue - user queued
COMMAND_REQUIRE_BEFORE = "require-before" # List of command names that must be completed before this in a queue - automatically queued if this command is invoked
COMMAND_NEXT_COMMANDS = "next-commands" # List of command names that will be automatically queued after this command is run