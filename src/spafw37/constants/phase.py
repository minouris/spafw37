"""Command execution phase constants.

These constants define the phases in which commands can be executed,
allowing for ordered execution of commands across different stages
of the application lifecycle.
"""

# Phase Definitions
PHASE_SETUP = "phase-setup"  # Phase where setup and configuration commands run (help, load-config)
PHASE_CLEANUP = "phase-cleanup"  # Phase where cleanup commands are run
PHASE_EXECUTION = "phase-execution"  # Phase where main execution commands are run
PHASE_TEARDOWN = "phase-teardown"  # Phase where teardown commands are run (save-config)
PHASE_END = "phase-end"  # Phase where end-of-process commands are run
PHASE_DEFAULT = PHASE_EXECUTION  # Default phase for commands

# Phase Order
PHASE_ORDER = [  # Order in which phases are run - if we do this as an array that gets passed around, we can allow custom phases per application
    PHASE_SETUP,
    PHASE_CLEANUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
    PHASE_END,
]
