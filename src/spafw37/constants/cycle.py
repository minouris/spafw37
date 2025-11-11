from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION
)

"""
System for running repeated sequences of commands in a loop, with initialization and finalization functions.

When the command is queued, the required params for all commands in the attached cycle should be checked before 
the command is run - this should happen during the normal param checking phase.

Normal sequencing rules apply both for the command that has the cycle, and also for the commands within the cycle.
If the commands within the cycle define prerequisite commands, they should be considered as part of the cycle's execution,
unless they are in a different phase - essentially, the cycle commands should be parsed and treated as normal commands,
except that commands WITHIN the cycle must all be of the same phase, and should not be queued via a direct command.

In-Cycle commands should not be triggered by params outside the cycle - they are only run as part of the cycle execution.
In-Cycle commands can define prerequisite commands, but these must also be within the cycle. If a prerequisite command is outside the cycle,
it should be defined as a prerequisite for the command that defines the cycle, not for the in-cycle command.

"""

CYCLE_COMMAND = "cycle-command" # Attaches a cycle to a command, from the cycle side


                                        # regular commands, false for cycle-internal commands. Will need to be added to regular
                                        # processing rules, and to help displays - should not be shown in help, but command help text will
                                        # be shown as part of the help for the parent command.

CYCLE_NAME = "cycle-name"               # Provide a name for the cycle for references and logging
CYCLE_INIT = "cycle-init-function"      # Function to initialize resources for this cycle - runs after the command action, if one is defined
CYCLE_LOOP = "cycle-loop-function"      # function to call each loop iteration - return true to continue, false to exit. 
                                        # Runs at the start of each loop, should prepare resources for that iteration, e.g. queue up the next 
                                        # file / whatever
CYCLE_END = "cycle-finalize-function"   # Runs after the last iteration of the cycle, for cleanup of resources and reporting
CYCLE_COMMANDS = "cycle-commands"       # List of commands to run in this cycle. Must all be in the same phase, should follow all 
                                        # the usual sequence / requirement rules