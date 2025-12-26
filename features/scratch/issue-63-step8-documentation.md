### Step 8: Update documentation

#### Overview

This step updates all relevant documentation to reflect the new top-level cycle registration API.

**Files to update:**
- `doc/cycles.md` - Add section on top-level cycle registration
- `doc/api-reference.md` - Add add_cycle() and add_cycles() function signatures
- `README.md` - Update features list and add "What's New" section

**Tests created:**
- Manual review tests (Tests 8.2.1-8.2.3)

#### Module-level imports

No imports needed - documentation files only.

#### Algorithm

##### Documentation Updates

1. **cycles.md**: Add new section explaining top-level API
2. **api-reference.md**: Document new public functions
3. **README.md**: Update features list and add version notice

#### Implementation

##### Code 8.1.1: Update doc/cycles.md

**File:** `doc/cycles.md`

**Action:** Add new section after existing cycle documentation

````markdown
#### Top-Level Cycle Registration

**Added in v1.1.0**

Cycles can be registered as top-level objects using `add_cycle()` and `add_cycles()`, providing an alternative to inline `COMMAND_CYCLE` definitions.

##### API Functions

**`add_cycle(cycle_def)`**

Register a single cycle definition:

```python
from spafw37 import core as spafw37
from spafw37.constants.cycle import CYCLE_COMMAND, CYCLE_NAME, CYCLE_LOOP

cycle = {
    CYCLE_COMMAND: 'my-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_LOOP: lambda: True
}
spafw37.add_cycle(cycle)
```

**`add_cycles(cycle_defs)`**

Register multiple cycle definitions:

```python
cycles = [
    {CYCLE_COMMAND: 'cmd1', CYCLE_NAME: 'cycle1', CYCLE_LOOP: loop1},
    {CYCLE_COMMAND: 'cmd2', CYCLE_NAME: 'cycle2', CYCLE_LOOP: loop2}
]
spafw37.add_cycles(cycles)
```

##### CYCLE_COMMAND Field

The `CYCLE_COMMAND` field identifies which command the cycle attaches to. It can be:

- **String**: Command name reference (command may exist or be registered later)
- **Dict**: Inline command definition (command registered immediately)

```python
### String reference
cycle = {
    CYCLE_COMMAND: 'existing-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_LOOP: loop_fn
}

### Inline definition
cycle = {
    CYCLE_COMMAND: {
        COMMAND_NAME: 'new-command',
        COMMAND_ACTION: action_fn
    },
    CYCLE_NAME: 'my-cycle',
    CYCLE_LOOP: loop_fn
}
```

##### Registration Order

Cycles can be registered before or after their target commands:

```python
### Cycle before command
spafw37.add_cycle({CYCLE_COMMAND: 'future-cmd', ...})
spafw37.add_command({COMMAND_NAME: 'future-cmd', ...})

### Command before cycle
spafw37.add_command({COMMAND_NAME: 'existing-cmd', ...})
spafw37.add_cycle({CYCLE_COMMAND: 'existing-cmd', ...})
```

##### Duplicate Handling

When a cycle is registered for a command that already has a cycle (via multiple `add_cycle()` calls or both inline and top-level):

- **Identical definitions**: First registration wins, subsequent identical registrations are silently skipped
- **Different definitions**: `ValueError` is raised to prevent conflicting configurations

This allows the same cycle definition to appear in multiple modules (useful for testing and modular code) while catching actual conflicts.

##### Benefits

- **API Consistency**: Matches `add_param()`/`add_params()` and `add_command()`/`add_commands()` patterns
- **Separation of Concerns**: Cycles defined separately from commands
- **Cleaner Organisation**: Related cycles grouped together
- **Flexible Order**: Register cycles and commands in any order
- **Inline Commands**: Commands can be defined inline in `CYCLE_COMMAND` field

See `examples/cycles_toplevel_api.py` for complete usage examples.
````

##### Code 8.1.2: Update doc/api-reference.md

**File:** `doc/api-reference.md`

**Action:** Add new section in core API functions area

````markdown
##### add_cycle(cycle_def)

Register a cycle definition for a command.

**Added in v1.1.0**

**Parameters:**
- `cycle_def` (dict): Cycle definition containing:
  - `CYCLE_COMMAND` (str or dict): Target command name or inline definition (required)
  - `CYCLE_NAME` (str): Cycle identifier (required)
  - `CYCLE_LOOP` (callable): Loop condition function (required)
  - `CYCLE_INIT` (callable): Initialisation function (optional)
  - `CYCLE_LOOP_START` (callable): Loop start function (optional)
  - `CYCLE_LOOP_END` (callable): Loop end function (optional)
  - `CYCLE_END` (callable): Cleanup function (optional)
  - `CYCLE_COMMANDS` (list): Commands in cycle (optional)

**Returns:** None

**Raises:**
- `ValueError`: If required fields missing or conflicting cycle registered

**Example:**
```python
from spafw37 import core as spafw37
cycle = {
    CYCLE_COMMAND: 'process',
    CYCLE_NAME: 'process-cycle',
    CYCLE_LOOP: lambda: True
}
spafw37.add_cycle(cycle)
```

---

##### add_cycles(cycle_defs)

Register multiple cycle definitions.

