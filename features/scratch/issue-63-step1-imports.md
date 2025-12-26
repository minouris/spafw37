### Step 1: Module-level Imports

This file consolidates ALL imports required for implementing Issue #63. Other step files reference this rather than duplicating imports.

#### Module-level imports for src/spafw37/cycle.py

```python
### Standard library imports
from copy import deepcopy

### Internal imports
from spafw37 import command
from spafw37.constants.command import COMMAND_NAME
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP
)
```

#### Module-level imports for src/spafw37/command.py

```python
### Note: command.py already has imports - these are ADDITIONS only

from spafw37 import cycle
```

#### Module-level imports for src/spafw37/core.py

```python
### Note: core.py already has imports - these are ADDITIONS only

from spafw37 import cycle
```

#### Module-level imports for tests/test_cycle.py

```python
### Standard library imports
import pytest

### Internal imports
from spafw37 import command, cycle
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
    CYCLE_END,
    CYCLE_COMMANDS
)
```

#### Module-level imports for tests/test_command.py

```python
### Note: test_command.py already has imports - these are ADDITIONS only

from spafw37 import cycle
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP
)
```

#### Module-level imports for tests/test_core.py

```python
### Note: test_core.py already has imports - these are ADDITIONS only

from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP
)
```
