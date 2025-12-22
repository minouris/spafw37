# Step 1: Module-level Imports

This step documents all module-level imports required for the test file and implementation file to support all subsequent steps.

## Overview

Add all necessary imports to `tests/test_command.py` and `src/spafw37/command.py` to support the helper functions and tests in Steps 1-6.
**No methods or tests in this step** - only import statements.
## Test File Imports (tests/test_command.py)

```python
# Standard library
import pytest

# Project imports - constants
from spafw37.constants.command import (
    COMMAND_ACTION,
    COMMAND_CYCLE,
    COMMAND_GOES_AFTER,
    COMMAND_GOES_BEFORE,
    COMMAND_NAME,
    COMMAND_NEXT_COMMANDS,
    COMMAND_PHASE,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_REQUIRE_BEFORE,
    COMMAND_TRIGGER_PARAM,
    COMMAND_VISIBLE_IF_PARAM,
)
from spafw37.constants.param import PARAM_NAME

# Project imports - modules
from spafw37 import command, config, cycle, param
```

## Implementation File Imports (src/spafw37/command.py)

```python
# Constants imports already present in command.py
# No additional imports required for the helper functions in Steps 1-6
```

## Notes

- All constants from `spafw37.constants.command` used across Steps 1-6 are imported explicitly
- `PARAM_NAME` from `spafw37.constants.param` is needed for Step 2 (inline params)
- Module imports include `command`, `param` (Steps 1-2, 6), `config` (Step 5), and `cycle` (Step 6)
- These imports should be added to `tests/test_command.py` before implementing any step
- Implementation file `src/spafw37/command.py` already has all necessary constant imports
