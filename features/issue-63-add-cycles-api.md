# Issue #63: Add top-level add_cycles() API for cycle definitions

**GitHub Issue:** https://github.com/minouris/spafw37/issues/63

## Overview

Currently, cycles can only be defined inline with commands using the `COMMAND_CYCLE` property. This works but is not consistent with how other framework objects (params, commands) are registered using top-level `add_params()` and `add_commands()` functions.

### Proposed Feature

Add `add_cycles()` and `add_cycle()` functions to the core API to allow cycles to be defined as top-level objects, similar to how params and commands are registered.

#### Current API (inline only):
```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.cycle import (
    CYCLE_NAME, CYCLE_INIT, CYCLE_LOOP, CYCLE_LOOP_START,
    CYCLE_LOOP_END, CYCLE_END, CYCLE_COMMANDS
)

commands = [{
    COMMAND_NAME: 'my-command',
    COMMAND_ACTION: my_action,
    COMMAND_CYCLE: {
        CYCLE_NAME: 'my-cycle',
        CYCLE_INIT: init_fn,
        CYCLE_LOOP: loop_fn,
        CYCLE_LOOP_START: loop_start_fn,
        CYCLE_LOOP_END: loop_end_fn,
        CYCLE_END: end_fn,
        CYCLE_COMMANDS: cycle_commands,
    }
}]
spafw37.add_commands(commands)
```

#### Proposed API (top-level - plural):
```python
from spafw37 import core as spafw37
from spafw37.constants.cycle import (
    CYCLE_COMMAND, CYCLE_NAME, CYCLE_INIT, CYCLE_LOOP,
    CYCLE_LOOP_START, CYCLE_LOOP_END, CYCLE_END, CYCLE_COMMANDS
)

cycles = [{
    CYCLE_COMMAND: 'my-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_INIT: init_fn,
    CYCLE_LOOP: loop_fn,
    CYCLE_LOOP_START: loop_start_fn,
    CYCLE_LOOP_END: loop_end_fn,
    CYCLE_END: end_fn,
    CYCLE_COMMANDS: cycle_commands,
}]
spafw37.add_cycles(cycles)
```

#### Proposed API (top-level - singular):
```python
from spafw37 import core as spafw37
from spafw37.constants.cycle import (
    CYCLE_COMMAND, CYCLE_NAME, CYCLE_INIT, CYCLE_LOOP,
    CYCLE_LOOP_START, CYCLE_LOOP_END, CYCLE_END, CYCLE_COMMANDS
)

cycle = {
    CYCLE_COMMAND: 'my-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_INIT: init_fn,
    CYCLE_LOOP: loop_fn,
    CYCLE_LOOP_START: loop_start_fn,
    CYCLE_LOOP_END: loop_end_fn,
    CYCLE_END: end_fn,
    CYCLE_COMMANDS: cycle_commands,
}
spafw37.add_cycle(cycle)
```

### Requirements

- Implement `add_cycles()` - accepts a list of cycle definitions
- Implement `add_cycle()` - accepts a single cycle definition
- Both functions should be exposed through `core.py` (public API)
- Follow existing patterns from `add_param()`/`add_params()` and `add_command()`/`add_commands()`

### Benefits

- Consistency with `add_params()` and `add_commands()` API design
- Separation of concerns (cycles defined separately from commands)
- Cleaner code organisation for complex workflows
- Easier testing with top-level cycle definitions
- Flexibility to add single cycles or multiple cycles at once

### Context

This feature was identified during implementation of Issue #15 (User Input Params) when writing integration tests. The tests assumed `add_cycles()` existed but it does not.

**Key architectural decisions:**