**Added in v1.1.0**

**Parameters:**
- `cycle_defs` (list): List of cycle definition dicts

**Returns:** None

**Raises:**
- `ValueError`: If any cycle validation fails

**Example:**
```python
from spafw37 import core as spafw37
cycles = [
    {CYCLE_COMMAND: 'cmd1', CYCLE_NAME: 'cycle1', CYCLE_LOOP: loop1},
    {CYCLE_COMMAND: 'cmd2', CYCLE_NAME: 'cycle2', CYCLE_LOOP: loop2}
]
spafw37.add_cycles(cycles)
```
````

##### Code 8.1.3: Update README.md features list

**File:** `README.md`

**Action:** Add to Features section and create What's New section

````markdown
<!-- In Features section, add bullet: -->
- **Top-Level Cycle Registration**: Define cycles with `add_cycle()` and `add_cycles()` functions, separate from commands, for cleaner code organisation

<!-- Add new section after Installation: -->
#### What's New in v1.1.0

- **Top-Level Cycle API**: New `add_cycle()` and `add_cycles()` functions allow cycles to be registered as top-level objects, matching the pattern established by `add_param()` and `add_command()`
- **Inline Command Definitions**: The `CYCLE_COMMAND` field now supports both string references and inline command definitions (dicts)
- **Flexible Registration Order**: Cycles can be registered before or after their target commands
- **Equivalency Checking**: Duplicate cycle registrations with identical definitions are silently skipped; different definitions raise errors

See `doc/cycles.md` and `examples/cycles_toplevel_api.py` for details.

<!-- In Examples section, add to list: -->
- `cycles_toplevel_api.py` - Top-level cycle registration with add_cycle() and add_cycles()
````

##### Test 8.2.1: cycles.md includes new top-level API section

**File:** Manual review

```gherkin
Scenario: Review cycles.md for top-level API documentation
  Given the updated cycles.md file
  When reviewing the content
  Then a "Top-Level Cycle Registration" section should exist
  And it should document add_cycle() and add_cycles() functions
  And it should explain CYCLE_COMMAND string vs dict formats
  And it should cover registration order flexibility
  And it should explain duplicate handling behaviour
  
  # Tests: User guide completeness
  # Validates: Developers can learn to use new API
```

**Manual review checklist:**
- [ ] "Top-Level Cycle Registration" section exists
- [ ] Section marked "**Added in v1.1.0**"
- [ ] `add_cycle()` function documented with example
- [ ] `add_cycles()` function documented with example
- [ ] CYCLE_COMMAND string vs dict formats explained
- [ ] Registration order flexibility documented
- [ ] Duplicate handling (equivalency checking) explained
- [ ] Link to `examples/cycles_toplevel_api.py` included
- [ ] UK English spelling throughout (behaviour, organisation, etc.)

##### Test 8.2.2: api-reference.md includes new functions

**File:** Manual review

```gherkin
Scenario: Review api-reference.md for function signatures
  Given the updated api-reference.md file
  When searching for add_cycle() and add_cycles()
  Then both functions should be listed with parameters
  And return types should be documented
  And parameter descriptions should be complete
  
  # Tests: API reference completeness
  # Validates: Developer reference includes new functions
```

**Manual review checklist:**
- [ ] `add_cycle(cycle_def)` documented with full signature
- [ ] `add_cycles(cycle_defs)` documented with full signature
- [ ] Both functions marked "**Added in v1.1.0**"
- [ ] Parameter types specified (dict, list)
- [ ] Required vs optional parameters indicated
- [ ] CYCLE_COMMAND field types documented (str or dict)
- [ ] Return types documented (None)
- [ ] Exceptions documented (ValueError)
- [ ] Code examples provided for both functions
- [ ] UK English spelling throughout

##### Test 8.2.3: README.md features list updated

**File:** Manual review

```gherkin
Scenario: Review README.md features section
  Given the updated README.md file
  When reviewing the features list
  Then top-level cycle registration should be mentioned
  And code example should show new API
  And "What's New in v1.1.0" section should mention this feature
  
  # Tests: README feature visibility
  # Validates: Users discover new feature from README
```

**Manual review checklist:**
- [ ] Features list includes top-level cycle registration bullet
- [ ] "What's New in v1.1.0" section added
- [ ] What's New mentions `add_cycle()` and `add_cycles()`
- [ ] What's New mentions inline CYCLE_COMMAND support
- [ ] What's New mentions flexible registration order
- [ ] What's New mentions equivalency checking
- [ ] Link to `doc/cycles.md` included
- [ ] Examples list includes `cycles_toplevel_api.py`
- [ ] UK English spelling throughout (organisation, behaviour, etc.)

#### Implementation Order

1. Update `doc/cycles.md` (Code 8.1.1)
2. Update `doc/api-reference.md` (Code 8.1.2)
3. Update `README.md` (Code 8.1.3)
4. Manual review of all documentation (Tests 8.2.1-8.2.3)

#### Notes

- All documentation must use UK English spelling (behaviour, organisation, initialise, etc.)
- Mark all new sections with "**Added in v1.1.0**"
- Provide clear code examples in all documentation
- Cross-reference between documents (cycles.md ↔ examples, README ↔ docs)
- Ensure consistent terminology throughout all docs
