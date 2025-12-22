# Issue #61: Refactor command.add_command() into focused helper methods

**GitHub Issue:** https://github.com/minouris/spafw37/issues/61

## Overview

The `command.add_command()` function has become monolithic and difficult to maintain. It handles multiple responsibilities in a single function:
- Command name validation
- Inline parameter definition processing
- Required parameter validation
- Dependency validation
- Trigger parameter handling
- Phase assignment
- Visibility control
- Command storage and registration

This makes the function hard to test, understand, and modify.

This refactoring will delegate responsibilities to focused helper methods, similar to the pattern used in issue #15 for prompt param processing. The refactored structure will create a high-level orchestrator function that calls discrete helpers, each with a single clear responsibility.

Each helper method will have focused unit tests, clear error messages, and reusable logic. The refactoring maintains backward compatibility - only internal structure changes, with no modifications to the public API or existing behaviour.

**Key architectural decisions:**

- **[Pattern]:** Follow issue #15's helper method pattern - extract focused private functions with single responsibilities, each with clear naming and dedicated tests
- **[Testing strategy]:** Incremental extraction with test verification after each step - leverage existing 95% test coverage to guard against regression
- **[Helper scope]:** Private helpers with `_` prefix - internal implementation details not part of public API
- **[Extraction order]:** Validation first (simplest), then inline processing (most complex), then registration (storage)
- **[Backward compatibility]:** Zero API changes - only internal structure refactoring, all existing tests must pass unchanged

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Extract validation helpers](#step-1-extract-validation-helpers)
  - [2. Extract inline parameter processing](#step-2-extract-inline-parameter-processing)
  - [3. Extract inline command processing](#step-3-extract-inline-command-processing)
  - [4. Extract phase assignment](#step-4-extract-phase-assignment)
  - [5. Extract command storage](#step-5-extract-command-storage)
- [Further Considerations](#further-considerations)
- [Success Criteria](#success-criteria)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

[↑ Back to top](#table-of-contents)

## Implementation Steps

### Current Structure Analysis

The `add_command()` function (lines 192-244 in `src/spafw37/command.py`) currently handles 8 responsibilities in a single 54-line function:

1. **Name validation** (lines 193-195): Check command name is not empty
2. **Action validation** (lines 196-197): Verify action function exists
3. **Duplicate check** (lines 198-199): Skip if command already registered
4. **Inline param processing** (lines 201-217): Handle `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM` inline definitions
5. **Inline command processing** (lines 219-227): Handle dependency field inline command definitions
6. **Self-reference validation** (lines 229-233): Prevent commands referencing themselves
7. **Conflict validation** (lines 235-240): Check for `GOES_BEFORE`/`GOES_AFTER` conflicts
8. **Phase assignment and storage** (lines 241-245): Set default phase, store in registry, register cycle

### Refactoring Strategy

Extract helpers in this order (simplest to most complex):

1. `_validate_command_name()` - Name validation
2. `_validate_command_action()` - Action validation
3. `_validate_command_references()` - Self-reference and conflict checks
4. `_process_inline_params()` - Inline parameter processing
5. `_process_inline_commands()` - Inline command processing
6. `_assign_command_phase()` - Phase assignment
7. `_store_command()` - Registry storage and cycle registration

### Step 1: Extract validation helpers

Extract the three validation helpers that check command definition properties. These are the simplest extractions with clear boundaries.

**Rationale:** Validation is self-contained with no side effects, making it the safest place to start. Each validation can be extracted and tested independently.

**Test Specifications:**

**Test 1.1: Name validation**

```gherkin
Scenario: Empty command name raises ValueError
  Given a command definition with empty name
  When _validate_command_name() is called
  Then ValueError is raised with "Command name cannot be empty"
  
  # Tests: Name validation enforcement
  # Validates: Helper catches empty/None command names
```

**Test 1.2: Action validation**

```gherkin
Scenario: Missing command action raises ValueError
  Given a command definition without COMMAND_ACTION
  When _validate_command_action() is called
  Then ValueError is raised with "Command action is required"
  
  # Tests: Action validation enforcement
  # Validates: Helper catches missing action functions
```

**Test 1.3: Self-reference validation**

```gherkin
Scenario: Command referencing itself raises ValueError
  Given a command with its own name in COMMAND_GOES_AFTER
  When _validate_command_references() is called
  Then ValueError is raised with "cannot reference itself"
  
  # Tests: Self-reference detection
  # Validates: Helper prevents circular self-references
```

**Test 1.4: Conflicting constraints validation**

```gherkin
Scenario: Conflicting GOES_BEFORE and GOES_AFTER raises ValueError
  Given a command with same name in both GOES_BEFORE and GOES_AFTER
  When _validate_command_references() is called
  Then ValueError is raised with "conflicting constraints"
  
  # Tests: Constraint conflict detection
  # Validates: Helper catches impossible sequencing requirements
```

[Implementation will be added to scratch/step1-validation-helpers.md]

[↑ Back to top](#table-of-contents)

---

### Step 2: Extract inline parameter processing

Extract inline parameter definition processing for `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM` into a single helper.

**Rationale:** This logic is complex but well-isolated. It delegates to `param._register_inline_param()` which already exists, so the extraction mainly reorganises code without changing behaviour.

**Test Specifications:**

**Test 2.1: Inline required params processing**

```gherkin
Scenario: Inline param definitions in COMMAND_REQUIRED_PARAMS are registered
  Given a command with inline param dict in COMMAND_REQUIRED_PARAMS
  When _process_inline_params() is called
  Then param is registered via param._register_inline_param()
  And COMMAND_REQUIRED_PARAMS contains param name string
  
  # Tests: Inline param registration
  # Validates: Helper normalizes dict definitions to name strings
```

**Test 2.2: String param names preserved**

```gherkin
Scenario: String param names in COMMAND_REQUIRED_PARAMS are preserved
  Given a command with string param names in COMMAND_REQUIRED_PARAMS
  When _process_inline_params() is called
  Then COMMAND_REQUIRED_PARAMS remains unchanged
  
  # Tests: String name preservation
  # Validates: Helper doesn't modify already-normalized names
```

**Test 2.3: Inline trigger param processing**

```gherkin
Scenario: Inline param definition in COMMAND_TRIGGER_PARAM is registered
  Given a command with inline param dict in COMMAND_TRIGGER_PARAM
  When _process_inline_params() is called
  Then param is registered via param._register_inline_param()
  And COMMAND_TRIGGER_PARAM contains param name string
  
  # Tests: Trigger param registration
  # Validates: Helper normalizes trigger param definitions
```

[Implementation will be added to scratch/step2-inline-params.md]

[↑ Back to top](#table-of-contents)

---

### Step 3: Extract inline command processing

Extract inline command definition processing for dependency/sequencing fields into a helper.

**Rationale:** Similar to param processing but handles four fields (`COMMAND_GOES_AFTER`, `COMMAND_GOES_BEFORE`, `COMMAND_NEXT_COMMANDS`, `COMMAND_REQUIRE_BEFORE`). Well-isolated with clear inputs/outputs.

**Test Specifications:**

**Test 3.1: Inline command definitions registered**

```gherkin
Scenario: Inline command dicts in dependency fields are registered
  Given a command with inline command dict in COMMAND_REQUIRE_BEFORE
  When _process_inline_commands() is called
  Then inline command is registered via _register_inline_command()
  And field contains command name string
  
  # Tests: Inline command registration
  # Validates: Helper normalizes dict definitions to name strings
```

**Test 3.2: Multiple dependency fields processed**

```gherkin
Scenario: All four dependency fields are processed
  Given a command with inline dicts in all dependency fields
  When _process_inline_commands() is called
  Then all inline commands are registered
  And all fields contain normalized name strings
  
  # Tests: Multi-field processing
  # Validates: Helper handles GOES_AFTER, GOES_BEFORE, NEXT_COMMANDS, REQUIRE_BEFORE
```

**Test 3.3: String command names preserved**

```gherkin
Scenario: String command names in dependency fields are preserved
  Given a command with string names in dependency fields
  When _process_inline_commands() is called
  Then fields remain unchanged
  
  # Tests: String name preservation
  # Validates: Helper doesn't modify already-normalized names
```

[Implementation will be added to scratch/step3-inline-commands.md]

[↑ Back to top](#table-of-contents)

---

### Step 4: Extract phase assignment

Extract default phase assignment logic into a helper.

**Rationale:** Simple single-line operation but conceptually distinct from storage. Making it explicit improves readability.

**Test Specifications:**

**Test 4.1: Default phase assignment**

```gherkin
Scenario: Command without COMMAND_PHASE gets default phase
  Given a command definition without COMMAND_PHASE property
  When _assign_command_phase() is called
  Then COMMAND_PHASE is set to config.get_default_phase()
  
  # Tests: Default phase assignment
  # Validates: Helper assigns default when phase not specified
```

**Test 4.2: Explicit phase preserved**

```gherkin
Scenario: Command with COMMAND_PHASE keeps its value
  Given a command definition with explicit COMMAND_PHASE
  When _assign_command_phase() is called
  Then COMMAND_PHASE value is unchanged
  
  # Tests: Explicit phase preservation
  # Validates: Helper doesn't override explicit phase assignments
```

[Implementation will be added to scratch/step4-phase-assignment.md]

[↑ Back to top](#table-of-contents)

---

### Step 5: Extract command storage

Extract final storage and cycle registration into a helper.

**Rationale:** Separates storage concerns from validation/processing. Groups related operations (registry storage + cycle registration).

**Test Specifications:**

**Test 5.1: Command stored in registry**

```gherkin
Scenario: Command is added to _commands registry
  Given a validated command definition
  When _store_command() is called
  Then command appears in _commands dict with name as key
  
  # Tests: Registry storage
  # Validates: Helper stores command in module registry
```

**Test 5.2: Cycle registration triggered**

```gherkin
Scenario: Command with cycle triggers cycle registration
  Given a command definition with COMMAND_CYCLE
  When _store_command() is called
  Then cycle.register_cycle() is called with command and registry
  
  # Tests: Cycle registration delegation
  # Validates: Helper delegates cycle registration to cycle module
```

**Test 5.3: Integration test - refactored add_command maintains behavior**

```gherkin
Scenario: Refactored add_command produces identical results
  Given the same command definition
  When add_command() is called with refactored helpers
  Then command is registered identically to original implementation
  And all existing tests continue to pass
  
  # Tests: Backward compatibility
  # Validates: Refactoring doesn't change external behavior
```

[Implementation will be added to scratch/step5-storage.md]

[↑ Back to top](#table-of-contents)

---

## Further Considerations

No unresolved questions at this time. The refactoring plan is straightforward:

- All helpers will be private (`_` prefix) - no API changes
- Existing test coverage (44 tests for command module, 95% overall) guards against regression
- Incremental extraction allows running tests after each step
- Pattern already proven successful in issue #15

If questions arise during implementation, they will be documented here.

[↑ Back to top](#table-of-contents)

---

## Success Criteria

[PLACEHOLDER - Will be completed in Step 5]

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

[PLACEHOLDER - Will be completed in Step 6]

[↑ Back to top](#table-of-contents)
