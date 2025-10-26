# Param Definitions
PARAM_NAME          = 'name'
PARAM_DESCRIPTION   = 'description'
PARAM_BIND_TO       = 'bind_to'
PARAM_TYPE          = 'type'
PARAM_ALIASES       = 'aliases'
PARAM_REQUIRED      = 'required'
PARAM_PERSISTENCE   = 'persistence'
PARAM_SWITCH_LIST   = 'switch-list'
PARAM_DEFAULT       = 'default-value'
PARAM_RUNTIME_ONLY   = 'runtime-only' # Not persisted, only for runtime use, not checked at startof queue, but checked when a command that uses them is run
PARAM_DEFERRED       = 'deferred' # When False, param should be processed immediately instead of being buffered (default: True for all params)
PARAM_GROUP         = 'param-group' # Group name for organizing parameters in help display


PARAM_PERSISTENCE_ALWAYS    = 'always'
PARAM_PERSISTENCE_NEVER     = 'never'

# Param Types
PARAM_TYPE_TEXT     = 'text'
PARAM_TYPE_NUMBER   = 'number'
PARAM_TYPE_TOGGLE   = 'toggle'
PARAM_TYPE_LIST     = 'list'

CONFIG_INFILE_PARAM='config-infile'
CONFIG_OUTFILE_PARAM='config-outfile'

CONFIG_INFILE_ALIAS = '--save-config'
CONFIG_OUTFILE_ALIAS = '--load-config'

# Run-level definitions
RUN_LEVEL_NAME = 'run-level-name'  # Name of the run-level
RUN_LEVEL_PARAMS = 'run-level-params'  # List of param bind names that are parsed in this run level
RUN_LEVEL_COMMANDS = 'run-level-commands'  # List of commands that are parsed and executed in this run-level
RUN_LEVEL_CONFIG = 'run-level-config'  # Dictionary of config name-value pairs to set for this run-level
RUN_LEVEL_ERROR_HANDLER = 'run-level-error-handler'  # Optional custom error handler for this run-level

# Command Definitions
COMMAND_NAME = "command-name" # Used on the CLI to queue the command
COMMAND_REQUIRED_PARAMS = "required-params" # List of param bind names that are required for this command
COMMAND_DESCRIPTION = "description" # Description of the command
COMMAND_HELP = "command-help" # Extended help text for the command
COMMAND_ACTION = "function" # Function to call when the command is run
COMMAND_GOES_BEFORE = "sequence-before" # List of command names that will be sequenced before this in a queue - user queued
COMMAND_GOES_AFTER = "sequence-after" # List of command names that will be sequenced after this in a queue - user queued
COMMAND_REQUIRE_BEFORE = "require-before" # List of command names that must be completed before this in a queue - automatically queued if this command is invoked
COMMAND_NEXT_COMMANDS = "next-commands" # List of command names that will be automatically queued after this command is run
COMMAND_TRIGGER_PARAM = "trigger-param" # Param bind name that triggers this command when set
COMMAND_PHASE = "command-phase" # Phase in which this command should be run
COMMAND_FRAMEWORK = "framework" # True if this is a framework-defined command (vs app-defined)

# Command Phases
PHASE_SETUP = "phase-setup" # Phase where config commands and suchlike happen
PHASE_CLEANUP = "phase-cleanup" # Phase where cleanup commands are run
PHASE_EXECUTION = "phase-execution" # Phase where main execution commands are run
PHASE_TEARDOWN = "phase-teardown" # Phase where teardown commands are run
PHASE_END = "phase-end" # Phase where end-of-process commands are run
PHASE_DEFAULT = PHASE_EXECUTION # Default phase for commands

PHASE_ORDER = [ # Order in which phases are run - if we do this as an array that gets passed around, we can allow custom phases per application
    PHASE_SETUP,
    PHASE_CLEANUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
    PHASE_END
]

# Will require queue functions to take an actual queue parameter, rather than using the global one. Dynamic command queueing
# must be able to add commands to other queues - a Map of queues will likely be required to implement this, so they can be easily 
# referred to by Phase. Each Phase queue will run in order. Commands in one phase can add commands to later phases, but not earlier ones.
# Likewise, parameter triggered commands will not be added to a phase that has already run.