- **API consistency:** New `add_cycle()` and `add_cycles()` functions mirror existing `add_param()`/`add_params()` and `add_command()`/`add_commands()` patterns for consistent developer experience
- **Cycle storage:** Cycles will be stored in a module-level registry (`_cycles` dict) in `cycle.py`, with command name as key to support cycle lookup
- **Integration approach:** Cycles registered via top-level API will be associated with commands during command registration phase (in `add_command()`)
- **Backward compatibility:** Existing inline `COMMAND_CYCLE` definition method continues to work unchanged; new API provides alternative registration approach
- **Equivalency checking:** Duplicate cycle registrations use deep equality comparison - identical definitions silently skip (no error), different definitions raise `ValueError`
- **Validation timing:** Cycle structure validated immediately on registration, command reference validated when command is registered (flexible order)
- **Immutability:** Cycles are immutable once registered - no editing capability (prevents scattered definitions across codebase)
- **CYCLE_NAME property:** Cycles have independent identifiers separate from command names for identification and logging (multi-command attachment is potential future enhancement, not in scope for this issue)
- **Inline command definitions:** Commands can be defined inline within `CYCLE_COMMANDS` list (similar to how params can be defined inline in `COMMAND_REQUIRED_PARAMS`)

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add cycle storage and registration functions to cycle.py](#1-add-cycle-storage-and-registration-functions-to-cyclepy)
  - [2. Add support for inline function definitions in cycles](#2-add-support-for-inline-function-definitions-in-cycles)
  - [3. Modify command registration to check for top-level cycles](#3-modify-command-registration-to-check-for-top-level-cycles)
  - [4. Expose new functions through core.py facade](#4-expose-new-functions-through-corepy-facade)
  - [5. Update constants file with CYCLE_NAME property](#5-update-constants-file-with-cycle_name-property)
  - [6. Create example demonstrating new API](#6-create-example-demonstrating-new-api)
  - [7. Update documentation](#7-update-documentation)
- [Further Considerations](#further-considerations)
  - [1. Error handling for duplicate cycle definitions](#1-error-handling-for-duplicate-cycle-definitions---resolved)
  - [2. Validation of CYCLE_COMMAND field](#2-validation-of-cycle_command-field---resolved)
  - [3. Priority when both inline and top-level cycles exist](#3-priority-when-both-inline-and-top-level-cycles-exist---resolved)
  - [4. Related Issue: Commands and params validation](#4-related-issue-commands-and-params-validation)
- [Success Criteria](#success-criteria)
- [Planning Checklist](#planning-checklist)
- [Implementation Log](#implementation-log)
- [Implementation Checklist](#implementation-checklist)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps

### 1. Add cycle storage and registration functions to cycle.py

**File:** `src/spafw37/cycle.py`

Add module-level `_cycles` dictionary to store cycle definitions indexed by command name. Implement `add_cycle()` (single) and `add_cycles()` (plural) functions following the pattern established in `param.py` and `command.py`. Implement equivalency checking helper function for deep equality comparison of cycle definitions.

**Tests:** Test cycle storage, registration functions, equivalency checking, duplicate handling

**Test 1.2.1: Module-level cycles storage initialised**

```gherkin
Scenario: Module-level _cycles dict exists
  Given the cycle module is imported
  When the module is loaded
  Then _cycles dict should exist at module level
  And _cycles dict should be empty initially
  
  # Tests: Module-level storage initialization
  # Validates: Infrastructure for storing registered cycles
```

**Test 1.2.2: add_cycle() registers single cycle definition**

```gherkin
Scenario: Register single cycle via add_cycle()
  Given a valid cycle definition with CYCLE_COMMAND and CYCLE_NAME
  When add_cycle() is called with the cycle dict
  Then the cycle should be stored in _cycles indexed by command name
  And no exceptions should be raised
  
  # Tests: Single cycle registration via add_cycle()
  # Validates: Basic cycle storage mechanism works correctly
```

**Test 1.2.3: add_cycles() registers multiple cycle definitions**

```gherkin
Scenario: Register multiple cycles via add_cycles()
  Given a list of valid cycle definitions for different commands
  When add_cycles() is called with the list
  Then all cycles should be stored in _cycles indexed by command names
  And no exceptions should be raised
  
  # Tests: Bulk cycle registration via add_cycles()
  # Validates: Plural function follows param/command patterns
```

**Test 1.2.4: add_cycle() validates required CYCLE_COMMAND field**

```gherkin
Scenario: Missing CYCLE_COMMAND field
  Given a cycle definition without CYCLE_COMMAND field
  When add_cycle() is called
  Then ValueError should be raised
  And error message should indicate missing CYCLE_COMMAND
  
  # Tests: Required field validation
  # Validates: Cannot register cycle without target command
```

**Test 1.2.5: add_cycle() validates required CYCLE_NAME field**

```gherkin
Scenario: Missing CYCLE_NAME field
  Given a cycle definition without CYCLE_NAME field
  When add_cycle() is called
  Then ValueError should be raised
  And error message should indicate missing CYCLE_NAME
  
  # Tests: Required field validation for cycle identifier
  # Validates: Cycles must have independent identifiers
```

**Test 1.2.6: add_cycle() validates required CYCLE_LOOP field**

```gherkin
Scenario: Missing CYCLE_LOOP field
  Given a cycle definition without CYCLE_LOOP field
  When add_cycle() is called
  Then ValueError should be raised
  And error message should indicate missing CYCLE_LOOP
  
  # Tests: Required field validation for loop function
  # Validates: Cycles must define loop behaviour
```

**Test 1.2.7: Equivalency checking - identical cycles silently skip**

```gherkin
Scenario: Register identical cycle definition twice
  Given a cycle definition registered for a command
  When add_cycle() is called again with identical definition
  Then the second registration should be silently skipped
  And no exception should be raised
  And the original cycle should remain in _cycles
  
  # Tests: Equivalency checking with first-wins behaviour
  # Validates: Identical definitions don't cause errors (useful for modular code)
```

**Test 1.2.8: Equivalency checking - different cycles raise error**

```gherkin
Scenario: Register different cycle for same command
  Given a cycle definition registered for a command
  When add_cycle() is called with different definition for same command
  Then ValueError should be raised
  And error message should indicate conflicting cycle definitions
  And the original cycle should remain in _cycles
  
  # Tests: Conflict detection for different definitions
  # Validates: Prevents conflicting cycle configurations
```

**Test 1.2.9: Equivalency checking compares all cycle properties**

```gherkin
Scenario: Cycles differ only in optional property
  Given a cycle registered with CYCLE_INIT function
  When add_cycle() is called with same command but different CYCLE_INIT
  Then ValueError should be raised
  And error message should indicate conflicting definitions
  
  # Tests: Deep equality comparison of cycle definitions
  # Validates: All properties checked, not just required fields
```

**Test 1.2.10: Equivalency checking compares function references**

```gherkin
Scenario: Cycles with same function objects
  Given a cycle registered with specific function references
  When add_cycle() is called with same command and same function objects
  Then the second registration should be silently skipped
  And no exception should be raised
  
  # Tests: Function object identity comparison
  # Validates: Same functions recognised as equivalent
```

**Test 1.2.11: get_cycle() retrieves registered cycle**

```gherkin
Scenario: Retrieve cycle by command name
  Given a cycle registered for command "my-command"
  When get_cycle("my-command") is called
  Then the cycle definition should be returned
  And the dict should contain all registered properties
  
  # Tests: Cycle retrieval by command name
  # Validates: Public API for accessing registered cycles
```

**Test 1.2.12: get_cycle() returns None for unregistered command**

```gherkin
Scenario: Request cycle for command with no cycle
  Given no cycle registered for command "unknown-command"
  When get_cycle("unknown-command") is called
  Then None should be returned
  And no exception should be raised
  
  # Tests: Graceful handling of missing cycles
  # Validates: Allows checking if cycle exists without errors
```

[↑ Back to top](#table-of-contents)

### 2. Add support for inline command definitions in cycles

**File:** `src/spafw37/cycle.py`

Add ability to define commands inline within cycle definitions. All commands referenced by a cycle (in `CYCLE_COMMANDS` and any other cycle properties that reference commands) should support inline command definition dicts in addition to command name strings.

**Tests:** Test inline command definitions in CYCLE_COMMANDS property

**Test 2.2.1: Inline command definition in CYCLE_COMMANDS**

```gherkin
Scenario: Cycle with inline command definition
  Given a cycle with CYCLE_COMMANDS containing command dict
  When the cycle is registered via add_cycle()
  Then the cycle should be stored successfully
  And the inline command definition should be preserved
  And no exceptions should be raised
  
  # Tests: Inline command definition support
  # Validates: Commands can be defined inline like params
```

**Test 2.2.2: Mixed inline and string command references**

```gherkin
Scenario: CYCLE_COMMANDS with both dicts and strings
  Given a cycle with CYCLE_COMMANDS containing mix of dicts and strings
  When the cycle is registered via add_cycle()
  Then the cycle should be stored successfully
  And both inline and referenced commands should be preserved
  And no exceptions should be raised
  
  # Tests: Mixed command definition formats
  # Validates: Flexibility in specifying cycle commands
```

**Test 2.2.3: Validation deferred for inline commands**

```gherkin
Scenario: Inline command with forward reference to param
  Given a cycle with inline command referencing param not yet defined
  When the cycle is registered via add_cycle()
  Then the cycle should be stored successfully
  And no validation error should be raised
  
  # Tests: Deferred validation of inline command definitions
  # Validates: Allows flexible registration order
```

[↑ Back to top](#table-of-contents)

### 3. Modify command registration to check for top-level cycles

**File:** `src/spafw37/command.py`

Update `_store_command()` to check if a cycle has been registered for the command via the new top-level API. If found, attach it to the command's `COMMAND_CYCLE` property before calling `cycle.register_cycle()`. Apply equivalency checking when both inline and top-level cycles exist.

**Tests:** Test integration between top-level cycles and command registration, equivalency checking when both exist

**Test 3.2.1: Top-level cycle attached to command**

```gherkin
Scenario: Register command after top-level cycle
  Given a cycle registered via add_cycle() for command "my-command"
  When add_command() is called for "my-command"
  Then the cycle should be attached to command's COMMAND_CYCLE property
  And cycle.register_cycle() should be called with the cycle
  And the command should be stored successfully
  
  # Tests: Top-level cycle integration with command registration
  # Validates: Cycles registered first attach to commands registered later
```

**Test 3.2.2: Command registered before cycle is added**

```gherkin
Scenario: Register command before top-level cycle exists
  Given add_command() is called for "my-command" with no cycle
  When add_cycle() is called later for same command
  Then the cycle should be stored in _cycles
  And the command should remain unchanged (no retroactive attachment)
  And no exceptions should be raised
  
  # Tests: Registration order flexibility
  # Validates: Cycles can be registered after commands without errors
```

**Test 3.2.3: Inline and top-level cycle - identical definitions**

```gherkin
Scenario: Command with inline cycle, then add_cycle() with identical definition
  Given a command registered with inline COMMAND_CYCLE
  When add_cycle() is called for same command with identical definition
  Then the second registration should be silently skipped
  And the command's cycle should remain unchanged
  And no exception should be raised
  
  # Tests: Equivalency checking across inline and top-level APIs
  # Validates: Identical definitions don't conflict
```

**Test 3.2.4: Inline and top-level cycle - different definitions**

```gherkin
Scenario: Command with inline cycle, then add_cycle() with different definition
  Given a command registered with inline COMMAND_CYCLE
  When add_cycle() is called for same command with different definition
  Then ValueError should be raised
  And error message should indicate conflicting cycle definitions
  And the command's cycle should remain unchanged
  
  # Tests: Conflict detection across inline and top-level APIs
  # Validates: Different definitions raise errors
```

**Test 3.2.5: Top-level cycle priority - command with no inline cycle**

```gherkin
Scenario: Command registered with no inline cycle, top-level cycle exists
  Given a cycle registered via add_cycle() for command "my-command"
  When add_command() is called for "my-command" with no COMMAND_CYCLE property
  Then the top-level cycle should be attached to command
  And the command should execute with the cycle
  And no exceptions should be raised
  
  # Tests: Top-level cycle attachment to commands without inline cycles
  # Validates: Top-level API fully functional for commands without inline definitions
```

**Test 3.2.6: Cycle commands registered through command registration**

```gherkin
Scenario: Top-level cycle with inline command definitions
  Given a cycle with CYCLE_COMMANDS containing inline command dicts
  When the parent command is registered
  Then cycle commands should be registered automatically
  And cycle commands should not be CLI-invocable
  And no exceptions should be raised
  
  # Tests: Inline command registration via cycle
  # Validates: Commands defined inline within cycles work correctly
```

[↑ Back to top](#table-of-contents)

### 4. Expose new functions through core.py facade

**File:** `src/spafw37/core.py`

Add `add_cycle()` and `add_cycles()` delegate functions to core.py public API, following the same pattern as existing `add_param()`, `add_params()`, `add_command()`, and `add_commands()` functions.

**Tests:** Test public API functions delegate correctly to cycle module

**Test 4.2.1: core.add_cycle() delegates to cycle.add_cycle()**

```gherkin
Scenario: Call core.add_cycle() with valid cycle definition
  Given a valid cycle definition dict
  When core.add_cycle() is called with the cycle
  Then cycle.add_cycle() should be called
  And the cycle should be stored in cycle._cycles
  And no exceptions should be raised
  
  # Tests: Public API delegation for single cycle
  # Validates: core.py facade provides add_cycle() access
```

**Test 4.2.2: core.add_cycles() delegates to cycle.add_cycles()**

```gherkin
Scenario: Call core.add_cycles() with list of cycle definitions
  Given a list of valid cycle definition dicts
  When core.add_cycles() is called with the list
  Then cycle.add_cycles() should be called
  And all cycles should be stored in cycle._cycles
  And no exceptions should be raised
  
  # Tests: Public API delegation for multiple cycles
  # Validates: core.py facade provides add_cycles() access
```

**Test 4.2.3: API consistency with add_command/add_param patterns**

```gherkin
Scenario: Compare add_cycle() signature with add_command()
  Given function signatures for add_cycle() and add_command()
  When comparing parameter names and types
  Then add_cycle() should follow same pattern
  And function documentation should be consistent
  And return types should match pattern
  
  # Tests: API consistency across registration functions
  # Validates: Consistent developer experience
```

[↑ Back to top](#table-of-contents)

### 5. Update constants file with CYCLE_NAME property

**File:** `src/spafw37/constants/cycle.py`

Ensure `CYCLE_COMMAND` constant is properly defined and documented. Add or update `CYCLE_NAME` property documentation to clarify that cycles have independent identifiers separate from command names, potentially allowing cycles to be attached to multiple commands.

**Tests:** Test constant definitions and documentation

**Test 5.2.1: CYCLE_COMMAND constant defined and exported**

```gherkin
Scenario: Import CYCLE_COMMAND from constants.cycle
  Given the constants.cycle module
  When CYCLE_COMMAND is imported
  Then the constant should be a string
  And the constant should be properly exported
  And no exceptions should be raised
  
  # Tests: CYCLE_COMMAND constant availability
  # Validates: New constant properly defined for top-level API
```

**Test 5.2.2: CYCLE_NAME constant defined and documented**

```gherkin
Scenario: Import CYCLE_NAME from constants.cycle
  Given the constants.cycle module
  When CYCLE_NAME is imported
  Then the constant should be a string
  And the constant should be properly exported
  And documentation should clarify cycle identifier purpose
  
  # Tests: CYCLE_NAME constant availability and documentation
  # Validates: Cycle identifiers separate from command names
```

**Tests:** Manual review to verify constant documentation explains cycle identity vs command association

[↑ Back to top](#table-of-contents)

### 6. Create example demonstrating new API

**File:** `examples/cycles_toplevel_api.py`

Create a new example file showing how to use `add_cycle()` and `add_cycles()` functions to define cycles separately from commands, demonstrating the cleaner code organisation this enables. Include examples of inline function definitions within cycles.

**Tests:** Manual execution and review

**Test 6.2.1: Example executes without errors**

```gherkin
Scenario: Run cycles_toplevel_api.py example
  Given the example file with add_cycle() and add_cycles() usage
  When the example is executed from command line
  Then it should complete successfully without exceptions
  And it should demonstrate cycle execution
  And output should show cycle functions being called
  
  # Tests: Example code functionality
  # Validates: Top-level API works in real usage scenario
```

**Test 6.2.2: Example demonstrates both add_cycle() and add_cycles()**

```gherkin
Scenario: Review example code coverage
  Given the cycles_toplevel_api.py example file
  When reviewing the code
  Then it should use add_cycle() for single cycle
  And it should use add_cycles() for multiple cycles
  And it should demonstrate inline command definitions
  
  # Tests: Example completeness
  # Validates: Both registration approaches documented
```

**Tests:** Manual review to verify example follows all coding standards and demonstrates key features

[↑ Back to top](#table-of-contents)

### 7. Update documentation

**Files:** `doc/cycles.md`, `doc/api-reference.md`, `README.md`

Document the new top-level cycle registration API, update API reference with new functions, and add examples showing both inline and top-level approaches to cycle definition.

**Tests:** Manual review of documentation accuracy and completeness

**Test 7.2.1: cycles.md documents top-level API**

```gherkin
Scenario: Review cycles.md for new API documentation
  Given the updated cycles.md documentation file
  When searching for add_cycle() and add_cycles() documentation
  Then both functions should be documented
  And usage examples should be provided
  And comparison with inline approach should be included
  
  # Tests: User guide completeness
  # Validates: Users can learn new API from documentation
```

**Test 7.2.2: api-reference.md includes new functions**

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

**Test 7.2.3: README.md features list updated**

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

**Tests:** Manual review to verify all documentation follows UK English spelling, uses consistent terminology, and accurately reflects implementation

[↑ Back to top](#table-of-contents)

### 2. Add support for inline command definitions in cycles

**File:** `src/spafw37/cycle.py`

Add ability to define commands inline within cycle definitions. All commands referenced by a cycle (in `CYCLE_COMMANDS` and any other cycle properties that reference commands) should support inline command definition dicts in addition to command name strings.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 3. Modify command registration to check for top-level cycles

**File:** `src/spafw37/command.py`

Update `_store_command()` to check if a cycle has been registered for the command via the new top-level API. If found, attach it to the command's `COMMAND_CYCLE` property before calling `cycle.register_cycle()`. Apply equivalency checking when both inline and top-level cycles exist.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 4. Expose new functions through core.py facade

**File:** `src/spafw37/core.py`

Add `add_cycle()` and `add_cycles()` delegate functions to core.py public API, following the same pattern as existing `add_param()`, `add_params()`, `add_command()`, and `add_commands()` functions.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 5. Update constants file with CYCLE_NAME property

**File:** `src/spafw37/constants/cycle.py`

Ensure `CYCLE_COMMAND` constant is properly defined and documented. Add or update `CYCLE_NAME` property documentation to clarify that cycles have independent identifiers separate from command names, potentially allowing cycles to be attached to multiple commands.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 6. Create example demonstrating new API

**File:** `examples/cycles_toplevel_api.py`

Create a new example file showing how to use `add_cycle()` and `add_cycles()` functions to define cycles separately from commands, demonstrating the cleaner code organisation this enables. Include examples of inline function definitions within cycles.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 7. Update documentation

**Files:** `doc/cycles.md`, `doc/api-reference.md`, `README.md`

Document the new top-level cycle registration API, update API reference with new functions, and add examples showing both inline and top-level approaches to cycle definition.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Error handling for duplicate cycle definitions - RESOLVED

([#issuecomment-3692502569](https://github.com/minouris/spafw37/issues/63#issuecomment-3692502569)) ([Resolution](https://github.com/minouris/spafw37/issues/63#issuecomment-3692548285))

**Question:** Should the framework raise an error if a cycle is registered multiple times for the same command (either via multiple `add_cycle()` calls or via both top-level API and inline `COMMAND_CYCLE`)?

**Answer:** Equivalency checking with first-wins behavior

**Rationale:** When a cycle is registered for a command that already has a cycle, compare for deep equality. If exact duplicate (identical structure, values, functions), silently skip (no error). If different definition, raise `ValueError`. This allows the same definition to appear multiple times (useful for modular code, shared test fixtures) while catching true configuration conflicts. Cycles are immutable once registered - no editing capability needed.

**Implementation:** Add equivalency checking helper function for deep equality comparison. In `add_cycle()` and `_store_command()`, compare cycle definitions before raising errors. First definition wins when identical, error raised when different.

[↑ Back to top](#table-of-contents)

---

### 2. Validation of CYCLE_COMMAND field - RESOLVED

([#issuecomment-3692534496](https://github.com/minouris/spafw37/issues/63#issuecomment-3692534496)) ([Resolution](https://github.com/minouris/spafw37/issues/63#issuecomment-3692587601))

**Question:** What validation should be performed on the `CYCLE_COMMAND` field when a cycle is registered via `add_cycle()`?

**Answer:** Immediate validation of cycle structure, deferred validation of command reference

**Rationale:** Validation is performed immediately when a cycle definition is complete. Required fields (like `CYCLE_LOOP`, `CYCLE_NAME`) and cycle structure are validated immediately. However, the `CYCLE_COMMAND` field does NOT require the command to exist yet (deferred validation of reference). This allows flexible registration order (cycles before commands or vice versa) while catching structural errors immediately.

**Implementation:** `add_cycle()` validates cycle definition structure but does NOT check if command exists. When command is registered, cycle is attached and full integration validation occurs via existing `cycle.register_cycle()`.

[↑ Back to top](#table-of-contents)

---

### 3. Priority when both inline and top-level cycles exist - RESOLVED

([#issuecomment-3692535462](https://github.com/minouris/spafw37/issues/63#issuecomment-3692535462)) ([Resolution](https://github.com/minouris/spafw37/issues/63#issuecomment-3692589909))

**Question:** If a cycle is defined both via top-level `add_cycle()` AND via inline `COMMAND_CYCLE` for the same command, which should take precedence?

**Answer:** First definition wins with equivalency checking (same as Q1)

**Rationale:** When a cycle is registered for a command that already has a cycle (either via another `add_cycle()` call or inline `COMMAND_CYCLE`), compare for deep equality. If exact duplicate, silently skip (no error). If different definition, raise `ValueError` with clear message. This provides consistent behavior regardless of whether the duplicate comes from multiple `add_cycle()` calls or from inline vs top-level definitions.

**Implementation:** Same equivalency checking logic applies whether comparing two top-level cycles or comparing top-level vs inline cycle. First registration wins when identical, error raised when different. Integration point in `_store_command()` checks both inline and top-level cycles and applies equivalency checking.

[↑ Back to top](#table-of-contents)

---

### 4. Related Issue: Commands and params validation

**Issue #87:** Add equivalency checking validation to add_command() and add_param()

The design decisions for cycles (equivalency checking, immutable definitions) revealed that commands and params currently lack this validation. Issue #87 has been created to address this separately from the cycle implementation.

[↑ Back to top](#table-of-contents)

---

## Success Criteria

This issue is considered successfully implemented when:

**Functional Requirements:**
- [ ] `add_cycle()` function accepts a single cycle definition dict and registers it correctly
- [ ] `add_cycles()` function accepts a list of cycle definition dicts and registers all of them
- [ ] Cycles registered via top-level API attach to commands during command registration
- [ ] Cycles defined with `CYCLE_COMMAND` property correctly identify their target command
- [ ] Commands with top-level cycles execute cycle functions (init, loop, loop_start, loop_end, end) correctly
- [ ] Cycle commands remain non-invocable from CLI when registered via top-level API
- [ ] Cycle parameter merging works correctly for top-level cycles (params from cycle commands merge into parent)
- [ ] Phase consistency validation applies to top-level cycles (all cycle commands same phase as parent)
- [ ] Top-level cycle API follows existing validation rules from inline cycles (required fields, nesting depth, etc.)

**Integration Requirements:**
- [ ] Inline `COMMAND_CYCLE` definitions continue to work unchanged (backward compatibility)
- [ ] Both inline and top-level cycle definition methods can coexist in same application
- [ ] Error handling for duplicate/conflicting cycle definitions works as designed (per Further Considerations resolution)
- [ ] Validation of `CYCLE_COMMAND` field works as designed (per Further Considerations resolution)
- [ ] Priority between inline and top-level cycles works as designed (per Further Considerations resolution)

**API Consistency Requirements:**
- [ ] `add_cycle()` and `add_cycles()` are exposed through `core.py` facade (public API)
- [ ] Function signatures and behaviour match patterns from `add_param()`/`add_params()` and `add_command()`/`add_commands()`
- [ ] `CYCLE_COMMAND` constant is properly exported from `constants.cycle` module
- [ ] Error messages are clear and actionable

**Testing Requirements:**
- [ ] Unit tests cover `add_cycle()` and `add_cycles()` functions in `cycle.py`
- [ ] Unit tests cover cycle-command association logic in `command.py`
- [ ] Unit tests cover public API functions in `core.py`
- [ ] Integration tests demonstrate top-level cycle execution
- [ ] Tests verify backward compatibility with inline cycle definitions
- [ ] Tests cover error cases per Further Considerations resolutions
- [ ] Test coverage remains at or above 80%

**Documentation Requirements:**
- [ ] API reference documents new `add_cycle()` and `add_cycles()` functions
- [ ] Cycles user guide updated with top-level API examples
- [ ] New example file demonstrates top-level cycle registration
- [ ] README updated with new API in features list
- [ ] Code examples show both inline and top-level approaches

**Compatibility Requirements:**
- [ ] Works with Python 3.7.0+
- [ ] All existing tests continue to pass
- [ ] No breaking changes to existing cycle functionality

---

## Planning Checklist

This checklist tracks completion of this planning document.

**Plan Structure:**
- [x] Overview section complete with architectural decisions
- [ ] Program Flow Analysis complete (if applicable)
- [x] All implementation steps identified and outlined
- [x] Further Considerations documented (all marked PENDING or RESOLVED)
  - [x] Q1: Error handling for duplicate cycle definitions answered and resolved (Comment #3692502569)
  - [x] Q2: Validation of CYCLE_COMMAND field answered and resolved (Comment #3692534496)
  - [x] Q3: Priority when both inline and top-level cycles exist answered and resolved (Comment #3692535462)
- [x] Success Criteria defined (feature outcomes)
- [ ] Implementation Checklist created (TDD workflow)
- [ ] CHANGES section populated for release
- [x] Table of Contents updated to reflect all sections

**Implementation Details:**
- [x] All implementation steps have detailed code blocks
- [x] All functions have corresponding test specifications
- [ ] All code blocks follow X.Y.Z numbering scheme
- [ ] All tests written in Gherkin + Python format
- [ ] Module-level imports consolidated in Step 1
- [ ] No nesting violations (max 2 levels)
- [ ] No nested blocks exceeding 2 lines
- [ ] All helper functions extracted and documented

**Documentation:**
- [ ] All affected documentation files identified
- [ ] Example files planned (if needed)
- [ ] API reference updates planned (if needed)
- [ ] User guide updates planned (if needed)

**Quality Verification:**
- [ ] All code follows Python 3.7.0 compatibility requirements
- [ ] All code follows UK English spelling conventions
- [ ] No lazy naming (tmp, data, result, i, j, etc.)
- [ ] All functions have proper docstrings
- [ ] Regression tests planned for modified functions

**Ready for Implementation:**
- [ ] Plan reviewed and approved
- [ ] All Further Considerations resolved
- [ ] Success Criteria agreed upon
- [ ] Implementation Checklist ready to execute

[↑ Back to top](#table-of-contents)

---

## Implementation Log

This section will record any errors, deviations, or unexpected issues encountered during implementation (Step 8).

**This section will be populated during Step 8: Implement from Plan.**

[↑ Back to top](#table-of-contents)

---

## Implementation Checklist

[PLACEHOLDER - Will be filled in Step 4: Generate implementation code blocks]

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

[PLACEHOLDER - Will be filled in Step 6]

[↑ Back to top](#table-of-contents)
