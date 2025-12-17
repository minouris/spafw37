# Issue #15: User Input Params

**GitHub Issue:** https://github.com/minouris/spafw37/issues/15

**Status:** PENDING REVIEW  
**Version:** 1.1.0  
**Branch:** feature/issue-15-user-input-params-1.1.0

---

## Table of Contents

- [Overview](#overview)
- [Success Criteria](#success-criteria)
- [Implementation Plan](#implementation-plan)
  - [Program Flow Analysis](#program-flow-analysis)
  - [Design Questions - Awaiting User Clarification](#design-questions---awaiting-user-clarification)
    - [Q1: Architecture Approach](#q1-architecture-approach)
    - [Q2: Multiple Choice Population](#q2-multiple-choice-population)
    - [Q3: Prompt Timing](#q3-prompt-timing)
    - [Q4: CLI Override Behaviour](#q4-cli-override-behaviour)
    - [Q5: Cycle Behaviour](#q5-cycle-behaviour)
    - [Q6: Validation Integration](#q6-validation-integration)
    - [Q7: User Input Mechanism](#q7-user-input-mechanism)
    - [Q8: Silent/Batch Mode](#q8-silentbatch-mode)
  - [Implementation Steps](#implementation-steps)
    - [Phase 1: Core Infrastructure](#phase-1-core-infrastructure)
    - [Phase 2: Prompt Execution](#phase-2-prompt-execution)
    - [Phase 3: Documentation](#phase-3-documentation)
- [Further Considerations](#further-considerations)
  - [1. Design Pattern Research](#1-design-pattern-research---resolved)
  - [2. Architecture Approach Trade-offs](#2-architecture-approach-trade-offs---resolved)
  - [3. Implementation Complexity Assessment](#3-implementation-complexity-assessment---resolved)
  - [4. User Experience Considerations](#4-user-experience-considerations---resolved)
  - [5. Alternative Solutions](#5-alternative-solutions---resolved)
  - [6. Backward Compatibility and Breaking Changes](#6-backward-compatibility-and-breaking-changes---resolved)
  - [7. Testing Strategy](#7-testing-strategy---resolved)
- [Fixing Regressions](#fixing-regressions)
- [Implementation Plan Changes](#implementation-plan-changes)
- [Documentation Updates](#documentation-updates)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

---

## Overview

Currently, spafw37 requires all parameter values to be provided via command-line arguments or configuration files. This makes the framework unsuitable for interactive workflows where users need to provide input dynamically during execution, such as confirmation prompts, selection from lists, or entering sensitive data that shouldn't appear in command history.

This feature adds interactive prompt support to the parameter system, allowing params to solicit user input at runtime. Prompts integrate with the existing parameter infrastructure, leveraging existing validation, type handling, and required param checking. The implementation uses a param-level architecture where new optional properties control prompt behaviour, keeping the feature opt-in and maintaining backward compatibility.

The solution provides an extensible design with a default handler using Python's built-in `input()` function for regular input and `getpass.getpass()` for sensitive data (passwords, API keys, tokens), whilst allowing custom handlers for advanced use cases such as GUI prompts or API-based input. Prompts can be configured to appear at application start or before specific commands, with fine-grained control over repeat behaviour in cycles. The `PARAM_SENSITIVE` property ensures sensitive values are not echoed to the terminal and default values are not displayed in prompts to prevent credential leakage.

**Key architectural decisions (all resolved):**

- **Architecture approach:** Param-level properties (`PARAM_PROMPT`, `PARAM_PROMPT_HANDLER`, `PARAM_PROMPT_TIMING`, `PARAM_PROMPT_REPEAT`, `PARAM_SENSITIVE`) extend existing param system rather than creating separate structure
- **Extensibility:** Default handler in `input_prompt.py` using `input()` function; customisable via per-param `PARAM_PROMPT_HANDLER` property or global `set_prompt_handler()` method
- **Timing control:** `PARAM_PROMPT_TIMING` property controls when prompts appear (`PROMPT_ON_START` or `PROMPT_ON_COMMAND`); `PROMPT_ON_COMMANDS` property stores list of command names when using `PROMPT_ON_COMMAND` timing; auto-population of `PROMPT_ON_COMMANDS` property from `COMMAND_REQUIRED_PARAMS`; reciprocal `COMMAND_PROMPT_PARAMS` list built automatically on commands for O(1) lookup
- **Inline definitions:** Commands can define prompt params inline in `COMMAND_PROMPT_PARAMS` using dictionary definitions, consistent with `COMMAND_REQUIRED_PARAMS`, `COMMAND_TRIGGER_PARAM`, and dependency fields (see `examples/inline_definitions_basic.py`)
- **CLI integration:** Prompts skipped entirely if param value already set via CLI; no confirmation needed
- **Cycle behaviour:** Unified timing/repeat mechanism using `PARAM_PROMPT_REPEAT` handles both regular commands and cycles
- **Validation:** Uses existing framework validation functions; validates immediately after entry with retry logic and max retry limit
- **Type handling:** Leverages existing `PARAM_TYPE` constants (`PARAM_TYPE_TEXT`, `PARAM_TYPE_NUMBER`, `PARAM_TYPE_TOGGLE`) and `PARAM_ALLOWED_VALUES` for multiple choice
- **Framework integration:** Proceed with implementation—complexity manageable, feature remains opt-in with complexity isolated behind `is_prompt_required()` helper
- **Testing approach:** Use pytest with `monkeypatch` fixture and `StringIO` for stdin mocking (compatible with Python 3.7.9, already used extensively in project)

## Success Criteria

- [ ] `PARAM_PROMPT` constant defined in `constants/param.py`
- [ ] `PARAM_PROMPT_HANDLER` constant defined in `constants/param.py`
- [ ] `PARAM_PROMPT_TIMING` constant defined in `constants/param.py`
- [ ] `PARAM_PROMPT_REPEAT` constant defined in `constants/param.py`
- [ ] `PARAM_SENSITIVE` constant defined in `constants/param.py`
- [ ] `PROMPT_ON_START` constant defined in `constants/param.py`
- [ ] `PROMPT_ON_COMMAND` constant defined in `constants/param.py`
- [ ] `PROMPT_ON_COMMANDS` constant defined in `constants/param.py`
- [ ] `PROMPT_REPEAT_NEVER` constant defined in `constants/param.py`
- [ ] `PROMPT_REPEAT_IF_BLANK` constant defined in `constants/param.py`
- [ ] `PROMPT_REPEAT_ALWAYS` constant defined in `constants/param.py`
- [ ] `COMMAND_PROMPT_PARAMS` constant defined in `constants/command.py`
- [ ] `input_prompt.py` module created with `prompt_for_value()` function
- [ ] `prompt_for_value()` uses `input()` for regular params
- [ ] `prompt_for_value()` uses `getpass.getpass()` for sensitive params
- [ ] `prompt_for_value()` displays numbered options for `PARAM_ALLOWED_VALUES`
- [ ] `prompt_for_value()` validates input immediately with retry logic
- [ ] `_global_prompt_handler` variable added to `param.py`
- [ ] `set_prompt_handler()` function added to `param.py`
- [ ] `_get_prompt_handler()` helper function created
- [ ] Handler resolution follows precedence: param-level → global → default
- [ ] `_prompted_params` set added to track prompt history
- [ ] `_param_value_is_set()` helper function created
- [ ] `_timing_matches_context()` helper function created
- [ ] `_should_prompt_param()` orchestration function created
- [ ] `_should_prompt_param()` respects CLI override (skips if value set)
- [ ] `_should_prompt_param()` handles `PROMPT_ON_START` timing
- [ ] `_should_prompt_param()` handles `PROMPT_ON_COMMAND` timing
- [ ] `_should_prompt_param()` handles `PROMPT_REPEAT_NEVER` behaviour
- [ ] `_should_prompt_param()` handles `PROMPT_REPEAT_IF_BLANK` behaviour
- [ ] `_should_prompt_param()` handles `PROMPT_REPEAT_ALWAYS` behaviour
- [ ] `COMMAND_PROMPT_PARAMS` inline definitions processed in `command.py`
- [ ] `PROMPT_ON_COMMANDS` auto-populated from `COMMAND_REQUIRED_PARAMS`
- [ ] Reciprocal `COMMAND_PROMPT_PARAMS` list built on commands
- [ ] Prompt execution integrated at application start for `PROMPT_ON_START`
- [ ] Prompt execution integrated before command execution for `PROMPT_ON_COMMAND`
- [ ] `set_max_prompt_retries()` function added to `param.py`
- [ ] Max retry enforcement in prompt execution logic
- [ ] `set_allowed_values()` function added to `param.py`
- [ ] Unit tests added for all constants
- [ ] Unit tests added for `prompt_for_value()` function
- [ ] Unit tests added for handler resolution
- [ ] Unit tests added for timing checks
- [ ] Unit tests added for repeat behaviour
- [ ] Unit tests added for CLI override
- [ ] Integration tests added for `PROMPT_ON_START` timing
- [ ] Integration tests added for `PROMPT_ON_COMMAND` timing
- [ ] Integration tests added for all repeat modes
- [ ] Integration tests added for sensitive parameter handling
- [ ] Integration tests added for custom handlers
- [ ] Integration tests added for inline definitions
- [ ] Integration tests added for auto-population
- [ ] Integration tests added for validation retry
- [ ] Integration tests added for max retry enforcement
- [ ] Regression tests added for existing parameter functionality
- [ ] All existing tests still passing
- [ ] Overall test coverage remains above 80%
- [ ] Documentation updated in `doc/parameters.md`
- [ ] API reference updated in `doc/api-reference.md`
- [ ] README.md updated with feature description
- [ ] README.md updated with examples list entry
- [ ] README.md updated with "What's New in v1.1.0" entry
- [ ] Example created in `examples/params_prompt_basic.py`
- [ ] Example created in `examples/params_prompt_timing.py`
- [ ] Example created in `examples/params_prompt_repeat.py`
- [ ] Example created in `examples/params_prompt_sensitive.py`
- [ ] Example created in `examples/params_prompt_choices.py`
- [ ] Example created in `examples/params_prompt_handlers.py`
- [ ] Example created in `examples/params_prompt_validation.py`
- [ ] All examples run without errors
- [ ] Issue #15 closed with reference to implementation

[↑ Back to top](#table-of-contents)

## Implementation Plan

### Program Flow Analysis

#### Current Behaviour (Before Changes)

Parameters are populated exclusively from command-line arguments and configuration files. Values are set during CLI parsing in `cli.py` via `_parse_command_line()`, and required params are validated before command execution. There is no mechanism for interactive user input.

**Standard execution flow:**
1. Application starts → `run_cli()` called in `core.py`
2. CLI parsing → `_parse_command_line()` in `cli.py`
   - Tokenises command line into params and commands
   - Sets param values from CLI arguments
   - Loads config file if specified
3. Param validation → Framework validates required params exist
4. Command execution → Commands run with available param values
5. Result: All param values must be provided upfront; no interactive prompting

#### New Behaviour (After Changes)

Parameters can optionally solicit interactive user input at runtime. Prompts integrate with existing param lifecycle and respect CLI-provided values.

**With PROMPT_ON_START timing:**
1. Application starts → `run_cli()` called in `core.py`
2. CLI parsing → `_parse_command_line()` in `cli.py`
   - Tokenises command line into params and commands
   - Sets param values from CLI arguments
   - Loads config file if specified
3. **NEW:** Prompt phase → After CLI parsing, before command execution
   - Check all params for `PARAM_PROMPT` with `PROMPT_ON_START` timing
   - For each prompt param without existing value (CLI didn't set it):
     - Call prompt handler (default: `input_prompt.py` → `input()`)
     - Validate input immediately using existing validation functions
     - Retry on error up to max retry limit
     - Set param value or exit/set None based on required status
4. Param validation → Framework validates required params exist
5. Command execution → Commands run with param values (prompted or CLI)
6. Result: Users prompted for missing values after CLI parsing; CLI values prevent prompting

**With PROMPT_ON_COMMAND timing:**
1. Application starts → `run_cli()` called in `core.py`
2. CLI parsing → `_parse_command_line()` in `cli.py`
3. Param validation → Framework validates required params exist
4. Command execution begins
5. **NEW:** Before each command execution:
   - Check if command name in param's `PROMPT_ON_COMMANDS` property (list)
   - Check param's `PARAM_PROMPT_REPEAT` setting:
     - `PROMPT_REPEAT_ALWAYS`: Prompt every time (preserves previous value)
     - `PROMPT_REPEAT_IF_BLANK`: Prompt only if value is blank
     - `PROMPT_REPEAT_NEVER`: Prompt only on first occurrence
   - If should prompt and no CLI value set:
     - Call prompt handler
     - Validate input immediately
     - Retry on error up to max retry limit
   - Command executes with param value
6. Result: Users prompted immediately before commands that require values

**With CLI override:**
1. CLI parsing sets param value from `--param-name value`
2. **NEW:** Prompt phase (after CLI parsing) checks if value already set
3. If set: Skip prompt entirely (no confirmation)
4. If not set: Execute prompt as normal
5. Result: CLI arguments prevent prompting; simple and predictable (no duplicate parsing needed)

**Extensibility flow:**
1. Application defines custom prompt handler function
2. **NEW:** Calls `set_prompt_handler(custom_function)` for global override
3. **NEW:** OR sets `PARAM_PROMPT_HANDLER: custom_function` for per-param override
4. During prompt execution:
   - Check param-level `PARAM_PROMPT_HANDLER` first
   - Fall back to global handler if set
   - Fall back to default `input_prompt.py` handler
5. Result: Custom handlers replace or augment default behaviour

### Design Questions - Awaiting User Clarification

**These questions have been posted as individual GitHub comments for threaded responses:**

Implementation cannot proceed without answers to the following design questions:

**Q1: Architecture Approach** ([#issuecomment-3587791402](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791402))

Should user input params be:
- Regular params with additional properties (e.g., `PARAM_PROMPT`, `PARAM_PROMPT_TIMING`)?
- A separate structure entirely (e.g., `INPUT_PROMPTS` at command level)?
- A hybrid approach where params define what can be prompted and commands control when?

**Answer:** See [Further Consideration 2: Architecture Approach Trade-offs](#2-architecture-approach-trade-offs---resolved) - Option A (param-level approach) has been selected.

[↑ Back to top](#table-of-contents)

---

**Q2: Multiple Choice Population** ([#issuecomment-3587791428](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791428))

For multiple choice prompts, how should the list of choices be populated programmatically?
- Via a command (as mentioned in the issue: "Specify command to populate list")?
- Via a callable function in the param definition?
- Via a static list that can be updated at runtime?

If via command: How would a param specify which command to run? This would create a bidirectional dependency between params and commands that doesn't currently exist in the architecture.

**Answer:** Use static list with runtime updates via new public API method `set_allowed_values(param_name, values)`. Multiple choice uses existing `PARAM_ALLOWED_VALUES`. Commands can call this method to populate choices dynamically without creating bidirectional dependencies.

[↑ Back to top](#table-of-contents)

---

**Q3: Prompt Timing** ([#issuecomment-3587791444](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791444))

The issue mentions "at the start of a flow, or immediately before the command is executed."
- Should timing be controlled by the param definition or the command definition?
- What exactly does "immediately before command execution" mean in the context of command queues, dependencies, and phases?
- Should there be a flag on the command (as suggested in the issue)?

**Answer:** Use param-level properties for timing control, with reciprocal lists on commands for efficient lookup.

**Design:**

**Param-side constants:**

`PARAM_PROMPT_TIMING` - Controls when the prompt appears:
- `PROMPT_ON_START`: Prompts immediately after CLI parsing (before command execution)
- `PROMPT_ON_COMMAND`: Prompts before commands (command list specified in `PROMPT_ON_COMMANDS` property)

`PROMPT_ON_COMMANDS` - Property containing list of commands (only used when `PARAM_PROMPT_TIMING` is `PROMPT_ON_COMMAND`):
- List of command name strings: `['deploy', 'delete']`
- Inline command definitions: `[{COMMAND_NAME: 'deploy', ...}]`
- Mixed string/inline: `['deploy', {COMMAND_NAME: 'delete', ...}]`
- Auto-populates from `COMMAND_REQUIRED_PARAMS` if not explicitly set

`PARAM_PROMPT_REPEAT` - Controls repeat behaviour (works with `PROMPT_ON_COMMAND` timing):
- `PROMPT_REPEAT_ALWAYS`: Repeats before every command in `PROMPT_ON_COMMANDS` list. Preserves previous value.
- `PROMPT_REPEAT_IF_BLANK`: Repeats before commands in `PROMPT_ON_COMMANDS` list if the value is blank
- `PROMPT_REPEAT_NEVER`: Never repeat after the first prompt

**Command-side constant:**

`COMMAND_PROMPT_PARAMS` - List of param names that prompt before this command (built automatically during registration):
- Enables O(1) lookup: "which params need prompting before this command executes?"
- Populated from params that have this command in their `PROMPT_ON_COMMANDS` list
- Can be explicitly set with param names (string references) or inline param definitions (dictionaries)
- Inline definitions follow same pattern as `COMMAND_REQUIRED_PARAMS` for API consistency

**Reciprocal list auto-population:**
- When a param is added with `PROMPT_ON_COMMANDS`, those command names are stored on the param
- When a command is added with `COMMAND_REQUIRED_PARAMS`, framework auto-populates `PROMPT_ON_COMMANDS` for matching params (if they have `PARAM_PROMPT` and `PROMPT_ON_COMMANDS` is not explicitly set)
- When a command is added with `COMMAND_PROMPT_PARAMS`, framework processes inline definitions and establishes reciprocal relationships
- Commands build their `COMMAND_PROMPT_PARAMS` list at registration time from params that prompt before them
- This allows efficient lookup: "which params need prompting before this command executes?"

**Rationale:** Param-level approach provides fine-grained control whilst integrating with existing `COMMAND_REQUIRED_PARAMS` structure. Auto-population from `COMMAND_REQUIRED_PARAMS` reduces configuration burden. Reciprocal lists enable efficient command-side lookup without scanning all params. Inline definition support in `COMMAND_PROMPT_PARAMS` maintains API consistency with existing framework patterns.

**Breaking changes:** None (new optional properties only).

**Cross-reference:** Resolves timing aspects of Q5 (Cycle Behaviour).

[↑ Back to top](#table-of-contents)

---

**Q4: CLI Override Behaviour** ([#issuecomment-3587791457](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791457))

If a user input param can also be set on the command line:
- Should the prompt be skipped entirely if the value is provided via CLI?
- Should it display the CLI value and ask for confirmation?
- Does the behaviour differ for required vs optional params?

**Answer:** If param value is already set (via CLI), skip the prompt entirely. Params with aliases can be set by CLI handler. No confirmation needed. Simple and predictable.

[↑ Back to top](#table-of-contents)

---

**Q5: Cycle Behaviour** ([#issuecomment-3587791473](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791473))

For params in cycle commands, the issue mentions three options:
- Pop up to confirm value if set
- Silently pass if value is set
- Make prompting optional

Which behaviour is preferred? How does this interact with loop iterations (should it prompt once before the cycle, or on each iteration)?

**Answer:** Controlled by `PARAM_PROMPT_REPEAT` (see Q3).

**Design:**

Cycle behaviour is handled by the repeat property:
- `PROMPT_REPEAT_ALWAYS`: Prompts before every cycle iteration (can confirm/change value each time, preserves previous)
- `PROMPT_REPEAT_IF_BLANK`: Prompts on first iteration if blank, then uses same value for remaining iterations
- `PROMPT_REPEAT_NEVER`: Prompts once before cycle starts, uses same value for all iterations

Combined with the `PROMPT_ON_COMMANDS` property listing the cycle command name, this provides full control over cycle prompt behaviour.

**Rationale:** Unified timing/repeat mechanism handles both regular commands and cycles without special-case logic.

**Breaking changes:** None.

**Cross-reference:** See Q3 (Prompt Timing) for full timing control details.

[↑ Back to top](#table-of-contents)

---

**Q6: Validation Integration** ([#issuecomment-3587791497](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791497))

The issue states "Not included in validation, as not a command line param" but user input params would still need validation (type checking, allowed values, etc.):
- Should validation happen immediately on user input?
- Should these params participate in required param checking?
- How do they interact with the existing `PARAM_REQUIRED`, `PARAM_ALLOWED_VALUES`, etc.?

**Answer:** Use existing framework validation functions. Validate immediately after entry. Required if `PARAM_REQUIRED: True` OR in `COMMAND_REQUIRED_PARAMS`. Default handling uses bash convention `[default: value]`. Retry logic: re-prompt on error with max retry limit; behaviour on max retry depends on required status (exit if required, set `None` if optional).

[↑ Back to top](#table-of-contents)

---

**Q7: User Input Mechanism** ([#issuecomment-3587791517](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791517))

What should the user input mechanism look like?
- Text: Use Python's `input()` function?
- Boolean: Accept yes/no, y/n, true/false?
- Number: Validate numeric input with retry on error?
- Multiple choice: Display numbered list and accept number input?
- Error handling: Retry on invalid input, abort, or use default?

**Answer:** See [Further Consideration 1: Design Pattern Research](#1-design-pattern-research---resolved) - Use Python's built-in `input()` function as the default handler, with `getpass.getpass()` for sensitive data, and extensibility support.

**Implementation:**
- Default prompt handler implemented in new file `input_prompt.py` using `input()` function for regular input and `getpass.getpass()` for sensitive data
- `PARAM_SENSITIVE` property controls sensitive data handling (suppresses echo and default value display)
- Extensible via `PARAM_PROMPT_HANDLER` property (per-param override) or `set_prompt_handler()` method (global override)
- **Text:** Use `input()` with string return value (or `getpass.getpass()` if `PARAM_SENSITIVE: True`)
- **Boolean:** Accept yes/no, y/n, true/false with case-insensitive matching
- **Number:** Use `input()` with int() or float() conversion, retry on ValueError
- **Multiple choice:** Display numbered list, accept either number or text value
- **Error handling:** Retry on invalid input with clear error message
- **Sensitive data:** Use `getpass.getpass()` for non-echoing input, suppress default value display to prevent credential leakage

**Note:** The `PARAM_SENSITIVE` flag should also be checked when logging parameter values to prevent passwords, API keys, and tokens from appearing in log files.

**Rationale:** Python's built-in `input()` function is simple, requires no dependencies, works on all platforms, and is what most Python CLI tools use. The `getpass` module (also in standard library) provides secure non-echoing input for sensitive data. Extensible design allows custom handlers for advanced use cases (GUI prompts, API-based input, etc.).

[↑ Back to top](#table-of-contents)

---

**Q8: Silent/Batch Mode** ([#issuecomment-3587791532](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791532))

How should prompts interact with existing framework flags?
- Should prompts be suppressed with `--silent`?
- How to disable prompts for automated scripts/batch mode?
- Should there be a `--no-prompts` flag?

**Answer:** Interactive prompts are incompatible with batch/automated execution by design. If a required param with `PARAM_PROMPT` is not provided via CLI or config, the existing "missing required param" validation error will occur naturally. No special handling needed.

**Note:** `--silent` suppresses console logging output, not interactive prompts. Some prompt timing/repeat configurations will simply not work in automated/batch scenarios - this is expected behaviour.

[↑ Back to top](#table-of-contents)

---

### Implementation Steps

Now that all design decisions are resolved, implementation follows a test-driven approach where each component is tested as it's built. Tests are interleaved with implementation to ensure incremental validation.

#### Phase 1: Core Infrastructure

**Step 1: Add prompt constants**

**Files:** `src/spafw37/constants/param.py`, `src/spafw37/constants/command.py`

Add new constants for prompt configuration in param.py and command.py modules.

**Implementation order:**

1. Add param-level prompt property constants to `param.py`
2. Add timing control constants to `param.py`
3. Add repeat behaviour constants to `param.py`
4. Add command reciprocal list constant to `command.py`
5. Verify no constant value collisions within each module

**Tests for Step 1: Prompt constants**

Module-level imports for `tests/test_constants.py`:
```python
# Module-level imports for tests/test_constants.py
from spafw37.constants import param, command
```

**Code 1.1.1: Param prompt property constants**

```python
# Block 1.1.1: Add to src/spafw37/constants/param.py
PARAM_PROMPT = 'prompt'  # Prompt text to display to user
PARAM_PROMPT_HANDLER = 'prompt-handler'  # Custom handler function for this param
PARAM_PROMPT_TIMING = 'prompt-timing'  # When to display prompt (constant or list)
PARAM_PROMPT_REPEAT = 'prompt-repeat'  # Repeat behaviour for cycles/multiple commands
PARAM_SENSITIVE = 'sensitive'  # Boolean: suppress echo and default display for sensitive data
```

**Test 1.1.2: Tests for param prompt constants definition**

```gherkin
Scenario: All PARAM_PROMPT* and PARAM_SENSITIVE constants are defined in param constants module
  Given the param constants module is imported
  When checking for PARAM_PROMPT, PARAM_PROMPT_HANDLER, PARAM_PROMPT_TIMING, PARAM_PROMPT_REPEAT, PARAM_SENSITIVE
  Then all constants are defined as string keys
  And each constant has a unique value
  
  # Tests: Constant definition completeness
  # Validates: All param-level prompt properties have corresponding constants
```

```python
# Test 1.1.2: Add to tests/test_constants.py
def test_param_prompt_constants_exist():
    """Test that all PARAM_PROMPT* and PARAM_SENSITIVE constants required for prompt configuration are defined.
    
    This test verifies that PARAM_PROMPT, PARAM_PROMPT_HANDLER, PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT, and PARAM_SENSITIVE constants exist as strings with unique values.
    This behaviour is expected because these constants form the core vocabulary for
    configuring interactive prompts on parameters and must be available for param definitions."""
    # Block 1.1.2.1: Check all five prompt property constants exist
    assert hasattr(param, 'PARAM_PROMPT'), "PARAM_PROMPT constant missing"
    assert hasattr(param, 'PARAM_PROMPT_HANDLER'), "PARAM_PROMPT_HANDLER constant missing"
    assert hasattr(param, 'PARAM_PROMPT_TIMING'), "PARAM_PROMPT_TIMING constant missing"
    assert hasattr(param, 'PARAM_PROMPT_REPEAT'), "PARAM_PROMPT_REPEAT constant missing"
    assert hasattr(param, 'PARAM_SENSITIVE'), "PARAM_SENSITIVE constant missing"
    
    # Block 1.1.2.2: Verify all are strings (required for dict keys)
    assert isinstance(param.PARAM_PROMPT, str), "PARAM_PROMPT must be string"
    assert isinstance(param.PARAM_PROMPT_HANDLER, str), "PARAM_PROMPT_HANDLER must be string"
    assert isinstance(param.PARAM_PROMPT_TIMING, str), "PARAM_PROMPT_TIMING must be string"
    assert isinstance(param.PARAM_PROMPT_REPEAT, str), "PARAM_PROMPT_REPEAT must be string"
    assert isinstance(param.PARAM_SENSITIVE, str), "PARAM_SENSITIVE must be string"
    
    # Block 1.1.2.3: Verify all values are unique
    constant_values = [
        param.PARAM_PROMPT,
        param.PARAM_PROMPT_HANDLER,
        param.PARAM_PROMPT_TIMING,
        param.PARAM_PROMPT_REPEAT,
        param.PARAM_SENSITIVE
    ]
    assert len(constant_values) == len(set(constant_values)), "Constant values must be unique"
```

**Code 1.2.1: Timing control constants**

```python
# Block 1.2.1: Add to src/spafw37/constants/param.py
PROMPT_ON_START = 'on-start'  # Prompt after CLI parsing, before command execution
PROMPT_ON_COMMAND = 'on-command'  # Prompt before commands (list in PROMPT_ON_COMMANDS property)
```

**Test 1.2.2: Tests for timing control constants**

```gherkin
Scenario: All PROMPT_* timing constants are defined with correct values
  Given the param constants module is imported
  When checking for PROMPT_ON_START and PROMPT_ON_COMMAND
  Then both constants are defined
  And PROMPT_ON_START is a string constant
  And PROMPT_ON_COMMAND is a string constant
  And values are distinct from each other
  
  # Tests: Timing constant definition
  # Validates: Timing options have proper constant values for comparison logic
```

```python
# Test 1.2.2: Add to tests/test_constants.py
def test_prompt_timing_constants_exist():
    """Test that timing control constants PROMPT_ON_START and PROMPT_ON_COMMAND are defined.
    
    This test verifies both constants exist as strings with distinct values for use in
    PARAM_PROMPT_TIMING configurations.
    This behaviour is expected because timing options require proper constants for comparison
    logic throughout the codebase to determine when prompts should appear."""
    # Block 1.2.2.1: Check both timing constants exist
    assert hasattr(param, 'PROMPT_ON_START'), "PROMPT_ON_START constant missing"
    assert hasattr(param, 'PROMPT_ON_COMMAND'), "PROMPT_ON_COMMAND constant missing"
    
    # Block 1.2.2.2: Verify both are strings
    assert isinstance(param.PROMPT_ON_START, str), "PROMPT_ON_START must be string"
    assert isinstance(param.PROMPT_ON_COMMAND, str), "PROMPT_ON_COMMAND must be string"
    
    # Block 1.2.2.3: Verify values are distinct
    assert param.PROMPT_ON_START != param.PROMPT_ON_COMMAND, "Timing constants must have distinct values"
```

**Code 1.3.1: Repeat behaviour constants**

```python
# Block 1.3.1: Add to src/spafw37/constants/param.py
PROMPT_REPEAT_ALWAYS = 'always'  # Prompt every time, preserve previous value
PROMPT_REPEAT_IF_BLANK = 'if-blank'  # Prompt only if value is blank
PROMPT_REPEAT_NEVER = 'never'  # Never repeat after first prompt
```

**Test 1.3.2: Tests for repeat behaviour constants**

```gherkin
Scenario: All PROMPT_REPEAT_* constants are defined with distinct values
  Given the param constants module is imported
  When checking for PROMPT_REPEAT_ALWAYS, PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_NEVER
  Then all three constants are defined
  And each constant is a string
  And all three values are unique
  
  # Tests: Repeat behaviour constant definition
  # Validates: All repeat options have proper constants for cycle control logic
```

```python
# Test 1.3.2: Add to tests/test_constants.py
def test_prompt_repeat_constants_exist():
    """Test that all PROMPT_REPEAT_* constants controlling cycle behaviour are defined.
    
    This test verifies PROMPT_REPEAT_ALWAYS, PROMPT_REPEAT_IF_BLANK, and PROMPT_REPEAT_NEVER
    constants exist as strings with unique values.
    This behaviour is expected because repeat options must have proper constants for cycle
    control logic to determine whether prompts should repeat on subsequent iterations."""
    # Block 1.3.2.1: Check all three repeat constants exist
    assert hasattr(param, 'PROMPT_REPEAT_ALWAYS'), "PROMPT_REPEAT_ALWAYS constant missing"
    assert hasattr(param, 'PROMPT_REPEAT_IF_BLANK'), "PROMPT_REPEAT_IF_BLANK constant missing"
    assert hasattr(param, 'PROMPT_REPEAT_NEVER'), "PROMPT_REPEAT_NEVER constant missing"
    
    # Block 1.3.2.2: Verify all are strings
    assert isinstance(param.PROMPT_REPEAT_ALWAYS, str), "PROMPT_REPEAT_ALWAYS must be string"
    assert isinstance(param.PROMPT_REPEAT_IF_BLANK, str), "PROMPT_REPEAT_IF_BLANK must be string"
    assert isinstance(param.PROMPT_REPEAT_NEVER, str), "PROMPT_REPEAT_NEVER must be string"
    
    # Block 1.3.2.3: Verify all three values are unique
    repeat_values = [
        param.PROMPT_REPEAT_ALWAYS,
        param.PROMPT_REPEAT_IF_BLANK,
        param.PROMPT_REPEAT_NEVER
    ]
    assert len(repeat_values) == len(set(repeat_values)), "Repeat constant values must be unique"
```

**Code 1.3.3: Param-level retry count constant**

```python
# Block 1.3.3: Add to src/spafw37/constants/param.py after PROMPT_REPEAT constants
PARAM_PROMPT_RETRIES = 'prompt-retries'  # Per-param retry count override
```

**Test 1.3.4: Test for PARAM_PROMPT_RETRIES constant**

```gherkin
Scenario: PARAM_PROMPT_RETRIES constant is defined
  Given the param constants module
  When checking for PARAM_PROMPT_RETRIES
  Then the constant is defined as a string
  And the value is 'prompt-retries'
  
  # Tests: Constant definition
  # Validates: Param-level retry count configuration available
```

```python
# Test 1.3.4: Add to tests/test_constants.py
def test_param_prompt_retries_constant():
    """Test that PARAM_PROMPT_RETRIES constant is defined correctly.
    
    This test verifies the constant exists as a string for use in param definitions.
    This behaviour is expected because params need to override global retry configuration
    on a per-param basis for sensitive or critical parameters."""
    from spafw37.constants.param import PARAM_PROMPT_RETRIES
    assert PARAM_PROMPT_RETRIES == 'prompt-retries'
```

**Code 1.4.1: Command reciprocal list constant**

```python
# Block 1.4.1: Add to src/spafw37/constants/command.py
COMMAND_PROMPT_PARAMS = 'prompt-params'  # List of param names that prompt before this command
```

**Test 1.4.2: Tests for command prompt params constant**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS constant defined in command constants module
  Given the command constants module is imported
  When checking for COMMAND_PROMPT_PARAMS
  Then the constant is defined as a string key
  And the value is unique within command constants
  
  # Tests: Command reciprocal list constant
  # Validates: Commands can store list of params that prompt before them
```

```python
# Test 1.4.2: Add to tests/test_constants.py
def test_command_prompt_params_constant_exists():
    """Test that COMMAND_PROMPT_PARAMS constant is defined in the command constants module.
    
    This test verifies the constant exists as a string key suitable for use as a dictionary
    property on command definitions.
    This behaviour is expected because commands need to store lists of parameter names that
    should prompt before execution, enabling O(1) lookup during command execution."""
    # Block 1.4.2.1: Check constant exists
    assert hasattr(command, 'COMMAND_PROMPT_PARAMS'), "COMMAND_PROMPT_PARAMS constant missing"
    
    # Block 1.4.2.2: Verify it's a string (required for dict key)
    assert isinstance(command.COMMAND_PROMPT_PARAMS, str), "COMMAND_PROMPT_PARAMS must be string"
```

[↑ Back to top](#table-of-contents)

---

**Step 2: Create default input handler module**

**File:** `src/spafw37/input_prompt.py`

Implement default prompt handler using Python's `input()` function with support for text, number, toggle, and multiple choice inputs.

**Implementation order:**

1. Import required constants from `constants/param.py`
2. Implement prompt text formatting with default value display
3. Implement text input handler (simplest case)
4. Implement number input handler with int/float conversion
5. Implement toggle input handler with multiple accepted formats
6. Implement multiple choice handler with numbered list display
7. Add EOF handling for non-interactive environments

**Code 2.1.1: Module docstring and imports**

```python
# Block 2.1.1: Create new file src/spafw37/input_prompt.py
"""Default interactive prompt handler using Python's built-in input() function.

This module provides the default implementation for soliciting user input
at runtime for params configured with PARAM_PROMPT. The handler supports
text, number, toggle, and multiple choice inputs with proper type conversion
and default value handling.
"""

from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_DEFAULT,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_ALLOWED_VALUES
)
```

**Code 2.2.1: Format prompt text with default**

```python
# Block 2.2.1: Add to src/spafw37/input_prompt.py
def _format_prompt_text(param_def):
    """Format prompt text with default value in bash convention.
    
    Sensitive params (PARAM_SENSITIVE=True) do not display default values
    to prevent credential leakage in terminal history or screen capture.
    
    Args:
        param_def: Parameter definition dictionary.
        
    Returns:
        Formatted prompt string with [default: value] if default exists and not sensitive.
    """
    # Block 2.2.1.1: Get prompt text from param definition
    prompt_text = param_def.get(PARAM_PROMPT, 'Enter value')
    
    # Block 2.2.1.2: Check if param is sensitive (security)
    is_sensitive = param_def.get(PARAM_SENSITIVE, False)
    
    # Block 2.2.1.3: Add default value indicator if present and not sensitive
    default_value = param_def.get(PARAM_DEFAULT)
    if default_value is not None and not is_sensitive:
        prompt_text = "{0} [default: {1}]".format(prompt_text, default_value)
    
    # Block 2.2.1.4: Add trailing space for user input
    return "{0}: ".format(prompt_text)
```

Module-level imports for `tests/test_input_prompt.py`:
```python
# Module-level imports for tests/test_input_prompt.py
from io import StringIO
import pytest
from spafw37 import input_prompt
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_DEFAULT,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_ALLOWED_VALUES,
    PARAM_SENSITIVE
)
```

**Test 2.2.2: Tests for prompt text formatting with default value**

```gherkin
Scenario: Default value shown in prompt text using bash convention
  Given a param with PARAM_DEFAULT "example_default"
  When prompt text is formatted
  Then prompt includes "[default: example_default]"
  And format follows bash convention style
  
  # Tests: Default value display formatting
  # Validates: Users see what default will be used if they press enter
```

```python
# Test 2.2.2: Add to tests/test_input_prompt.py
def test_format_prompt_text_with_default():
    """Test that prompt text formatting includes default values using bash convention.
    
    This test verifies that when a parameter has PARAM_DEFAULT set, the formatted prompt
    displays "[default: value]" following standard bash/Unix prompt conventions.
    This behaviour is expected because users need clear indication of what value will be
    used if they press Enter without typing, matching familiar command-line tool patterns."""
    # Block 2.2.2.1: Create param with default value
    param_def = {
        PARAM_DEFAULT: 'example_default',
        PARAM_PROMPT: 'Enter text'
    }
    
    # Block 2.2.2.2: Format prompt text
    formatted_text = input_prompt._format_prompt_text(param_def)
    
    # Block 2.2.2.3: Verify bash convention format
    assert '[default: example_default]' in formatted_text, "Default value not displayed"
    assert formatted_text == 'Enter text [default: example_default]: ', "Format incorrect"
```

**Test 2.2.3: Tests for sensitive param without default display**

```gherkin
Scenario: Sensitive param does not display default value
  Given a param with PARAM_SENSITIVE=True and PARAM_DEFAULT set
  When prompt text is formatted
  Then prompt does NOT include "[default: ...]"
  And only shows prompt text with colon and space
  
  # Tests: Security - prevent credential leakage via default display
  # Validates: Sensitive params hide defaults from terminal output
```

```python
# Test 2.2.3: Add to tests/test_input_prompt.py
def test_format_prompt_text_sensitive_hides_default():
    """Test that sensitive params do not display default values in prompt text.
    
    This test verifies that when a parameter has PARAM_SENSITIVE=True, the formatted
    prompt does not include "[default: value]" even if PARAM_DEFAULT is set.
    This behaviour is expected because displaying default values for passwords, API keys,
    or other sensitive data in terminal output creates security risks (screen capture,
    terminal history, shoulder surfing). The default will still be used if user presses
    Enter, but it won't be visible."""
    # Block 2.2.3.1: Create sensitive param with default value
    param_def = {
        PARAM_PROMPT: 'API Key',
        PARAM_DEFAULT: 'secret_key_123',
        PARAM_SENSITIVE: True
    }
    
    # Block 2.2.3.2: Format prompt text
    formatted_text = input_prompt._format_prompt_text(param_def)
    
    # Block 2.2.3.3: Verify default not displayed
    assert '[default:' not in formatted_text, "Default should not be displayed for sensitive param"
    assert 'secret_key_123' not in formatted_text, "Sensitive value should not appear in prompt"
    assert formatted_text == 'API Key: ', "Format should be prompt text with colon only"
```

**Code 2.3.1: Handle text input**

```python
# Block 2.3.1: Add to src/spafw37/input_prompt.py
from getpass import getpass

def _handle_text_input(param_def, prompt_text):
    """Handle text input type with sensitive data support.
    
    Uses getpass.getpass() for sensitive params (no echo) and input() for regular params.
    
    Args:
        param_def: Parameter definition dictionary.
        prompt_text: Formatted prompt text to display.
        
    Returns:
        User input string or default value if blank.
    """
    # Block 2.3.1.1: Check if param is sensitive
    is_sensitive = param_def.get(PARAM_SENSITIVE, False)
    
    # Block 2.3.1.2: Get user input with appropriate function
    if is_sensitive:
        user_input = getpass(prompt_text)
    else:
        user_input = input(prompt_text)
    
    # Block 2.3.1.3: Return user input if not blank
    if user_input.strip():
        return user_input.strip()
    
    # Block 2.3.1.4: Return default if blank input
    return param_def.get(PARAM_DEFAULT)
```

**Test 2.3.2: Tests for text input handling**

```gherkin
Scenario: Text input handler returns user-entered string
  Given a param with PARAM_TYPE_TEXT and no default value
  And stdin is mocked with StringIO("test value\n")
  When prompt_for_value() is called
  Then the function returns "test value"
  
  # Tests: Basic text input handling with input() function
  # Validates: String input is captured and returned correctly
```

```python
# Test 2.3.2: Add to tests/test_input_prompt.py
def test_prompt_text_input_returns_string(monkeypatch):
    """Test that the default prompt handler captures plain text input from users.
    
    This test verifies that when stdin is mocked with StringIO containing "test value",
    the prompt_for_value() function returns exactly that string without modification.
    This behaviour is expected because text parameters are the simplest type and should
    return user input verbatim, establishing the foundation for all other input types."""
    # Block 2.3.2.1: Create param definition for text input
    param_def = {
        PARAM_NAME: 'test_param',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    
    # Block 2.3.2.2: Mock stdin with test input
    mock_stdin = StringIO("test value\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.3.2.3: Call prompt handler
    user_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.3.2.4: Verify returned value
    assert user_value == "test value", "Expected 'test value', got '{0}'".format(user_value)
```

**Test 2.3.3: Tests for blank input with default value**

```gherkin
Scenario: Blank input with default value returns the default
  Given a param with PARAM_TYPE_TEXT and PARAM_DEFAULT "default_value"
  And stdin is mocked with StringIO("\n")
  When prompt_for_value() is called
  Then the function returns "default_value"
  
  # Tests: Default value handling for text input
  # Validates: Blank input selects default using bash convention
```

```python
# Test 2.3.3: Add to tests/test_input_prompt.py
def test_prompt_text_with_default_blank_input(monkeypatch):
    """Test that pressing Enter without typing selects the default value automatically.
    
    This test verifies that when stdin is mocked with just a newline character and
    PARAM_DEFAULT is set, the function returns the default value.
    This behaviour is expected because the bash convention of showing "[default: value]"
    implies that blank input (just pressing Enter) will use that default value."""
    # Block 2.3.3.1: Create param with default value
    param_def = {
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'default_value'
    }
    
    # Block 2.3.3.2: Mock stdin with blank input (just newline)
    mock_stdin = StringIO("\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.3.3.3: Call prompt handler
    user_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.3.3.4: Verify default value returned
    assert user_value == 'default_value', "Expected 'default_value', got '{0}'".format(user_value)
```

**Test 2.3.4: Tests for sensitive param uses getpass**

```gherkin
Scenario: Sensitive parameter uses getpass for non-echoing input
  Given a param with PARAM_TYPE_TEXT and PARAM_SENSITIVE True
  And getpass.getpass is mocked to return "secret123"
  When prompt_for_value() is called
  Then getpass.getpass was called (not input())
  And the function returns "secret123"
  
  # Tests: Sensitive parameter input handling
  # Validates: getpass.getpass() used instead of input() for non-echoing input
```

```python
# Test 2.3.4: Add to tests/test_input_prompt.py
def test_prompt_sensitive_param_uses_getpass(monkeypatch):
    """Test that sensitive parameters use getpass.getpass() for non-echoing input.
    
    This test verifies that when PARAM_SENSITIVE is True, the handler calls getpass.getpass()
    instead of input() to prevent keystrokes from being echoed to the terminal.
    This behaviour is expected for security reasons - passwords, API keys, and tokens should not
    be visible on screen or in terminal logs."""
    # Block 2.3.4.1: Create sensitive param
    param_def = {
        PARAM_PROMPT: 'Password',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_SENSITIVE: True
    }
    
    # Block 2.3.4.2: Mock getpass to return test value
    getpass_called = []
    def mock_getpass(prompt_text):
        getpass_called.append(prompt_text)
        return "secret123"
    monkeypatch.setattr('getpass.getpass', mock_getpass)
    
    # Block 2.3.4.3: Call prompt handler
    user_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.3.4.4: Verify getpass was called
    assert len(getpass_called) == 1, "getpass should have been called once"
    assert user_value == "secret123", "Expected 'secret123', got '{0}'".format(user_value)
```

**Test 2.3.5: Tests for sensitive param suppresses default value display**

```gherkin
Scenario: Sensitive parameter with default does not display default in prompt
  Given a param with PARAM_TYPE_TEXT, PARAM_SENSITIVE True, and PARAM_DEFAULT "old_key"
  And getpass.getpass is mocked
  When prompt text is formatted
  Then the prompt does NOT contain "[default: old_key]"
  And the prompt is just "API Key: "
  
  # Tests: Default value suppression for sensitive parameters
  # Validates: Prevents credential leakage by not displaying default values in prompts
```

```python
# Test 2.3.5: Add to tests/test_input_prompt.py
def test_prompt_sensitive_param_suppresses_default_display(monkeypatch):
    """Test that sensitive parameters do not display default values in prompt text.
    
    This test verifies that when PARAM_SENSITIVE is True and PARAM_DEFAULT is set,
    the formatted prompt text does NOT include the '[default: value]' suffix.
    This behaviour is expected for security reasons - displaying default passwords or API keys
    in the prompt would leak credentials in terminal logs, screen recordings, or observed screens."""
    # Block 2.3.5.1: Create sensitive param with default
    param_def = {
        PARAM_PROMPT: 'API Key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_SENSITIVE: True,
        PARAM_DEFAULT: 'old_secret_key_12345'
    }
    
    # Block 2.3.5.2: Mock getpass
    getpass_called = []
    def mock_getpass(prompt_text):
        getpass_called.append(prompt_text)
        return ""
    monkeypatch.setattr('getpass.getpass', mock_getpass)
    
    # Block 2.3.5.3: Call prompt handler to trigger prompt text formatting
    input_prompt.prompt_for_value(param_def)
    
    # Block 2.3.5.4: Verify default not in prompt text
    prompt_text = getpass_called[0]
    assert '[default:' not in prompt_text, "Sensitive param must not display default value"
    assert 'old_secret_key_12345' not in prompt_text, "Credential leaked in prompt text"
    assert prompt_text == 'API Key: ', "Expected 'API Key: ', got '{0}'".format(prompt_text)
```

**Code 2.4.1: Handle number input**

```python
# Block 2.4.1: Add to src/spafw37/input_prompt.py
def _handle_number_input(param_def, user_input):
    """Handle number input with int/float conversion.
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        
    Returns:
        Converted number (int or float) or default value if blank.
        
    Raises:
        ValueError: If input cannot be converted to number.
    """
    # Block 2.4.1.1: Return default if blank input
    if not user_input.strip():
        return param_def.get(PARAM_DEFAULT)
    
    # Block 2.4.1.2: Try integer conversion first
    try:
        return int(user_input)
    except ValueError:
        pass
    
    # Block 2.4.1.3: Fall back to float conversion
    return float(user_input)
```

**Test 2.4.2: Tests for number integer input conversion**

```gherkin
Scenario: Valid integer input converted correctly
  Given a param with PARAM_TYPE_NUMBER
  And stdin is mocked with StringIO("42\n")
  When prompt_for_value() is called
  Then the function returns 42 as integer
  And no conversion errors occur
  
  # Tests: Number input with integer conversion
  # Validates: Integer strings converted to int type
```

```python
# Test 2.4.2: Add to tests/test_input_prompt.py
def test_prompt_number_integer_valid(monkeypatch):
    """Test that integer input is correctly converted to int type for numeric parameters.
    
    This test verifies that when a user enters "42" for a PARAM_TYPE_NUMBER parameter,
    the handler converts it to the integer 42 (not string or float).
    This behaviour is expected because integer input (no decimal point) should be
    converted using int() for proper numeric operations, counters, and array indices."""
    # Block 2.4.2.1: Create param definition for number input
    param_def = {
        PARAM_PROMPT: 'Enter number',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    
    # Block 2.4.2.2: Mock stdin with integer input
    mock_stdin = StringIO("42\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.4.2.3: Call prompt handler
    result_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.4.2.4: Verify integer type and value
    assert isinstance(result_value, int), "Expected int type, got {0}".format(type(result_value))
    assert result_value == 42, "Expected 42, got {0}".format(result_value)
```

**Test 2.4.3: Tests for number float input conversion**

```gherkin
Scenario: Valid float input converted correctly
  Given a param with PARAM_TYPE_NUMBER  
  And stdin is mocked with StringIO("3.14\n")
  When prompt_for_value() is called
  Then the function returns 3.14 as float
  And no conversion errors occur
  
  # Tests: Number input with float conversion
  # Validates: Float strings converted to float type
```

```python
# Test 2.4.3: Add to tests/test_input_prompt.py
def test_prompt_number_float_valid(monkeypatch):
    """Test that floating-point input is correctly converted to float type for numeric parameters.
    
    This test verifies that when a user enters "3.14" for a PARAM_TYPE_NUMBER parameter,
    the handler converts it to the float 3.14 (not string or integer).
    This behaviour is expected because float input (contains decimal point) should be
    converted using float() for precise measurements, percentages, and scientific values."""
    # Block 2.4.3.1: Create param definition for number input
    param_def = {
        PARAM_PROMPT: 'Enter number',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    
    # Block 2.4.3.2: Mock stdin with float input
    mock_stdin = StringIO("3.14\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.4.3.3: Call prompt handler
    result_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.4.3.4: Verify float type and value
    assert isinstance(result_value, float), "Expected float type, got {0}".format(type(result_value))
    assert result_value == 3.14, "Expected 3.14, got {0}".format(result_value)
```

**Test 2.4.4: Tests for number invalid input validation**

```gherkin
Scenario: Invalid number input raises ValueError
  Given a param with PARAM_TYPE_NUMBER
  And stdin is mocked with StringIO("not_a_number\n")
  When prompt_for_value() is called
  Then ValueError is raised
  And error message indicates conversion failure
  
  # Tests: Number input validation
  # Validates: Non-numeric input rejected with clear error
```

```python
# Test 2.4.4: Add to tests/test_input_prompt.py
def test_prompt_number_invalid_raises_error(monkeypatch):
    """Test that non-numeric input raises ValueError for numeric parameters.
    
    This test verifies that when a user enters "not_a_number" for a PARAM_TYPE_NUMBER parameter,
    the handler raises ValueError rather than returning invalid data.
    This behaviour is expected because type conversion failures must be caught and reported
    clearly, enabling retry logic at higher levels to prompt the user again."""
    # Block 2.4.4.1: Create param definition for number input
    param_def = {
        PARAM_PROMPT: 'Enter number',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    
    # Block 2.4.4.2: Mock stdin with invalid input
    mock_stdin = StringIO("not_a_number\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.4.4.3: Verify ValueError raised
    with pytest.raises(ValueError):
        input_prompt.prompt_for_value(param_def)
```

**Code 2.5.1: Handle toggle input**

```python
# Block 2.5.1: Add to src/spafw37/input_prompt.py
def _handle_toggle_input(param_def, user_input):
    """Handle toggle (boolean) input with multiple accepted formats.
    
    Accepts: y/yes/true (case-insensitive) for True
             n/no/false (case-insensitive) for False
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        
    Returns:
        Boolean value or default value if blank.
        
    Raises:
        ValueError: If input is not a recognized boolean format.
    """
    # Block 2.5.1.1: Return default if blank input
    if not user_input.strip():
        return param_def.get(PARAM_DEFAULT)
    
    # Block 2.5.1.2: Normalize input to lowercase for comparison
    normalized_input = user_input.strip().lower()
    
    # Block 2.5.1.3: Check affirmative values
    if normalized_input in ('y', 'yes', 'true'):
        return True
    
    # Block 2.5.1.4: Check negative values
    if normalized_input in ('n', 'no', 'false'):
        return False
    
    # Block 2.5.1.5: Raise error for unrecognized format
    raise ValueError("Expected y/yes/true or n/no/false")
```

**Test 2.5.2: Tests for toggle affirmative input variations**

```gherkin
Scenario: Toggle input accepts multiple affirmative formats
  Given a param with PARAM_TYPE_TOGGLE
  And stdin provides "y", "Y", "yes", "YES", "true", "True" in sequence
  When prompt_for_value() is called for each input
  Then all return True boolean value
  And case-insensitive matching works correctly
  
  # Tests: Toggle input affirmative value recognition
  # Validates: Multiple formats accepted for true/yes values
```

```python
# Test 2.5.2: Add to tests/test_input_prompt.py
def test_prompt_toggle_yes_variations(monkeypatch):
    """Test that toggle parameters accept multiple affirmative formats with case-insensitive matching.
    
    This test verifies that inputs "y", "Y", "yes", "YES", "true", and "True" all return
    the Python boolean True for PARAM_TYPE_TOGGLE parameters.
    This behaviour is expected because providing flexible, user-friendly input options
    improves usability rather than forcing users to remember exact format requirements."""
    # Block 2.5.2.1: Create param definition for toggle input
    param_def = {
        PARAM_PROMPT: 'Confirm?',
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    }
    
    # Block 2.5.2.2: Test all affirmative variations
    affirmative_inputs = ['y', 'Y', 'yes', 'YES', 'true', 'True']
    for test_input in affirmative_inputs:
        mock_stdin = StringIO("{0}\n".format(test_input))
        monkeypatch.setattr('sys.stdin', mock_stdin)
        result_value = input_prompt.prompt_for_value(param_def)
        assert result_value is True, "Input '{0}' should return True".format(test_input)
```

**Test 2.5.3: Tests for toggle negative input variations**

```gherkin
Scenario: Toggle input accepts multiple negative formats
  Given a param with PARAM_TYPE_TOGGLE
  And stdin provides "n", "N", "no", "NO", "false", "False" in sequence  
  When prompt_for_value() is called for each input
  Then all return False boolean value
  And case-insensitive matching works correctly
  
  # Tests: Toggle input negative value recognition
  # Validates: Multiple formats accepted for false/no values
```

```python
# Test 2.5.3: Add to tests/test_input_prompt.py
def test_prompt_toggle_no_variations(monkeypatch):
    """Test that toggle parameters accept multiple negative formats with case-insensitive matching.
    
    This test verifies that inputs "n", "N", "no", "NO", "false", and "False" all return
    the Python boolean False for PARAM_TYPE_TOGGLE parameters.
    This behaviour is expected because comprehensive support for common negative variations
    provides a complete and intuitive toggle input experience."""
    # Block 2.5.3.1: Create param definition for toggle input
    param_def = {
        PARAM_PROMPT: 'Confirm?',
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    }
    
    # Block 2.5.3.2: Test all negative variations
    negative_inputs = ['n', 'N', 'no', 'NO', 'false', 'False']
    for test_input in negative_inputs:
        mock_stdin = StringIO("{0}\n".format(test_input))
        monkeypatch.setattr('sys.stdin', mock_stdin)
        result_value = input_prompt.prompt_for_value(param_def)
        assert result_value is False, "Input '{0}' should return False".format(test_input)
```

**Test 2.5.4: Tests for toggle invalid input validation**

```gherkin
Scenario: Invalid toggle input raises ValueError
  Given a param with PARAM_TYPE_TOGGLE
  And stdin is mocked with StringIO("maybe\n")
  When prompt_for_value() is called
  Then ValueError is raised
  And error message indicates expected formats
  
  # Tests: Toggle input validation
  # Validates: Unrecognized input rejected with helpful error
```

```python
# Test 2.5.4: Add to tests/test_input_prompt.py
def test_prompt_toggle_invalid_raises_error(monkeypatch):
    """Test that unrecognized input raises ValueError for toggle parameters.
    
    This test verifies that when a user enters "maybe" for a PARAM_TYPE_TOGGLE parameter,
    the handler raises ValueError with a clear message about expected formats.
    This behaviour is expected because ambiguous or invalid input must be rejected,
    enabling retry logic to prompt the user again with guidance on valid options."""
    # Block 2.5.4.1: Create param definition for toggle input
    param_def = {
        PARAM_PROMPT: 'Confirm?',
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    }
    
    # Block 2.5.4.2: Mock stdin with invalid input
    mock_stdin = StringIO("maybe\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.5.4.3: Verify ValueError raised with helpful message
    with pytest.raises(ValueError, match="Expected y/yes/true or n/no/false"):
        input_prompt.prompt_for_value(param_def)
```

**Code 2.6.1: Handle multiple choice input**

```python
# Block 2.6.1: Add to src/spafw37/input_prompt.py
def _handle_multiple_choice_input(param_def, user_input, allowed_values):
    """Handle multiple choice input with numeric or text selection.
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        allowed_values: List of allowed string values.
        
    Returns:
        Selected value from allowed_values or default if blank.
        
    Raises:
        ValueError: If input is not valid selection (number or text).
    """
    # Block 2.6.1.1: Return default if blank input
    if not user_input.strip():
        return param_def.get(PARAM_DEFAULT)
    
    # Block 2.6.1.2: Try numeric selection first (1-indexed)
    try:
        selection_index = int(user_input) - 1
        if 0 <= selection_index < len(allowed_values):
            return allowed_values[selection_index]
    except ValueError:
        pass
    
    # Block 2.6.1.3: Try exact text match
    user_input_stripped = user_input.strip()
    if user_input_stripped in allowed_values:
        return user_input_stripped
    
    # Block 2.6.1.4: Raise error for invalid selection
    raise ValueError("Invalid selection. Enter number or exact text value")
```

**Code 2.7.1: Display multiple choice options**

```python
# Block 2.7.1: Add to src/spafw37/input_prompt.py
def _display_multiple_choice_options(allowed_values):
    """Display numbered list of multiple choice options.
    
    Args:
        allowed_values: List of allowed string values to display.
    """
    # Block 2.7.1.1: Display each option with 1-indexed number
    for option_index, option_value in enumerate(allowed_values, start=1):
        print("{0}. {1}".format(option_index, option_value))
```

**Test 2.6.2: Tests for multiple choice selection by number**

```gherkin
Scenario: Multiple choice selection by number works correctly
  Given a param with PARAM_ALLOWED_VALUES ["option1", "option2", "option3"]
  And stdin is mocked with StringIO("2\n")
  When prompt_for_value() is called
  Then numbered list displayed: "1. option1\n2. option2\n3. option3"
  And the function returns "option2"
  
  # Tests: Multiple choice selection by index number
  # Validates: Users can select by entering list number
```

```python
# Test 2.6.2: Add to tests/test_input_prompt.py
def test_prompt_multiple_choice_by_number(monkeypatch, capsys):
    """Test that users can select from multiple choice options by entering the numeric index.
    
    This test verifies that when PARAM_ALLOWED_VALUES contains ["red", "green", "blue"]
    and the user enters "2", the handler returns "green" (the second option).
    This behaviour is expected because numbered selection provides an efficient interface
    where users can type a single digit instead of the full option text."""
    # Block 2.6.2.1: Create param with allowed values
    param_def = {
        PARAM_PROMPT: 'Select option',
        PARAM_ALLOWED_VALUES: ['red', 'green', 'blue']
    }
    
    # Block 2.6.2.2: Mock stdin with numeric selection
    mock_stdin = StringIO("2\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.6.2.3: Call prompt handler
    selected_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.6.2.4: Verify correct option selected
    assert selected_value == 'green', "Expected 'green', got '{0}'".format(selected_value)
    
    # Block 2.6.2.5: Verify numbered list was displayed
    captured_output = capsys.readouterr()
    assert '1. red' in captured_output.out, "Option 1 not displayed"
    assert '2. green' in captured_output.out, "Option 2 not displayed"
    assert '3. blue' in captured_output.out, "Option 3 not displayed"
```

**Test 2.6.3: Tests for multiple choice selection by exact text**

```gherkin
Scenario: Multiple choice selection by exact text works correctly
  Given a param with PARAM_ALLOWED_VALUES ["red", "green", "blue"]
  And stdin is mocked with StringIO("green\n")
  When prompt_for_value() is called
  Then the function returns "green"
  And selection matches exact text from allowed values
  
  # Tests: Multiple choice selection by typing exact value
  # Validates: Users can select by entering the text value directly
```

```python
# Test 2.6.3: Add to tests/test_input_prompt.py
def test_prompt_multiple_choice_by_text(monkeypatch):
    """Test that users can select from multiple choice options by entering the exact text value.
    
    This test verifies that when PARAM_ALLOWED_VALUES contains ["red", "green", "blue"]
    and the user enters "green", the handler returns "green" directly.
    This behaviour is expected because some users prefer typing the full option name
    rather than remembering numeric indices, providing flexible selection methods."""
    # Block 2.6.3.1: Create param with allowed values
    param_def = {
        PARAM_PROMPT: 'Select colour',
        PARAM_ALLOWED_VALUES: ['red', 'green', 'blue']
    }
    
    # Block 2.6.3.2: Mock stdin with text selection
    mock_stdin = StringIO("green\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.6.3.3: Call prompt handler
    selected_value = input_prompt.prompt_for_value(param_def)
    
    # Block 2.6.3.4: Verify correct text match
    assert selected_value == 'green', "Expected 'green', got '{0}'".format(selected_value)
```

**Test 2.6.4: Tests for multiple choice invalid selection validation**

```gherkin
Scenario: Invalid multiple choice selection raises ValueError
  Given a param with PARAM_ALLOWED_VALUES ["red", "green", "blue"]
  And stdin is mocked with StringIO("yellow\n")
  When prompt_for_value() is called
  Then ValueError is raised
  And error message indicates invalid selection
  
  # Tests: Multiple choice validation
  # Validates: Invalid selections rejected with clear error
```

```python
# Test 2.6.4: Add to tests/test_input_prompt.py
def test_prompt_multiple_choice_invalid_selection(monkeypatch):
    """Test that invalid selections raise ValueError for multiple choice parameters.
    
    This test verifies that when the user enters "yellow" for options ["red", "green", "blue"],
    the handler raises ValueError with a message about valid selection methods.
    This behaviour is expected because only values in PARAM_ALLOWED_VALUES or their indices
    are valid, and invalid selections must be rejected to enable retry logic."""
    # Block 2.6.4.1: Create param with allowed values
    param_def = {
        PARAM_PROMPT: 'Select colour',
        PARAM_ALLOWED_VALUES: ['red', 'green', 'blue']
    }
    
    # Block 2.6.4.2: Mock stdin with invalid selection
    mock_stdin = StringIO("yellow\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.6.4.3: Verify ValueError raised
    with pytest.raises(ValueError, match="Invalid selection"):
        input_prompt.prompt_for_value(param_def)
```

**Code 2.8.1: Main prompt handler function**

```python
# Block 2.8.1: Add to src/spafw37/input_prompt.py
def prompt_for_value(param_def):
    """Main prompt handler using Python's built-in input() function.
    
    Prompts user for input based on param type and configuration.
    Handles text, number, toggle, and multiple choice inputs.
    
    Args:
        param_def: Parameter definition dictionary containing:
            - PARAM_PROMPT: Prompt text to display
            - PARAM_TYPE: Type of input (text/number/toggle)
            - PARAM_DEFAULT: Optional default value
            - PARAM_ALLOWED_VALUES: Optional list for multiple choice
    
    Returns:
        User input value converted to appropriate type.
        
    Raises:
        EOFError: If stdin reaches EOF (non-interactive environment).
        ValueError: If input cannot be converted to required type.
    """
    # Block 2.8.1.1: Get allowed values for multiple choice
    allowed_values = param_def.get(PARAM_ALLOWED_VALUES)
    if allowed_values:
        _display_multiple_choice_options(allowed_values)
    
    # Block 2.8.1.2: Format and display prompt text
    prompt_text = _format_prompt_text(param_def)
    user_input = input(prompt_text)
    
    # Block 2.8.1.3: Handle multiple choice if allowed values present
    if allowed_values:
        return _handle_multiple_choice_input(param_def, user_input, allowed_values)
    
    # Block 2.8.1.4: Get param type with text as default
    param_type = param_def.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # Block 2.8.1.5: Route to appropriate handler based on type
    if param_type == PARAM_TYPE_NUMBER:
        return _handle_number_input(param_def, user_input)
    elif param_type == PARAM_TYPE_TOGGLE:
        return _handle_toggle_input(param_def, user_input)
    else:
        return _handle_text_input(param_def, user_input)
```

**Test 2.8.2: Tests for EOF handling in non-interactive environment**

```gherkin
Scenario: EOF on stdin raises EOFError
  Given a param with PARAM_TYPE_TEXT
  And stdin is mocked with StringIO("") (empty)
  When prompt_for_value() is called
  Then EOFError is raised
  And no value is returned
  
  # Tests: EOF handling when stdin closes unexpectedly
  # Validates: Framework detects and reports EOF condition properly
```

```python
# Test 2.8.2: Add to tests/test_input_prompt.py
def test_prompt_eof_raises_error(monkeypatch):
    """Test that EOF condition raises EOFError when stdin closes unexpectedly.
    
    This test verifies that when stdin is empty (EOF condition from Ctrl+D, closed pipe,
    or automated scripts), the handler raises EOFError rather than failing silently.
    This behaviour is expected because EOF must be detected and reported clearly,
    ensuring the application fails predictably in non-interactive environments."""
    # Block 2.8.2.1: Create param definition
    param_def = {
        PARAM_PROMPT: 'Enter value',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    
    # Block 2.8.2.2: Mock stdin with empty stream (EOF)
    mock_stdin = StringIO("")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    
    # Block 2.8.2.3: Verify EOFError raised
    with pytest.raises(EOFError):
        input_prompt.prompt_for_value(param_def)
```

[↑ Back to top](#table-of-contents)


---

**Step 3: Add param registration logic**

**File:** `src/spafw37/param.py`

Add internal state for prompt handling, extend parameter registration to validate and store prompt properties, and provide public APIs for dynamic configuration.

**Implementation order:**

1. Add module-level storage for global prompt handler and prompted params tracking
2. Import new prompt constants from constants/param.py module
3. Create validation helper to check prompt timing values are valid
4. Create validation helper to check prompt repeat values are valid
5. Add prompt property validation to parameter registration flow
6. Implement public API function to set global prompt handler
7. Implement public API function to update allowed values dynamically
8. Add unit tests for validation helpers
9. Add unit tests for prompt property storage during registration
10. Add unit tests for public API functions

**Code 3.1.1: Module-level prompt state**

```python
# Block 3.1.1: Add after _SWITCH_REGISTER constant in src/spafw37/param.py
# Global prompt handler storage (None = use default handler)
_global_prompt_handler = None

# Tracked params that have been prompted (for PROMPT_REPEAT_NEVER)
_prompted_params = set()

# Auto-population flag marker (internal use only)
_PROMPT_AUTO_POPULATE = '_prompt_auto_populate'
```

Module-level imports for `tests/test_param_prompts.py`:
```python
# Module-level imports for tests/test_param_prompts.py
from spafw37 import param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT,
    PROMPT_ON_START,
    PROMPT_ON_COMMAND,
    PROMPT_REPEAT_ALWAYS,
    PROMPT_REPEAT_IF_BLANK,
    PROMPT_REPEAT_NEVER
)
```

**Test 3.1.2: Tests for module-level state initialisation**

```gherkin
Scenario: Module-level prompt state initialises correctly
  Given the param module is imported
  When checking module-level variables
  Then _global_prompt_handler is None
  And _prompted_params is an empty set
  And _PROMPT_AUTO_POPULATE constant is defined
  
  # Tests: Module-level state initialisation
  # Validates: Prompt state starts in clean initial state
```

```python
# Test 3.1.2: Add to tests/test_param_prompts.py
def test_module_level_prompt_state_initialised():
    """Test that module-level prompt state variables are initialised correctly.
    
    This test verifies _global_prompt_handler starts as None (no custom handler),
    _prompted_params starts as empty set (no prompts executed yet), and the
    _PROMPT_AUTO_POPULATE flag constant is defined for marking params during registration.
    This behaviour is expected because clean initial state ensures no leftover configuration
    from previous test runs or imports affects prompt behaviour."""
    # Block 3.1.2.1: Verify global handler starts as None
    assert param._global_prompt_handler is None, "Global handler should start as None"
    
    # Block 3.1.2.2: Verify prompted params tracking starts empty
    assert isinstance(param._prompted_params, set), "Prompted params must be a set"
    assert len(param._prompted_params) == 0, "Prompted params should start empty"
    
    # Block 3.1.2.3: Verify auto-populate flag constant exists
    assert hasattr(param, '_PROMPT_AUTO_POPULATE'), "Auto-populate flag constant missing"
    assert isinstance(param._PROMPT_AUTO_POPULATE, str), "Flag must be string key"
```

**Code 3.2.1: Import prompt constants**

```python
# Block 3.2.1: Add to imports section after existing PARAM_* imports
from spafw37.constants.param import (
    # ... existing imports ...
    PARAM_PROMPT,
    PARAM_PROMPT_HANDLER,
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT,
    PROMPT_ON_START,
    PROMPT_ON_COMMAND,
    PROMPT_REPEAT_ALWAYS,
    PROMPT_REPEAT_IF_BLANK,
    PROMPT_REPEAT_NEVER,
)
```

**Code 3.3.1: Validate prompt timing value**

```python
# Block 3.3.1: Add before add_param() function
def _validate_prompt_timing(timing_value):
    """Validate PARAM_PROMPT_TIMING value is a recognised constant.
    
    Args:
        timing_value: Value from PARAM_PROMPT_TIMING property.
        
    Raises:
        ValueError: If timing value is not valid.
    """
    # Block 3.3.1.1: Accept PROMPT_ON_START constant
    if timing_value == PROMPT_ON_START:
        return
    
    # Block 3.3.1.2: Accept PROMPT_ON_COMMAND constant
    if timing_value == PROMPT_ON_COMMAND:
        return
    
    # Block 3.3.1.3: Reject all other values
    raise ValueError(
        "PARAM_PROMPT_TIMING must be PROMPT_ON_START or PROMPT_ON_COMMAND constant"
    )
```

**Test 3.3.2: Tests for prompt timing validation with valid constant**

```gherkin
Scenario: PROMPT_ON_START constant passes validation
  Given timing value set to PROMPT_ON_START constant
  When _validate_prompt_timing() is called
  Then no exception is raised
  And validation passes successfully
  
  # Tests: Valid timing constant acceptance
  # Validates: PROMPT_ON_START recognised as valid timing value
```

```python
# Test 3.3.2: Add to tests/test_param_prompts.py
def test_validate_prompt_timing_with_on_start():
    """Test that PROMPT_ON_START constant passes timing validation successfully.
    
    This test verifies _validate_prompt_timing() accepts the PROMPT_ON_START constant
    without raising exceptions, as this is one of the two valid timing modes.
    This behaviour is expected because PROMPT_ON_START indicates prompts should run
    immediately after CLI parsing, before command execution, which is a core timing option."""
    # Block 3.3.2.1: Call validation with PROMPT_ON_START
    try:
        param._validate_prompt_timing(PROMPT_ON_START)
        validation_passed = True
    except ValueError:
        validation_passed = False
    
    # Block 3.3.2.2: Verify validation passed
    assert validation_passed, "PROMPT_ON_START should pass validation"
```

**Test 3.3.3: Tests for prompt timing validation with PROMPT_ON_COMMAND constant**

```gherkin
Scenario: PROMPT_ON_COMMAND constant passes validation
  Given timing value set to PROMPT_ON_COMMAND constant
  When _validate_prompt_timing() is called
  Then no exception is raised
  And validation passes successfully
  
  # Tests: Valid timing constant acceptance
  # Validates: PROMPT_ON_COMMAND recognised as valid timing value
```

```python
# Test 3.3.3: Add to tests/test_param_prompts.py
def test_validate_prompt_timing_with_on_command():
    """Test that PROMPT_ON_COMMAND constant passes timing validation successfully.
    
    This test verifies _validate_prompt_timing() accepts the PROMPT_ON_COMMAND constant
    without raising exceptions, as this indicates prompts should run before specific commands.
    This behaviour is expected because PROMPT_ON_COMMAND tells the framework to check the
    PROMPT_ON_COMMANDS property for the list of commands to prompt before."""
    # Block 3.3.3.1: Call validation with PROMPT_ON_COMMAND
    try:
        param._validate_prompt_timing(PROMPT_ON_COMMAND)
        validation_passed = True
    except ValueError:
        validation_passed = False
    
    # Block 3.3.3.2: Verify validation passed
    assert validation_passed, "PROMPT_ON_COMMAND should pass validation"
```

**Test 3.3.4: Tests for prompt timing validation rejection of invalid values**

```gherkin
Scenario: Invalid timing value raises ValueError
  Given timing value set to "invalid_constant" or a list
  When _validate_prompt_timing() is called
  Then ValueError is raised
  And error message indicates valid options (PROMPT_ON_START or PROMPT_ON_COMMAND)
  
  # Tests: Invalid timing value rejection
  # Validates: Only PROMPT_ON_START or PROMPT_ON_COMMAND constants accepted
```

```python
# Test 3.3.4: Add to tests/test_param_prompts.py
def test_validate_prompt_timing_rejects_invalid_value():
    """Test that invalid timing values raise ValueError during validation.
    
    This test verifies _validate_prompt_timing() rejects values that are neither
    PROMPT_ON_START constant nor lists, such as arbitrary strings like "invalid".
    This behaviour is expected because accepting invalid timing values would cause
    subtle runtime errors when the framework tries to determine when to prompt."""
    # Block 3.3.4.1: Attempt validation with invalid value
    with pytest.raises(ValueError, match="PARAM_PROMPT_TIMING must be"):
        param._validate_prompt_timing("invalid_constant")
```

**Code 3.4.1: Validate prompt repeat value**

```python
# Block 3.4.1: Add after _validate_prompt_timing() function
def _validate_prompt_repeat(repeat_value):
    """Validate PARAM_PROMPT_REPEAT value is a recognised constant.
    
    Args:
        repeat_value: Value from PARAM_PROMPT_REPEAT property.
        
    Raises:
        ValueError: If repeat value is not valid.
    """
    # Block 3.4.1.1: Check against all valid repeat constants
    valid_repeats = (PROMPT_REPEAT_ALWAYS, PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_NEVER)
    if repeat_value not in valid_repeats:
        raise ValueError(
            "PARAM_PROMPT_REPEAT must be one of: PROMPT_REPEAT_ALWAYS, "
            "PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_NEVER"
        )
```

**Test 3.4.2: Tests for prompt repeat validation with valid constants**

```gherkin
Scenario: All three PROMPT_REPEAT_* constants pass validation
  Given repeat values PROMPT_REPEAT_ALWAYS, PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_NEVER
  When _validate_prompt_repeat() is called for each
  Then no exceptions are raised
  And all three constants accepted
  
  # Tests: Valid repeat constant acceptance
  # Validates: All repeat behaviour options recognised
```

```python
# Test 3.4.2: Add to tests/test_param_prompts.py
def test_validate_prompt_repeat_with_valid_constants():
    """Test that all PROMPT_REPEAT_* constants pass repeat validation successfully.
    
    This test verifies _validate_prompt_repeat() accepts PROMPT_REPEAT_ALWAYS,
    PROMPT_REPEAT_IF_BLANK, and PROMPT_REPEAT_NEVER without raising exceptions.
    This behaviour is expected because these three constants represent the complete
    set of valid repeat behaviours for prompts in cycle and multi-command scenarios."""
    # Block 3.4.2.1: Test each valid constant
    valid_constants = [PROMPT_REPEAT_ALWAYS, PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_NEVER]
    for repeat_constant in valid_constants:
        try:
            param._validate_prompt_repeat(repeat_constant)
            validation_passed = True
        except ValueError:
            validation_passed = False
        
        assert validation_passed, "Constant {0} should pass validation".format(repeat_constant)
```

**Test 3.4.3: Tests for prompt repeat validation rejection of invalid values**

```gherkin
Scenario: Invalid repeat value raises ValueError
  Given repeat value set to "invalid_repeat"
  When _validate_prompt_repeat() is called
  Then ValueError is raised
  And error message lists valid constants
  
  # Tests: Invalid repeat value rejection
  # Validates: Only valid PROMPT_REPEAT_* constants accepted
```

```python
# Test 3.4.3: Add to tests/test_param_prompts.py
def test_validate_prompt_repeat_rejects_invalid_value():
    """Test that invalid repeat values raise ValueError during validation.
    
    This test verifies _validate_prompt_repeat() rejects arbitrary values that are
    not one of the three valid PROMPT_REPEAT_* constants.
    This behaviour is expected because accepting invalid repeat values would cause
    undefined behaviour in cycle logic where the framework checks repeat mode."""
    # Block 3.4.3.1: Attempt validation with invalid value
    with pytest.raises(ValueError, match="PARAM_PROMPT_REPEAT must be one of"):
        param._validate_prompt_repeat("invalid_repeat")
```

**Code 3.5.1: Validate and process prompt properties in add_param**

```python
# Block 3.5.1: Add after _apply_runtime_only_constraint() call in add_param()
def _validate_and_process_prompt_properties(_param):
    """Validate and process prompt-related properties during parameter registration.
    
    Args:
        _param: Parameter definition dictionary.
        
    Raises:
        ValueError: If prompt properties are invalid or required fields missing.
    """
    # Block 3.5.1.1: Skip if param has no PARAM_PROMPT (not a prompt-enabled param)
    if PARAM_PROMPT not in _param:
        return
    
    # Block 3.5.1.2: Validate PARAM_PROMPT is a non-empty string
    prompt_text = _param[PARAM_PROMPT]
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        param_name = _param.get(PARAM_NAME, '<unknown>')
        raise ValueError(
            "PARAM_PROMPT must be a non-empty string for param '{0}'".format(param_name)
        )
    
    # Block 3.5.1.3: Validate PARAM_TYPE exists (required for input handling)
    if PARAM_TYPE not in _param:
        param_name = _param.get(PARAM_NAME, '<unknown>')
        raise ValueError(
            "PARAM_TYPE is required for prompt-enabled param '{0}'".format(param_name)
        )
    
    # Block 3.5.1.4: Validate timing if specified
    if PARAM_PROMPT_TIMING in _param:
        _validate_prompt_timing(_param[PARAM_PROMPT_TIMING])
    else:
        # Block 3.5.1.5: Mark for auto-population if no explicit timing
        _param[_PROMPT_AUTO_POPULATE] = True
    
    # Block 3.5.1.6: Validate repeat behaviour if specified
    if PARAM_PROMPT_REPEAT in _param:
        _validate_prompt_repeat(_param[PARAM_PROMPT_REPEAT])
```

**Test 3.5.2: Tests for prompt property validation during registration**

```gherkin
Scenario: Param with PARAM_PROMPT and valid timing registers successfully
  Given a param with PARAM_PROMPT and PARAM_PROMPT_TIMING set to PROMPT_ON_START
  When add_param() is called
  Then param is registered without errors
  And PARAM_PROMPT_TIMING property is preserved
  
  # Tests: Successful registration with valid prompt properties
  # Validates: Validation accepts valid prompt configurations
```

```python
# Test 3.5.2: Add to tests/test_param_prompts.py
def test_param_with_valid_prompt_properties_registers():
    """Test that params with valid prompt properties register successfully without errors.
    
    This test verifies add_param() accepts parameters with PARAM_PROMPT and valid
    PARAM_PROMPT_TIMING (PROMPT_ON_START), storing all properties correctly.
    This behaviour is expected because properly configured prompt params are valid
    and should integrate seamlessly with the registration system."""
    # Block 3.5.2.1: Clear any existing params
    param._params = {}
    
    # Block 3.5.2.2: Create param with valid prompt properties
    test_param = {
        PARAM_NAME: 'test_prompt_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START
    }
    
    # Block 3.5.2.3: Register param (should not raise)
    param.add_param(test_param)
    
    # Block 3.5.2.4: Verify param was registered with properties intact
    registered_param = param.get_param_by_name('test_prompt_param')
    assert registered_param is not None, "Param should be registered"
    assert registered_param[PARAM_PROMPT] == 'Enter value:', "PARAM_PROMPT not preserved"
    assert registered_param[PARAM_PROMPT_TIMING] == PROMPT_ON_START, "Timing not preserved"
```

**Test 3.5.3: Tests for auto-population flag on params without explicit timing**

```gherkin
Scenario: Param with PARAM_PROMPT but no timing gets auto-populate flag
  Given a param with PARAM_PROMPT but no PARAM_PROMPT_TIMING
  When add_param() is called
  Then param is registered with auto-populate flag set
  And flag indicates PROMPT_ON_COMMANDS should be populated from commands
  
  # Tests: Auto-population flag mechanism
  # Validates: Params without explicit timing marked for command-driven population
```

```python
# Test 3.5.3: Add to tests/test_param_prompts.py
def test_param_without_timing_gets_auto_populate_flag():
    """Test that params with PARAM_PROMPT but no explicit timing get auto-populate flag.
    
    This test verifies add_param() marks parameters with _PROMPT_AUTO_POPULATE flag
    when they have PARAM_PROMPT but don't specify PARAM_PROMPT_TIMING.
    This behaviour is expected because the auto-population mechanism allows commands
    to automatically trigger prompts for their required params without duplicate configuration."""
    # Block 3.5.3.1: Clear any existing params
    param._params = {}
    
    # Block 3.5.3.2: Create param with PARAM_PROMPT but no timing
    test_param = {
        PARAM_NAME: 'auto_populate_param',
        PARAM_PROMPT: 'Enter value:'
    }
    
    # Block 3.5.3.3: Register param
    param.add_param(test_param)
    
    # Block 3.5.3.4: Verify auto-populate flag is set
    registered_param = param.get_param_by_name('auto_populate_param')
    assert registered_param[param._PROMPT_AUTO_POPULATE] is True, "Auto-populate flag should be set"
```

**Test 3.5.4: Tests for invalid prompt timing rejection during registration**

```gherkin
Scenario: Param with invalid PARAM_PROMPT_TIMING raises ValueError
  Given a param with PARAM_PROMPT_TIMING set to "invalid_value"
  When add_param() is called
  Then ValueError is raised
  And param is not registered
  
  # Tests: Invalid timing rejection at registration time
  # Validates: Registration fails fast for invalid configurations
```

```python
# Test 3.5.4: Add to tests/test_param_prompts.py
def test_param_with_invalid_timing_raises_error_on_registration():
    """Test that params with invalid PARAM_PROMPT_TIMING values are rejected during registration.
    
    This test verifies add_param() raises ValueError when a parameter specifies an
    invalid PARAM_PROMPT_TIMING value (not PROMPT_ON_START or a list).
    This behaviour is expected because failing fast during registration prevents subtle
    runtime errors when the framework tries to determine prompt timing."""
    # Block 3.5.4.1: Clear any existing params
    param._params = {}
    
    # Block 3.5.4.2: Create param with invalid timing
    invalid_param = {
        PARAM_NAME: 'invalid_timing_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: 'invalid_value'
    }
    
    # Block 3.5.4.3: Verify ValueError raised during registration
    with pytest.raises(ValueError, match="PARAM_PROMPT_TIMING must be"):
        param.add_param(invalid_param)
```

**Test 3.5.5: Tests for empty PARAM_PROMPT rejection during registration**

```gherkin
Scenario: Param with empty or whitespace-only PARAM_PROMPT raises ValueError
  Given a param with PARAM_PROMPT set to empty string or "   "
  When add_param() is called
  Then ValueError is raised
  And error message indicates PARAM_PROMPT must be non-empty string
  
  # Tests: PARAM_PROMPT field validation
  # Validates: Prompt text must be meaningful (non-empty string)
```

```python
# Test 3.5.5: Add to tests/test_param_prompts.py
def test_param_with_empty_prompt_raises_error():
    """Test that params with empty or whitespace-only PARAM_PROMPT are rejected.
    
    This test verifies add_param() raises ValueError when PARAM_PROMPT is an empty
    string or contains only whitespace, as prompt text must be meaningful.
    This behaviour is expected because empty prompts would confuse users and
    indicate a configuration error."""
    # Block 3.5.5.1: Clear any existing params
    param._params = {}
    
    # Block 3.5.5.2: Test empty string
    empty_param = {
        PARAM_NAME: 'empty_prompt',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: ''
    }
    with pytest.raises(ValueError, match="PARAM_PROMPT must be a non-empty string"):
        param.add_param(empty_param)
    
    # Block 3.5.5.3: Test whitespace-only string
    param._params = {}
    whitespace_param = {
        PARAM_NAME: 'whitespace_prompt',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: '   '
    }
    with pytest.raises(ValueError, match="PARAM_PROMPT must be a non-empty string"):
        param.add_param(whitespace_param)
```

**Test 3.5.6: Tests for missing PARAM_TYPE rejection for prompt params**

```gherkin
Scenario: Prompt param without PARAM_TYPE raises ValueError
  Given a param with PARAM_PROMPT but no PARAM_TYPE
  When add_param() is called
  Then ValueError is raised
  And error message indicates PARAM_TYPE required for prompt params
  
  # Tests: Required field validation for prompt params
  # Validates: PARAM_TYPE needed to determine input handling
```

```python
# Test 3.5.6: Add to tests/test_param_prompts.py
def test_prompt_param_without_type_raises_error():
    """Test that prompt-enabled params without PARAM_TYPE are rejected during registration.
    
    This test verifies add_param() raises ValueError when a parameter has PARAM_PROMPT
    but doesn't specify PARAM_TYPE, which is needed to determine input handling.
    This behaviour is expected because the framework needs PARAM_TYPE to know how to
    parse and validate user input (text, number, toggle, etc.)."""
    # Block 3.5.6.1: Clear any existing params
    param._params = {}
    
    # Block 3.5.6.2: Create prompt param without PARAM_TYPE
    no_type_param = {
        PARAM_NAME: 'no_type_prompt',
        PARAM_PROMPT: 'Enter value:'
    }
    
    # Block 3.5.6.3: Verify ValueError raised during registration
    with pytest.raises(ValueError, match="PARAM_TYPE is required for prompt-enabled param"):
        param.add_param(no_type_param)
```

**Code 3.6.1: Public API to set global prompt handler**

```python
# Block 3.6.1: Add after add_pre_parse_args() function
def set_prompt_handler(handler):
    """Set the global prompt handler function for all parameters.
    
    This handler will be used for any parameter prompts that don't have
    a param-specific PARAM_PROMPT_HANDLER defined. Set to None to restore
    the default handler (input_prompt.prompt_for_value).
    
    Args:
        handler: Callable that accepts param_def dict and returns user input value.
                 Signature: handler(param_def) -> value
    """
    global _global_prompt_handler
    _global_prompt_handler = handler
```

**Test 3.6.2: Tests for set_prompt_handler storing custom handler**

```gherkin
Scenario: Custom prompt handler set via set_prompt_handler()
  Given a custom handler function custom_handler()
  When set_prompt_handler(custom_handler) is called
  Then _global_prompt_handler stores custom_handler reference
  And subsequent prompts will use custom_handler by default
  
  # Tests: Global handler registration
  # Validates: Custom handlers can replace default input() behaviour globally
```

```python
# Test 3.6.2: Add to tests/test_param_prompts.py
def test_set_prompt_handler_stores_custom_handler():
    """Test that set_prompt_handler() correctly stores custom handler reference globally.
    
    This test verifies set_prompt_handler() updates the module-level _global_prompt_handler
    variable with the provided custom handler function reference.
    This behaviour is expected because the global handler provides extensibility,
    allowing applications to replace the default input() handler with GUI prompts,
    API-based input, or other custom input mechanisms."""
    # Block 3.6.2.1: Define a custom handler function
    def custom_handler(param_def):
        return "custom_value"
    
    # Block 3.6.2.2: Set the global handler
    param.set_prompt_handler(custom_handler)
    
    # Block 3.6.2.3: Verify handler was stored
    assert param._global_prompt_handler is custom_handler, "Custom handler should be stored"
    
    # Block 3.6.2.4: Clean up (restore None)
    param.set_prompt_handler(None)
```

**Test 3.6.3: Tests for set_prompt_handler restoring default with None**

```gherkin
Scenario: Passing None to set_prompt_handler restores default behaviour
  Given _global_prompt_handler was set to a custom handler
  When set_prompt_handler(None) is called
  Then _global_prompt_handler is set to None
  And default handler will be used for prompts
  
  # Tests: Handler restoration to default
  # Validates: Applications can revert to default behaviour
```

```python
# Test 3.6.3: Add to tests/test_param_prompts.py
def test_set_prompt_handler_with_none_restores_default():
    """Test that passing None to set_prompt_handler() restores default handler behaviour.
    
    This test verifies set_prompt_handler(None) clears the custom handler, setting
    _global_prompt_handler back to None (which signals use of default handler).
    This behaviour is expected because applications need a way to revert to default
    behaviour after setting a custom handler, ensuring flexibility in testing and configuration."""
    # Block 3.6.3.1: Set a custom handler first
    def custom_handler(param_def):
        return "custom"
    param.set_prompt_handler(custom_handler)
    
    # Block 3.6.3.2: Restore default by passing None
    param.set_prompt_handler(None)
    
    # Block 3.6.3.3: Verify handler is None
    assert param._global_prompt_handler is None, "Handler should be None (default)"
```

**Code 3.7.1: Public API to set allowed values dynamically**

```python
# Block 3.7.1: Add after set_prompt_handler() function
def set_allowed_values(param_name, values):
    """Set or update PARAM_ALLOWED_VALUES for a parameter at runtime.
    
    This enables commands to populate multiple choice lists dynamically
    without requiring parameter re-registration.
    
    Args:
        param_name: Name of the parameter to update.
        values: List of allowed values for multiple choice prompts.
        
    Raises:
        ValueError: If parameter does not exist.
    """
    # Block 3.7.1.1: Get param definition (raises if not found)
    param_def = get_param_by_name(param_name)
    if param_def is None:
        raise ValueError("Parameter '{0}' not found".format(param_name))
    
    # Block 3.7.1.2: Update allowed values on param definition
    param_def[PARAM_ALLOWED_VALUES] = values
```

**Test 3.7.2: Tests for set_allowed_values updating existing param**

```gherkin
Scenario: Dynamic allowed values updated via set_allowed_values()
  Given a param "choices" already registered
  And param initially has no PARAM_ALLOWED_VALUES
  When set_allowed_values("choices", ["a", "b", "c"]) is called
  Then param definition updated with PARAM_ALLOWED_VALUES ["a", "b", "c"]
  And multiple choice prompting enabled for this param
  
  # Tests: Dynamic allowed values API
  # Validates: Commands can populate choice lists at runtime
```

```python
# Test 3.7.2: Add to tests/test_param_prompts.py
def test_set_allowed_values_updates_param_definition():
    """Test that set_allowed_values() dynamically updates PARAM_ALLOWED_VALUES on existing param.
    
    This test verifies set_allowed_values() successfully adds or updates the PARAM_ALLOWED_VALUES
    property on a registered parameter, enabling multiple choice prompting at runtime.
    This behaviour is expected because commands often need to populate choice lists dynamically
    based on data queries or user context without re-registering parameters."""
    # Block 3.7.2.1: Clear and register a param without allowed values
    param._params = {}
    test_param = {PARAM_NAME: 'choice_param'}
    param.add_param(test_param)
    
    # Block 3.7.2.2: Update allowed values dynamically
    param.set_allowed_values('choice_param', ['option_a', 'option_b', 'option_c'])
    
    # Block 3.7.2.3: Verify param definition was updated
    updated_param = param.get_param_by_name('choice_param')
    assert PARAM_ALLOWED_VALUES in updated_param, "PARAM_ALLOWED_VALUES should be added"
    assert updated_param[PARAM_ALLOWED_VALUES] == ['option_a', 'option_b', 'option_c'], "Values incorrect"
```

**Test 3.7.3: Tests for set_allowed_values with non-existent param**

```gherkin
Scenario: set_allowed_values with non-existent param raises ValueError
  Given no param named "nonexistent" is registered
  When set_allowed_values("nonexistent", ["a", "b"]) is called
  Then ValueError is raised
  And error message indicates parameter not found
  
  # Tests: Error handling for missing params
  # Validates: API fails clearly when param doesn't exist
```

```python
# Test 3.7.3: Add to tests/test_param_prompts.py
def test_set_allowed_values_raises_error_for_nonexistent_param():
    """Test that set_allowed_values() raises ValueError when parameter doesn't exist.
    
    This test verifies set_allowed_values() fails fast with clear error message when
    called with a parameter name that hasn't been registered.
    This behaviour is expected because updating allowed values on a non-existent parameter
    is a programming error that should be caught immediately rather than silently ignored."""
    # Block 3.7.3.1: Clear all params
    param._params = {}
    
    # Block 3.7.3.2: Attempt to set allowed values on non-existent param
    with pytest.raises(ValueError, match="Parameter 'nonexistent' not found"):
        param.set_allowed_values('nonexistent', ['a', 'b'])
```

**Test 3.8.1: Regression test for params without PARAM_PROMPT**

```gherkin
Scenario: Params without PARAM_PROMPT register identically to before
  Given a param without PARAM_PROMPT property (standard param)
  When add_param() is called
  Then param is registered successfully
  And no prompt validation is performed
  And param behaves exactly as in previous framework versions
  
  # Tests: Regression - non-prompt params unchanged
  # Validates: Adding prompt support doesn't break existing param registration
```

```python
# Test 3.8.1: Add to tests/test_param_prompts.py
def test_params_without_prompt_register_unchanged():
    """Regression test: params without PARAM_PROMPT register identically to before.
    
    This test verifies that adding prompt support doesn't break existing parameter
    registration. Params without PARAM_PROMPT should register and behave exactly
    as they did before prompt functionality was added.
    This behaviour is expected because backward compatibility is critical - existing
    applications must continue to work without modification."""
    # Block 3.8.1.1: Clear any existing params
    param._params = {}
    
    # Block 3.8.1.2: Create standard param without PARAM_PROMPT
    standard_param = {
        PARAM_NAME: 'standard_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'default_value',
        PARAM_ALLOWED_VALUES: ['option1', 'option2', 'option3']
    }
    
    # Block 3.8.1.3: Register param (should work exactly as before)
    param.add_param(standard_param)
    
    # Block 3.8.1.4: Verify param registered with all properties intact
    registered_param = param.get_param_by_name('standard_param')
    assert registered_param is not None, "Standard param should register"
    assert registered_param[PARAM_TYPE] == PARAM_TYPE_TEXT, "PARAM_TYPE preserved"
    assert registered_param[PARAM_DEFAULT] == 'default_value', "PARAM_DEFAULT preserved"
    assert registered_param[PARAM_ALLOWED_VALUES] == ['option1', 'option2', 'option3'], "PARAM_ALLOWED_VALUES preserved"
    
    # Block 3.8.1.5: Verify no prompt-related properties added automatically
    assert PARAM_PROMPT not in registered_param, "PARAM_PROMPT should not be added automatically"
    assert PARAM_PROMPT_TIMING not in registered_param, "PARAM_PROMPT_TIMING should not be added automatically"
```

**Test 3.8.2: Regression test for param validation behaviour**

```gherkin
Scenario: Existing param validation rules work unchanged
  Given a param without PARAM_PROMPT but with invalid PARAM_TYPE
  When add_param() is called
  Then validation error is raised exactly as before
  And error handling behaviour is unchanged
  
  # Tests: Regression - existing validation preserved
  # Validates: Prompt validation doesn't interfere with existing validation logic
```

```python
# Test 3.8.2: Add to tests/test_param_prompts.py
def test_existing_param_validation_unchanged():
    """Regression test: existing param validation rules work identically to before.
    
    This test verifies that adding prompt validation doesn't interfere with existing
    validation logic. Invalid params (missing required fields, invalid types, etc.)
    should fail validation exactly as they did before.
    This behaviour is expected because adding new validation for prompt properties
    must not change or break existing validation behaviour for non-prompt properties."""
    # Block 3.8.2.1: Clear any existing params
    param._params = {}
    
    # Block 3.8.2.2: Create param with missing required PARAM_NAME
    invalid_param = {
        # Missing PARAM_NAME - should fail validation
    }
    
    # Block 3.8.2.3: Verify existing validation still works
    with pytest.raises((ValueError, KeyError)):
        param.add_param(invalid_param)
```

**Test 3.8.3: Regression test for param operations on non-prompt params**

```gherkin
Scenario: get_param, set_param, and other operations work unchanged for non-prompt params
  Given a registered param without PARAM_PROMPT
  When get_param(), set_param(), and other param operations are used
  Then all operations work exactly as before
  And no prompt-related side effects occur
  
  # Tests: Regression - param operations unchanged
  # Validates: Adding prompt support doesn't alter existing param operation behaviour
```

```python
# Test 3.8.3: Add to tests/test_param_prompts.py
def test_param_operations_unchanged_for_non_prompt_params():
    """Regression test: param operations work identically for params without PARAM_PROMPT.
    
    This test verifies that get_param(), set_param(), and other param operations continue
    to work exactly as before for params without prompt configuration.
    This behaviour is expected because prompt functionality should be entirely opt-in
    through PARAM_PROMPT property - params without it should be completely unaffected."""
    # Block 3.8.3.1: Clear and register standard param
    param._params = {}
    test_param = {
        PARAM_NAME: 'counter',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    param.add_param(test_param)
    
    # Block 3.8.3.2: Test set_param() works unchanged
    param.set_param('counter', 42)
    
    # Block 3.8.3.3: Test get_param() works unchanged
    value = param.get_param('counter')
    assert value == 42, "get_param() should return set value"
    
    # Block 3.8.3.4: Test get_param_by_name() works unchanged
    param_def = param.get_param_by_name('counter')
    assert param_def is not None, "get_param_by_name() should return param definition"
    assert param_def[PARAM_NAME] == 'counter', "Param definition unchanged"
```

[↑ Back to top](#table-of-contents)

---

**Step 4.1: Process inline param definitions in COMMAND_PROMPT_PARAMS**

**File:** `src/spafw37/command.py`

Following the established pattern from `COMMAND_REQUIRED_PARAMS` inline processing, implement support for inline param definitions in `COMMAND_PROMPT_PARAMS`. This maintains API consistency across the framework where commands can define params inline alongside named references.

**Algorithm:**

1. Check if command has `COMMAND_PROMPT_PARAMS` property; if not present, return early
2. Iterate through each entry in the `COMMAND_PROMPT_PARAMS` list
3. For each entry:
   - If entry is a string: add it directly to normalised list (references existing param)
   - If entry is a dict: call `param._register_inline_param(entry)` to register the param, then extract and add the param name to normalised list
   - If entry is neither string nor dict: raise `ValueError` indicating invalid entry type
4. Replace the command's `COMMAND_PROMPT_PARAMS` property with the normalised list containing only param name strings

This enables commands to mix named references ("username") with inline definitions ({PARAM_NAME: "password", PARAM_PROMPT: "Password:", ...}) in the same list, providing flexibility for shared params and command-specific params.

**Implementation order:**

1. Create `_normalise_prompt_params(cmd)` helper function after `_register_inline_command()` helper
2. Add call to helper in `add_command()` function after inline processing for `COMMAND_TRIGGER_PARAM`
3. Add regression tests verifying existing command registration still works unchanged
4. Add tests for string entries (named param references)
5. Add tests for dict entries (inline param definitions)
6. Add tests for mixed entries (strings and dicts together)
7. Add tests for invalid entry types (raise ValueError)

**Module-level imports for tests/test_command.py:**

```python
# Module-level imports for tests/test_command.py
from spafw37 import command, param
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_PROMPT_PARAMS,
    COMMAND_REQUIRED_PARAMS,
    PROMPT_ON_COMMANDS
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_TYPE,
    PARAM_TYPE_TEXT
)
import pytest
```

**Code 4.1.1: Helper function to normalise COMMAND_PROMPT_PARAMS**

```python
# Block 4.1.1: Add to src/spafw37/command.py after _register_inline_command() helper
def _normalise_prompt_params(cmd):
    """Normalise COMMAND_PROMPT_PARAMS by processing inline param definitions.
    
    Processes both string references and dict definitions in COMMAND_PROMPT_PARAMS,
    registering inline params and building a normalised list of param names.
    
    Args:
        cmd: Command definition dictionary
    """
    # Block 4.1.1.1: Get prompt params list
    prompt_params = cmd.get(COMMAND_PROMPT_PARAMS, [])
    if not prompt_params:
        return
    
    # Block 4.1.1.2: Normalise each entry
    normalised_params = []
    for param_def in prompt_params:
        param_name = param._register_inline_param(param_def)
        normalised_params.append(param_name)
    
    # Block 4.1.1.3: Replace with normalised list
    cmd[COMMAND_PROMPT_PARAMS] = normalised_params
```

**Code 4.1.2: Call normalisation helper from add_command()**

```python
# Block 4.1.2: Add to src/spafw37/command.py in add_command() after COMMAND_TRIGGER_PARAM processing
# Process inline parameter definitions in COMMAND_PROMPT_PARAMS
_normalise_prompt_params(cmd)
```

**Test 4.1.3: Regression test for command registration without COMMAND_PROMPT_PARAMS**

```gherkin
Scenario: Command without COMMAND_PROMPT_PARAMS registers unchanged
  Given a command definition without COMMAND_PROMPT_PARAMS property
  When add_command() is called
  Then command registers successfully
  And no COMMAND_PROMPT_PARAMS property is added
  
  # Tests: Existing command registration behaviour unchanged
  # Validates: Feature is opt-in; commands without prompt params work identically
```

```python
# Test 4.1.3: Add to tests/test_command.py
def test_command_registration_without_prompt_params_unchanged():
    """Test that commands without COMMAND_PROMPT_PARAMS register identically to before.
    
    This regression test verifies that the new COMMAND_PROMPT_PARAMS processing does not
    affect commands that do not use this feature, ensuring backward compatibility.
    This behaviour is expected because prompt params are entirely opt-in."""
    # Block 4.1.3.1: Clear existing commands
    command._commands = {}
    
    # Block 4.1.3.2: Register command without COMMAND_PROMPT_PARAMS
    command.add_command({
        COMMAND_NAME: 'test_cmd',
        COMMAND_ACTION: lambda: None
    })
    
    # Block 4.1.3.3: Verify command registered successfully
    assert 'test_cmd' in command._commands
    
    # Block 4.1.3.4: Verify COMMAND_PROMPT_PARAMS not added
    registered_cmd = command._commands['test_cmd']
    assert COMMAND_PROMPT_PARAMS not in registered_cmd
```

**Test 4.1.4: String entry references existing param**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS with string entry references existing param
  Given a registered param "username"
  And a command with COMMAND_PROMPT_PARAMS containing "username"
  When add_command() is called
  Then COMMAND_PROMPT_PARAMS list contains "username" string unchanged
  
  # Tests: Named param reference processing
  # Validates: String entries pass through unchanged
```

```python
# Test 4.1.4: Add to tests/test_command.py
def test_prompt_params_string_entry_references_existing_param():
    """Test that COMMAND_PROMPT_PARAMS with string entry references an existing param.
    
    This test verifies that when COMMAND_PROMPT_PARAMS contains a string like "username",
    the framework treats it as a reference to an already-registered param and leaves it unchanged.
    This behaviour is expected because string entries are named references, consistent with
    the pattern used in COMMAND_REQUIRED_PARAMS."""
    # Block 4.1.4.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.1.4.2: Register param
    param.add_param({
        PARAM_NAME: 'username',
        PARAM_PROMPT: 'Username:'
    })
    
    # Block 4.1.4.3: Register command with string entry
    command.add_command({
        COMMAND_NAME: 'login',
        COMMAND_ACTION: lambda: None,
        COMMAND_PROMPT_PARAMS: ['username']
    })
    
    # Block 4.1.4.4: Verify list contains string unchanged
    registered_cmd = command._commands['login']
    assert registered_cmd[COMMAND_PROMPT_PARAMS] == ['username']
```

**Test 4.1.5: Dict entry registers inline param**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS with dict entry registers inline param
  Given a command with COMMAND_PROMPT_PARAMS containing inline param dict
  When add_command() is called
  Then param is registered via _register_inline_param()
  And COMMAND_PROMPT_PARAMS list contains extracted param name
  
  # Tests: Inline param definition processing
  # Validates: Dict entries trigger param registration and name extraction
```

```python
# Test 4.1.5: Add to tests/test_command.py
def test_prompt_params_dict_entry_registers_inline_param():
    """Test that COMMAND_PROMPT_PARAMS with dict entry registers an inline param definition.
    
    This test verifies that when COMMAND_PROMPT_PARAMS contains a dictionary like
    {PARAM_NAME: 'password', PARAM_PROMPT: 'Password:'}, the framework calls
    _register_inline_param() to register that param and extracts the name into the list.
    This behaviour is expected because dict entries define params inline, consistent with
    COMMAND_REQUIRED_PARAMS inline processing."""
    # Block 4.1.5.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.1.5.2: Register command with inline dict entry
    command.add_command({
        COMMAND_NAME: 'secure_login',
        COMMAND_ACTION: lambda: None,
        COMMAND_PROMPT_PARAMS: [{
            PARAM_NAME: 'password',
            PARAM_PROMPT: 'Password:'
        }]
    })
    
    # Block 4.1.5.3: Verify param was registered
    assert 'password' in param._params
    
    # Block 4.1.5.4: Verify list contains extracted name
    registered_cmd = command._commands['secure_login']
    assert registered_cmd[COMMAND_PROMPT_PARAMS] == ['password']
```

**Test 4.1.6: Mixed entries process correctly**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS with mixed string and dict entries
  Given a command with COMMAND_PROMPT_PARAMS containing both strings and dicts
  When add_command() is called
  Then string entries pass through unchanged
  And dict entries register inline params
  And list contains all param names in order
  
  # Tests: Mixed entry type processing
  # Validates: Framework handles heterogeneous lists correctly
```

```python
# Test 4.1.6: Add to tests/test_command.py
def test_prompt_params_mixed_entries_process_correctly():
    """Test that COMMAND_PROMPT_PARAMS with mixed string and dict entries processes correctly.
    
    This test verifies that when COMMAND_PROMPT_PARAMS contains both named references
    (strings) and inline definitions (dicts), the framework processes each appropriately
    and builds a normalised list containing all param names in the original order.
    This behaviour is expected because the API allows flexibility to mix shared and
    command-specific params."""
    # Block 4.1.6.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.1.6.2: Register existing param
    param.add_param({
        PARAM_NAME: 'username',
        PARAM_PROMPT: 'Username:'
    })
    
    # Block 4.1.6.3: Register command with mixed entries
    command.add_command({
        COMMAND_NAME: 'mixed_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PROMPT_PARAMS: [
            'username',
            {PARAM_NAME: 'password', PARAM_PROMPT: 'Password:'},
            {PARAM_NAME: 'token', PARAM_PROMPT: 'Token:'}
        ]
    })
    
    # Block 4.1.6.4: Verify all params in list
    registered_cmd = command._commands['mixed_cmd']
    expected_list = ['username', 'password', 'token']
    assert registered_cmd[COMMAND_PROMPT_PARAMS] == expected_list
```

**Test 4.1.7: Invalid entry type raises ValueError**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS with invalid entry type raises error
  Given a command with COMMAND_PROMPT_PARAMS containing a number
  When add_command() is called
  Then ValueError is raised
  And error message indicates invalid entry type
  
  # Tests: Invalid entry type validation
  # Validates: Framework rejects non-string, non-dict entries
```

```python
# Test 4.1.7: Add to tests/test_command.py
def test_prompt_params_invalid_entry_type_raises_error():
    """Test that COMMAND_PROMPT_PARAMS with invalid entry type raises ValueError.
    
    This test verifies that when COMMAND_PROMPT_PARAMS contains an entry that is neither
    a string nor a dict (e.g., a number), the framework raises ValueError with a clear message.
    This behaviour is expected because only strings (named references) and dicts (inline
    definitions) are valid entry types in the param list API."""
    # Block 4.1.7.1: Clear existing state
    command._commands = {}
    
    # Block 4.1.7.2: Attempt to register command with invalid entry
    with pytest.raises(ValueError) as exc_info:
        command.add_command({
            COMMAND_NAME: 'invalid_cmd',
            COMMAND_ACTION: lambda: None,
            COMMAND_PROMPT_PARAMS: [123]
        })
    
    # Block 4.1.7.3: Verify error message
    assert 'must be string or dict' in str(exc_info.value).lower()
```

[↑ Back to top](#table-of-contents)

---

**Step 4.2: Build reciprocal registration for required params**

**File:** `src/spafw37/command.py`

Implement the auto-population mechanism that reduces configuration burden. When a param has `PARAM_PROMPT` but no explicit `PARAM_PROMPT_TIMING` (marked with internal `_PROMPT_AUTO_POPULATE` flag during param registration), and a command lists that param in `COMMAND_REQUIRED_PARAMS`, automatically establish the relationship. This allows commands to trigger prompts for their required params without duplicate configuration whilst building reciprocal lists for O(1) lookup.

**Algorithm:**

1. Initialize `COMMAND_PROMPT_PARAMS` as empty list on command if not already set
2. Check if command has `COMMAND_REQUIRED_PARAMS`; if not present, return early
3. Get the command name from command definition
4. For each param name in `COMMAND_REQUIRED_PARAMS`:
   a. Look up param definition from `param._params` registry
   b. If param not found or doesn't have `PARAM_PROMPT` property, skip to next param
   c. Check if param has `_PROMPT_AUTO_POPULATE` flag set to True:
      - If yes: Initialize `PROMPT_ON_COMMANDS` list on param if not set
      - Add this command name to param's `PROMPT_ON_COMMANDS` list (if not already present)
      - Clear the `_PROMPT_AUTO_POPULATE` flag (set to False)
   d. Check if param has `PROMPT_ON_COMMANDS` list and this command name is in that list:
      - If yes: Add param name to command's `COMMAND_PROMPT_PARAMS` list (if not already present)

This establishes bidirectional relationships: params know which commands they prompt before (`PROMPT_ON_COMMANDS`), and commands know which params prompt before them (`COMMAND_PROMPT_PARAMS`).

**Implementation order:**

1. Create leaf helper functions (no dependencies) with unit tests for each
2. Create mid-level helper functions (depend on leaf helpers) with unit tests for each
3. Create top-level helper function (entry point) with integration tests
4. Add call to helper in `add_command()`

**Code 4.2.1: Leaf helper to add param to command list**

```python
# Block 4.2.1: Add to src/spafw37/command.py after _normalise_prompt_params()
def _add_param_to_command_list(cmd, param_name):
    """Add param name to command's COMMAND_PROMPT_PARAMS list.
    
    Args:
        cmd: Command definition dictionary
        param_name: Parameter name string
    """
    # Block 4.2.1.1: Add param if not already present
    if param_name not in cmd[COMMAND_PROMPT_PARAMS]:
        cmd[COMMAND_PROMPT_PARAMS].append(param_name)
```

**Test 4.2.2: Unit test for adding param to command list**

```gherkin
Scenario: Param added to command list when not already present
  Given a command with initialized COMMAND_PROMPT_PARAMS list
  And a param name not in the list
  When _add_param_to_command_list() is called
  Then param name is appended to list
  And list contains only one entry for that param
  
  # Tests: Deduplication when adding param to command list
  # Validates: Helper prevents duplicate entries
```

```python
# Test 4.2.2: Add to tests/test_command.py
def test_add_param_to_command_list():
    """Test that _add_param_to_command_list() adds param to command list without duplicates.
    
    This test verifies that the helper function correctly adds a param name to the
    command's COMMAND_PROMPT_PARAMS list only if it's not already present.
    This behaviour prevents duplicate entries in the list."""
    # Block 4.2.2.1: Create command with empty list
    cmd = {COMMAND_PROMPT_PARAMS: []}
    
    # Block 4.2.2.2: Add param first time
    command._add_param_to_command_list(cmd, 'test_param')
    assert cmd[COMMAND_PROMPT_PARAMS] == ['test_param']
    
    # Block 4.2.2.3: Add same param again
    command._add_param_to_command_list(cmd, 'test_param')
    assert cmd[COMMAND_PROMPT_PARAMS] == ['test_param']
    
    # Block 4.2.2.4: Add different param
    command._add_param_to_command_list(cmd, 'other_param')
    assert cmd[COMMAND_PROMPT_PARAMS] == ['test_param', 'other_param']
```

**Code 4.2.3: Leaf helper to check if param prompts for command**

```python
# Block 4.2.3: Add to src/spafw37/command.py after _add_param_to_command_list()
def _param_prompts_for_command(param_def, cmd_name):
    """Check if param prompts before specified command.
    
    Args:
        param_def: Parameter definition dictionary
        cmd_name: Command name string
        
    Returns:
        True if param prompts before command, False otherwise
    """
    # Block 4.2.3.1: Check PROMPT_ON_COMMANDS list
    prompt_commands = param_def.get(PROMPT_ON_COMMANDS, [])
    return cmd_name in prompt_commands
```

**Test 4.2.4: Unit test for checking if param prompts for command**

```gherkin
Scenario: Param check returns True when command in PROMPT_ON_COMMANDS
  Given a param with PROMPT_ON_COMMANDS list containing command name
  When _param_prompts_for_command() is called with that command name
  Then function returns True
  
  # Tests: PROMPT_ON_COMMANDS list membership check
  # Validates: Helper correctly identifies prompt relationships
```

```python
# Test 4.2.4: Add to tests/test_command.py
def test_param_prompts_for_command():
    """Test that _param_prompts_for_command() correctly checks PROMPT_ON_COMMANDS list.
    
    This test verifies that the helper function returns True when the command name
    is in the param's PROMPT_ON_COMMANDS list, and False otherwise.
    This behaviour is essential for determining reciprocal relationships."""
    # Block 4.2.4.1: Param with command in list
    param_def = {PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']}
    assert command._param_prompts_for_command(param_def, 'cmd1') is True
    assert command._param_prompts_for_command(param_def, 'cmd2') is True
    
    # Block 4.2.4.2: Param with command not in list
    assert command._param_prompts_for_command(param_def, 'cmd3') is False
    
    # Block 4.2.4.3: Param without PROMPT_ON_COMMANDS
    param_def_no_list = {}
    assert command._param_prompts_for_command(param_def_no_list, 'cmd1') is False
```

**Code 4.2.5: Leaf helper to establish auto-populated relationship**

```python
# Block 4.2.5: Add to src/spafw37/command.py after _param_prompts_for_command()
def _establish_auto_populated_relationship(param_def, cmd_name):
    """Establish auto-populated relationship between param and command.
    
    Args:
        param_def: Parameter definition dictionary
        cmd_name: Command name string
    """
    # Block 4.2.5.1: Initialize PROMPT_ON_COMMANDS list
    if PROMPT_ON_COMMANDS not in param_def:
        param_def[PROMPT_ON_COMMANDS] = []
    
    # Block 4.2.5.2: Add command to param's list
    if cmd_name not in param_def[PROMPT_ON_COMMANDS]:
        param_def[PROMPT_ON_COMMANDS].append(cmd_name)
    
    # Block 4.2.5.3: Clear auto-populate flag
    param_def[param._PROMPT_AUTO_POPULATE] = False
```

**Test 4.2.6: Unit test for establishing auto-populated relationship**

```gherkin
Scenario: Auto-populated relationship established and flag cleared
  Given a param with _PROMPT_AUTO_POPULATE flag set
  When _establish_auto_populated_relationship() is called with command name
  Then param's PROMPT_ON_COMMANDS contains command name
  And _PROMPT_AUTO_POPULATE flag is set to False
  
  # Tests: Auto-populate mechanism for single param-command pair
  # Validates: Flag cleared to prevent re-processing
```

```python
# Test 4.2.6: Add to tests/test_command.py
def test_establish_auto_populated_relationship():
    """Test that _establish_auto_populated_relationship() creates bidirectional link and clears flag.
    
    This test verifies that the helper function initializes PROMPT_ON_COMMANDS if needed,
    adds the command name without duplicates, and clears the _PROMPT_AUTO_POPULATE flag.
    This behaviour ensures auto-population happens exactly once per param-command pair."""
    # Block 4.2.6.1: Param without PROMPT_ON_COMMANDS
    param_def = {param._PROMPT_AUTO_POPULATE: True}
    command._establish_auto_populated_relationship(param_def, 'test_cmd')
    assert param_def[PROMPT_ON_COMMANDS] == ['test_cmd']
    assert param_def[param._PROMPT_AUTO_POPULATE] is False
    
    # Block 4.2.6.2: Param with existing PROMPT_ON_COMMANDS
    param_def2 = {
        PROMPT_ON_COMMANDS: ['other_cmd'],
        param._PROMPT_AUTO_POPULATE: True
    }
    command._establish_auto_populated_relationship(param_def2, 'test_cmd')
    assert 'test_cmd' in param_def2[PROMPT_ON_COMMANDS]
    assert 'other_cmd' in param_def2[PROMPT_ON_COMMANDS]
    assert param_def2[param._PROMPT_AUTO_POPULATE] is False
    
    # Block 4.2.6.3: Prevent duplicates
    command._establish_auto_populated_relationship(param_def, 'test_cmd')
    assert param_def[PROMPT_ON_COMMANDS].count('test_cmd') == 1
```

**Code 4.2.7: Mid-level helper to process single required param relationship**

```python
# Block 4.2.7: Add to src/spafw37/command.py after _establish_auto_populated_relationship()
def _process_required_param_relationship(cmd, cmd_name, param_name):
    """Process relationship between command and a single required param.
    
    Args:
        cmd: Command definition dictionary
        cmd_name: Command name string
        param_name: Parameter name string
    """
    # Block 4.2.7.1: Look up param definition
    param_def = param.get_param_by_name(param_name)
    if not param_def or PARAM_PROMPT not in param_def:
        return
    
    # Block 4.2.7.2: Handle auto-populate flag
    if param_def.get(param._PROMPT_AUTO_POPULATE):
        _establish_auto_populated_relationship(param_def, cmd_name)
    
    # Block 4.2.7.3: Add param to command list if relationship exists
    if _param_prompts_for_command(param_def, cmd_name):
        _add_param_to_command_list(cmd, param_name)
```

**Test 4.2.8: Unit test for processing single required param relationship**

```gherkin
Scenario: Required param without PARAM_PROMPT skipped
  Given a param without PARAM_PROMPT property
  When _process_required_param_relationship() is called
  Then no relationship established
  And command list unchanged
  
  # Tests: Non-prompt params skipped during processing
  # Validates: Helper validates param has prompt capability
```

```python
# Test 4.2.8: Add to tests/test_command.py
def test_process_required_param_relationship_without_prompt():
    """Test that _process_required_param_relationship() skips params without PARAM_PROMPT.
    
    This test verifies that when a required param doesn't have PARAM_PROMPT configured,
    the helper function returns early without establishing any relationships.
    This behaviour is expected because only prompt-enabled params participate."""
    # Block 4.2.8.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.2.8.2: Register param without PARAM_PROMPT
    param.add_param({
        PARAM_NAME: 'config_file',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 4.2.8.3: Create command with empty list
    cmd = {COMMAND_PROMPT_PARAMS: []}
    
    # Block 4.2.8.4: Process relationship
    command._process_required_param_relationship(cmd, 'test_cmd', 'config_file')
    
    # Block 4.2.8.5: Verify no changes
    assert cmd[COMMAND_PROMPT_PARAMS] == []
    param_def = param._params['config_file']
    assert PROMPT_ON_COMMANDS not in param_def
```

**Code 4.2.9: Top-level helper to build reciprocal registration for required params**

```python
# Block 4.2.9: Add to src/spafw37/command.py after _process_required_param_relationship()
def _build_reciprocal_registration_for_required_params(cmd):
    """Build reciprocal registration between commands and their required prompt params.
    
    Auto-populates PROMPT_ON_COMMANDS for params marked with _PROMPT_AUTO_POPULATE flag
    when they appear in COMMAND_REQUIRED_PARAMS, establishing bidirectional relationships.
    
    Args:
        cmd: Command definition dictionary
    """
    # Block 4.2.9.1: Initialize COMMAND_PROMPT_PARAMS if not set
    if COMMAND_PROMPT_PARAMS not in cmd:
        cmd[COMMAND_PROMPT_PARAMS] = []
    
    # Block 4.2.9.2: Check for required params
    required_params = cmd.get(COMMAND_REQUIRED_PARAMS, [])
    if not required_params:
        return
    
    # Block 4.2.9.3: Process each required param
    cmd_name = cmd.get(COMMAND_NAME)
    for param_name in required_params:
        _process_required_param_relationship(cmd, cmd_name, param_name)
```

**Test 4.2.10: Integration test for command without required params**

```gherkin
Scenario: Command without COMMAND_REQUIRED_PARAMS unchanged
  Given a command definition without COMMAND_REQUIRED_PARAMS property
  When add_command() is called
  Then COMMAND_PROMPT_PARAMS is empty list
  And no param relationships established
  
  # Tests: Auto-population is opt-in via required params
  # Validates: Commands without dependencies unaffected
```

```python
# Test 4.2.10: Add to tests/test_command.py
def test_reciprocal_registration_without_required_params():
    """Test that commands without COMMAND_REQUIRED_PARAMS get empty COMMAND_PROMPT_PARAMS list.
    
    This regression test verifies that the auto-population mechanism initialises
    COMMAND_PROMPT_PARAMS as an empty list even when there are no required params.
    This behaviour is expected because the property should exist even if unused."""
    # Block 4.2.10.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.2.10.2: Register command without required params
    command.add_command({
        COMMAND_NAME: 'standalone_cmd',
        COMMAND_ACTION: lambda: None
    })
    
    # Block 4.2.10.3: Verify COMMAND_PROMPT_PARAMS is empty list
    registered_cmd = command._commands['standalone_cmd']
    assert registered_cmd[COMMAND_PROMPT_PARAMS] == []
```

**Test 4.2.11: Integration test for required param without PARAM_PROMPT**

```gherkin
Scenario: Required param without PARAM_PROMPT is skipped
  Given a param without PARAM_PROMPT property
  And a command with that param in COMMAND_REQUIRED_PARAMS
  When add_command() is called
  Then param is not added to COMMAND_PROMPT_PARAMS
  And no reciprocal relationship established
  
  # Tests: Auto-population only for prompt-enabled params
  # Validates: Framework skips non-prompt params
```

```python
# Test 4.2.11: Add to tests/test_command.py
def test_required_param_without_prompt_skipped():
    """Test that required params without PARAM_PROMPT are skipped during auto-population.
    
    This test verifies that when a command lists a param in COMMAND_REQUIRED_PARAMS,
    but that param does not have PARAM_PROMPT configured, the framework skips it
    during reciprocal registration. This behaviour is expected because only
    prompt-enabled params participate in the auto-population mechanism."""
    # Block 4.2.11.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.2.11.2: Register param without PARAM_PROMPT
    param.add_param({
        PARAM_NAME: 'config_file',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 4.2.11.3: Register command with required param
    command.add_command({
        COMMAND_NAME: 'process_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_REQUIRED_PARAMS: ['config_file']
    })
    
    # Block 4.2.11.4: Verify param not in COMMAND_PROMPT_PARAMS
    registered_cmd = command._commands['process_cmd']
    assert 'config_file' not in registered_cmd[COMMAND_PROMPT_PARAMS]
```


**Test 4.2.12: Integration test for auto-populate flag establishing relationship**

```gherkin
Scenario: Param with _PROMPT_AUTO_POPULATE flag establishes relationship
  Given a param with PARAM_PROMPT and _PROMPT_AUTO_POPULATE flag set
  And a command with that param in COMMAND_REQUIRED_PARAMS
  When add_command() is called
  Then param's PROMPT_ON_COMMANDS contains command name
  And command's COMMAND_PROMPT_PARAMS contains param name
  And _PROMPT_AUTO_POPULATE flag is cleared
  
  # Tests: Auto-population mechanism for flagged params
  # Validates: Bidirectional relationships established correctly
```

```python
# Test 4.2.12: Add to tests/test_command.py
def test_auto_populate_flag_establishes_bidirectional_relationship():
    """Test that params with _PROMPT_AUTO_POPULATE flag establish bidirectional relationships.
    
    This test verifies that when a param has PARAM_PROMPT and _PROMPT_AUTO_POPULATE flag set,
    and a command lists it in COMMAND_REQUIRED_PARAMS, the framework automatically establishes
    the reciprocal relationship: param's PROMPT_ON_COMMANDS includes the command, and command's
    COMMAND_PROMPT_PARAMS includes the param. The flag is then cleared to prevent re-processing.
    This behaviour is expected because it reduces configuration burden for common use cases."""
    # Block 4.2.12.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.2.12.2: Register param with auto-populate flag
    param.add_param({
        PARAM_NAME: 'username',
        PARAM_PROMPT: 'Username:',
        param._PROMPT_AUTO_POPULATE: True
    })
    
    # Block 4.2.12.3: Register command with required param
    command.add_command({
        COMMAND_NAME: 'login_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_REQUIRED_PARAMS: ['username']
    })
    
    # Block 4.2.12.4: Verify param's PROMPT_ON_COMMANDS
    param_def = param._params['username']
    assert 'login_cmd' in param_def[PROMPT_ON_COMMANDS]
    
    # Block 4.2.12.5: Verify command's COMMAND_PROMPT_PARAMS
    registered_cmd = command._commands['login_cmd']
    assert 'username' in registered_cmd[COMMAND_PROMPT_PARAMS]
    
    # Block 4.2.12.6: Verify flag cleared
    assert param_def[param._PROMPT_AUTO_POPULATE] is False
```

**Test 4.2.13: Integration test for existing PROMPT_ON_COMMANDS relationship**

```gherkin
Scenario: Param with existing PROMPT_ON_COMMANDS adds to command list
  Given a param with PARAM_PROMPT and PROMPT_ON_COMMANDS including command
  And a command with that param in COMMAND_REQUIRED_PARAMS
  When add_command() is called
  Then command's COMMAND_PROMPT_PARAMS contains param name
  And param's PROMPT_ON_COMMANDS unchanged
  
  # Tests: Explicit timing relationships honoured
  # Validates: Framework respects pre-existing PROMPT_ON_COMMANDS
```

```python
# Test 4.2.13: Add to tests/test_command.py
def test_existing_prompt_on_commands_relationship_honoured():
    """Test that params with existing PROMPT_ON_COMMANDS add themselves to command list.
    
    This test verifies that when a param already has PROMPT_ON_COMMANDS configured
    (explicit timing, not auto-population), and a command lists it in COMMAND_REQUIRED_PARAMS,
    the framework adds the param to the command's COMMAND_PROMPT_PARAMS list without
    modifying the param's configuration. This behaviour is expected because explicit
    relationships override auto-population."""
    # Block 4.2.13.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.2.13.2: Register param with explicit timing
    param.add_param({
        PARAM_NAME: 'api_key',
        PARAM_PROMPT: 'API Key:',
        PROMPT_ON_COMMANDS: ['deploy_cmd']
    })
    
    # Block 4.2.13.3: Register command with required param
    command.add_command({
        COMMAND_NAME: 'deploy_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_REQUIRED_PARAMS: ['api_key']
    })
    
    # Block 4.2.13.4: Verify command list includes param
    registered_cmd = command._commands['deploy_cmd']
    assert 'api_key' in registered_cmd[COMMAND_PROMPT_PARAMS]
    
    # Block 4.2.13.5: Verify param list unchanged
    param_def = param._params['api_key']
    assert param_def[PROMPT_ON_COMMANDS] == ['deploy_cmd']
```

**Test 4.2.14: Integration test for multiple required params with mixed configurations**

```gherkin
Scenario: Command with multiple required params processes each correctly
  Given multiple params with different prompt configurations
  And a command requiring all of them
  When add_command() is called
  Then only prompt-enabled params added to COMMAND_PROMPT_PARAMS
  And relationships established appropriately for each
  
  # Tests: Batch processing of required params
  # Validates: Framework handles heterogeneous param configurations
```

```python
# Test 4.2.14: Add to tests/test_command.py
def test_multiple_required_params_with_mixed_configurations():
    """Test that commands with multiple required params process each configuration correctly.
    
    This test verifies that when a command has multiple required params with different
    configurations (some with prompts, some without; some auto-populate, some explicit),
    the framework processes each appropriately and builds the correct COMMAND_PROMPT_PARAMS list.
    This behaviour is expected because real applications mix different param types."""
    # Block 4.2.14.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.2.14.2: Register params with different configs
    param.add_param({
        PARAM_NAME: 'username',
        PARAM_PROMPT: 'Username:',
        param._PROMPT_AUTO_POPULATE: True
    })
    param.add_param({
        PARAM_NAME: 'password',
        PARAM_PROMPT: 'Password:',
        PROMPT_ON_COMMANDS: ['secure_cmd']
    })
    param.add_param({
        PARAM_NAME: 'config_file',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 4.2.14.3: Register command requiring all params
    command.add_command({
        COMMAND_NAME: 'secure_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_REQUIRED_PARAMS: ['username', 'password', 'config_file']
    })
    
    # Block 4.2.14.4: Verify only prompt params in list
    registered_cmd = command._commands['secure_cmd']
    assert 'username' in registered_cmd[COMMAND_PROMPT_PARAMS]
    assert 'password' in registered_cmd[COMMAND_PROMPT_PARAMS]
    assert 'config_file' not in registered_cmd[COMMAND_PROMPT_PARAMS]
```

**Code 4.2.15: Call reciprocal registration helper from add_command()**

```python
# Block 4.2.15: Add to src/spafw37/command.py in add_command() after inline command definitions processing
# Build reciprocal registration for required params
_build_reciprocal_registration_for_required_params(cmd)
```


[↑ Back to top](#table-of-contents)

---

**Step 4.3: Build reciprocal registration for explicit prompt params**

**File:** `src/spafw37/command.py`

Handle params explicitly listed in `COMMAND_PROMPT_PARAMS` that weren't processed via auto-population. When a command explicitly declares which params should prompt before it executes, ensure the reciprocal relationship is established on the param side. This handles cases where params are defined with explicit timing or where the command-param relationship isn't captured through `COMMAND_REQUIRED_PARAMS`.

**Algorithm:**

1. Check if command has `COMMAND_PROMPT_PARAMS` property (after inline processing has normalised it); if not present, return early
2. Get the command name from command definition
3. For each param name in the normalised `COMMAND_PROMPT_PARAMS` list:
   a. Look up param definition from `param._params` registry
   b. If param not found, raise `ValueError` indicating param must be registered before being referenced in `COMMAND_PROMPT_PARAMS`
   c. Verify param has `PARAM_PROMPT` property; if not present, raise `ValueError` indicating all params in `COMMAND_PROMPT_PARAMS` must have `PARAM_PROMPT` configured
   d. Check if param's `PROMPT_ON_COMMANDS` property is not set (is None or missing):
      - If not set: Initialize `PROMPT_ON_COMMANDS` as empty list
      - Add this command name to param's `PROMPT_ON_COMMANDS` list (if not already present)
      - This establishes the reciprocal relationship for explicitly declared prompt params
   e. If `PROMPT_ON_COMMANDS` was already set, verify this command name is in the list (consistency check)

This ensures all params in `COMMAND_PROMPT_PARAMS` are valid prompt-enabled params with proper bidirectional relationships established.

**Implementation order:**

1. Create `_build_reciprocal_registration_for_explicit_params(cmd)` helper function
2. Add call to helper in `add_command()` after reciprocal registration for required params
3. Add tests for param not found (raise ValueError)
4. Add tests for param without PARAM_PROMPT (raise ValueError)
5. Add tests for param without PROMPT_ON_COMMANDS (establish relationship)
6. Add tests for param with existing PROMPT_ON_COMMANDS (consistency check)

**Code 4.3.1: Leaf helper to ensure reciprocal link exists**

```python
# Block 4.3.1: Add to src/spafw37/command.py after _build_reciprocal_registration_for_required_params()
def _ensure_reciprocal_link_exists(param_def, cmd_name):
    """Ensure reciprocal link exists from param to command.
    
    Args:
        param_def: Parameter definition dictionary
        cmd_name: Command name string
    """
    # Block 4.3.1.1: Initialize PROMPT_ON_COMMANDS if not set
    if PROMPT_ON_COMMANDS not in param_def:
        param_def[PROMPT_ON_COMMANDS] = []
    
    # Block 4.3.1.2: Add command to param's list
    if cmd_name not in param_def[PROMPT_ON_COMMANDS]:
        param_def[PROMPT_ON_COMMANDS].append(cmd_name)
```

**Test 4.3.2: Unit test for ensuring reciprocal link**

```gherkin
Scenario: Reciprocal link established from param to command
  Given a param definition
  When _ensure_reciprocal_link_exists() is called with command name
  Then param's PROMPT_ON_COMMANDS contains command name
  And no duplicates created
  
  # Tests: Reciprocal link creation without duplicates
  # Validates: Helper initializes list if needed
```

```python
# Test 4.3.2: Add to tests/test_command.py
def test_ensure_reciprocal_link_exists():
    """Test that _ensure_reciprocal_link_exists() creates reciprocal link without duplicates.
    
    This test verifies that the helper function initializes PROMPT_ON_COMMANDS if needed,
    adds the command name, and prevents duplicate entries.
    This behaviour ensures clean bidirectional relationships."""
    # Block 4.3.2.1: Param without PROMPT_ON_COMMANDS
    param_def = {}
    command._ensure_reciprocal_link_exists(param_def, 'test_cmd')
    assert param_def[PROMPT_ON_COMMANDS] == ['test_cmd']
    
    # Block 4.3.2.2: Prevent duplicates
    command._ensure_reciprocal_link_exists(param_def, 'test_cmd')
    assert param_def[PROMPT_ON_COMMANDS] == ['test_cmd']
    
    # Block 4.3.2.3: Multiple commands
    command._ensure_reciprocal_link_exists(param_def, 'other_cmd')
    assert set(param_def[PROMPT_ON_COMMANDS]) == {'test_cmd', 'other_cmd'}
```

**Code 4.3.3: Mid-level helper to validate and link explicit param**

```python
# Block 4.3.3: Add to src/spafw37/command.py after _ensure_reciprocal_link_exists()
def _validate_and_link_explicit_param(cmd_name, param_name):
    """Validate and establish reciprocal link for explicitly declared prompt param.
    
    Args:
        cmd_name: Command name string
        param_name: Parameter name string
        
    Raises:
        ValueError: If param not found or missing PARAM_PROMPT property
    """
    # Block 4.3.3.1: Look up param definition
    param_def = param.get_param_by_name(param_name)
    if not param_def:
        raise ValueError(
            f"Param '{param_name}' in COMMAND_PROMPT_PARAMS must be registered first"
        )
    
    # Block 4.3.3.2: Verify PARAM_PROMPT exists
    if PARAM_PROMPT not in param_def:
        raise ValueError(
            f"Param '{param_name}' in COMMAND_PROMPT_PARAMS must have PARAM_PROMPT configured"
        )
    
    # Block 4.3.3.3: Establish or verify reciprocal link
    _ensure_reciprocal_link_exists(param_def, cmd_name)
```

**Test 4.3.4: Unit test for validating and linking explicit param**

```gherkin
Scenario: Validation catches missing param configuration
  Given param name not registered
  When _validate_and_link_explicit_param() is called
  Then ValueError is raised with appropriate message
  
  # Tests: Validation logic for explicit params
  # Validates: Helper enforces configuration requirements
```

```python
# Test 4.3.4: Add to tests/test_command.py
def test_validate_and_link_explicit_param_validation():
    """Test that _validate_and_link_explicit_param() validates param configuration.
    
    This test verifies that the helper function raises ValueError when param
    is not found or doesn't have PARAM_PROMPT configured.
    This behaviour prevents invalid command-param relationships."""
    # Block 4.3.4.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.3.4.2: Test param not found
    with pytest.raises(ValueError) as exc_info:
        command._validate_and_link_explicit_param('test_cmd', 'missing_param')
    assert 'must be registered first' in str(exc_info.value)
    
    # Block 4.3.4.3: Register param without PARAM_PROMPT
    param.add_param({
        PARAM_NAME: 'no_prompt_param',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 4.3.4.4: Test param without PARAM_PROMPT
    with pytest.raises(ValueError) as exc_info:
        command._validate_and_link_explicit_param('test_cmd', 'no_prompt_param')
    assert 'must have PARAM_PROMPT' in str(exc_info.value)
    
    # Block 4.3.4.5: Register valid param and verify link
    param.add_param({
        PARAM_NAME: 'valid_param',
        PARAM_PROMPT: 'Value:'
    })
    command._validate_and_link_explicit_param('test_cmd', 'valid_param')
    param_def = param._params['valid_param']
    assert 'test_cmd' in param_def[PROMPT_ON_COMMANDS]
```

**Code 4.3.5: Top-level helper to build reciprocal registration for explicit params**

```python
# Block 4.3.5: Add to src/spafw37/command.py after _validate_and_link_explicit_param()
def _build_reciprocal_registration_for_explicit_params(cmd):
    """Build reciprocal registration for params explicitly listed in COMMAND_PROMPT_PARAMS.
    
    Validates all params in COMMAND_PROMPT_PARAMS and establishes reciprocal relationships
    on the param side, ensuring bidirectional links exist.
    
    Args:
        cmd: Command definition dictionary
    """
    # Block 4.3.5.1: Check for prompt params list
    prompt_params = cmd.get(COMMAND_PROMPT_PARAMS, [])
    if not prompt_params:
        return
    
    # Block 4.3.5.2: Process each explicit param
    cmd_name = cmd.get(COMMAND_NAME)
    for param_name in prompt_params:
        _validate_and_link_explicit_param(cmd_name, param_name)
```

**Test 4.3.6: Integration test for param not found**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS with unregistered param raises error
  Given a command with COMMAND_PROMPT_PARAMS referencing non-existent param
  When add_command() is called
  Then ValueError is raised
  And error message indicates param must be registered first
  
  # Tests: Validation of param existence
  # Validates: Framework prevents dangling references
```

```python
# Test 4.3.6: Add to tests/test_command.py
def test_explicit_prompt_param_not_found_raises_error():
    """Test that COMMAND_PROMPT_PARAMS with unregistered param raises ValueError.
    
    This test verifies that when COMMAND_PROMPT_PARAMS references a param that hasn't been
    registered, the framework raises ValueError with a clear message. This behaviour is
    expected because all params must be registered before being referenced in commands."""
    # Block 4.3.5.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.3.5.2: Attempt to register command with unregistered param
    with pytest.raises(ValueError) as exc_info:
        command.add_command({
            COMMAND_NAME: 'login_cmd',
            COMMAND_ACTION: lambda: None,
            COMMAND_PROMPT_PARAMS: ['nonexistent_param']
        })
    
    # Block 4.3.5.3: Verify error message
    assert 'must be registered first' in str(exc_info.value).lower()
```

**Test 4.3.7: Integration test for param without PARAM_PROMPT**

```gherkin
Scenario: COMMAND_PROMPT_PARAMS with non-prompt param raises error
  Given a registered param without PARAM_PROMPT property
  And a command with COMMAND_PROMPT_PARAMS containing that param
  When add_command() is called
  Then ValueError is raised
  And error message indicates PARAM_PROMPT required
  
  # Tests: Validation of PARAM_PROMPT property
  # Validates: Framework enforces prompt configuration requirement
```

```python
# Test 4.3.7: Add to tests/test_command.py
def test_explicit_prompt_param_without_prompt_property_raises_error():
    """Test that COMMAND_PROMPT_PARAMS with non-prompt param raises ValueError.
    
    This test verifies that when COMMAND_PROMPT_PARAMS references a param that doesn't have
    PARAM_PROMPT configured, the framework raises ValueError. This behaviour is expected
    because only prompt-enabled params can be listed in COMMAND_PROMPT_PARAMS."""
    # Block 4.3.6.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.3.6.2: Register param without PARAM_PROMPT
    param.add_param({
        PARAM_NAME: 'config_file',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 4.3.6.3: Attempt to register command
    with pytest.raises(ValueError) as exc_info:
        command.add_command({
            COMMAND_NAME: 'process_cmd',
            COMMAND_ACTION: lambda: None,
            COMMAND_PROMPT_PARAMS: ['config_file']
        })
    
    # Block 4.3.6.4: Verify error message
    assert 'must have param_prompt configured' in str(exc_info.value).lower()
```

**Test 4.3.8: Integration test for param without PROMPT_ON_COMMANDS**

```gherkin
Scenario: Explicit param without PROMPT_ON_COMMANDS gets reciprocal link
  Given a param with PARAM_PROMPT but no PROMPT_ON_COMMANDS
  And a command with COMMAND_PROMPT_PARAMS containing that param
  When add_command() is called
  Then param's PROMPT_ON_COMMANDS is initialised
  And command name is added to param's list
  
  # Tests: Reciprocal link establishment for new relationships
  # Validates: Framework creates bidirectional relationship
```

```python
# Test 4.3.8: Add to tests/test_command.py
def test_explicit_param_without_prompt_on_commands_establishes_relationship():
    """Test that explicit params without PROMPT_ON_COMMANDS get reciprocal link established.
    
    This test verifies that when COMMAND_PROMPT_PARAMS references a param that doesn't have
    PROMPT_ON_COMMANDS configured, the framework initialises the property and adds the
    command name. This behaviour is expected because explicit declarations establish
    relationships even without auto-population."""
    # Block 4.3.8.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.3.8.2: Register param without PROMPT_ON_COMMANDS
    param.add_param({
        PARAM_NAME: 'secret_key',
        PARAM_PROMPT: 'Secret Key:'
    })
    
    # Block 4.3.8.3: Register command with explicit param
    command.add_command({
        COMMAND_NAME: 'secure_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PROMPT_PARAMS: ['secret_key']
    })
    
    # Block 4.3.8.4: Verify reciprocal link established
    param_def = param._params['secret_key']
    assert PROMPT_ON_COMMANDS in param_def
    assert 'secure_cmd' in param_def[PROMPT_ON_COMMANDS]
```

**Test 4.3.9: Integration test for param with existing PROMPT_ON_COMMANDS**

```gherkin
Scenario: Explicit param with existing PROMPT_ON_COMMANDS verified consistent
  Given a param with PARAM_PROMPT and PROMPT_ON_COMMANDS including command
  And a command with COMMAND_PROMPT_PARAMS containing that param
  When add_command() is called
  Then command registers successfully
  And param's PROMPT_ON_COMMANDS includes command (no change)
  
  # Tests: Consistency check for pre-existing relationships
  # Validates: Framework verifies but doesn't duplicate
```

```python
# Test 4.3.8: Add to tests/test_command.py
def test_explicit_param_with_existing_prompt_on_commands_consistency():
    """Test that explicit params with existing PROMPT_ON_COMMANDS maintain consistency.
    
    This test verifies that when COMMAND_PROMPT_PARAMS references a param that already has
    PROMPT_ON_COMMANDS configured including this command, the framework verifies consistency
    without duplicating the entry. This behaviour is expected because the relationship
    may have been established earlier (e.g., via auto-population or prior explicit declaration)."""
    # Block 4.3.8.1: Clear existing state
    command._commands = {}
    param._params = {}
    
    # Block 4.3.8.2: Register param with existing relationship
    param.add_param({
        PARAM_NAME: 'token',
    # Block 4.3.9.2: Register param with existing relationship
    param.add_param({
        PARAM_NAME: 'token',
        PARAM_PROMPT: 'Token:',
        PROMPT_ON_COMMANDS: ['auth_cmd']
    })
    
    # Block 4.3.9.3: Register command with explicit param
    command.add_command({
        COMMAND_NAME: 'auth_cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PROMPT_PARAMS: ['token']
    })
    
    # Block 4.3.9.4: Verify no duplication
    param_def = param._params['token']
    assert param_def[PROMPT_ON_COMMANDS].count('auth_cmd') == 1
```

**Code 4.3.10: Call reciprocal registration helper from add_command()**

```python
# Block 4.3.10: Add to src/spafw37/command.py in add_command() after _build_reciprocal_registration_for_required_params()
# Build reciprocal registration for explicit prompt params
_build_reciprocal_registration_for_explicit_params(cmd)
```

[↑ Back to top](#table-of-contents)

---

#### Phase 2: Prompt Execution

**Step 5.1: Implement handler resolution helper**

**File:** `src/spafw37/param.py`

Implement the three-tier handler resolution system that provides fine-grained control whilst maintaining sensible defaults. This enables per-param customisation (e.g., GUI prompt for sensitive data), application-wide replacement (e.g., automated testing), and default behaviour (terminal input) without configuration.

**Algorithm:**

1. Check if param definition has `PARAM_PROMPT_HANDLER` property set:
   - If present and not None: return this handler (param-level override takes highest precedence)
2. Check module-level `_global_prompt_handler` variable:
   - If not None: return this handler (global override set via `set_prompt_handler()` API)
3. Return default handler:
   - Import and return `input_prompt.prompt_for_value` function (built-in terminal prompting)

**Precedence order:** Param-specific → Global → Default

This design allows:
- Individual params to use custom handlers (e.g., file picker, password masking)
- Applications to replace all prompts globally (e.g., GUI wrapper, test automation)
- Zero-configuration usage with sensible terminal input defaults

**Implementation order:**

1. Add module-level `_global_prompt_handler` variable to `param.py`
2. Add public `set_prompt_handler()` API function
3. Create `_get_prompt_handler()` helper function
4. Add regression test for default behaviour without handlers
5. Add test for param-level handler override
6. Add test for global handler override
7. Add test for precedence (param-level overrides global)

**Module-level imports for tests/test_param_prompts.py:**

```python
# Module-level imports for tests/test_param_prompts.py
from spafw37 import param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_HANDLER,
    PARAM_TYPE,
    PARAM_TYPE_TEXT
)
import pytest
```

**Code 5.1.1: Module-level global handler variable**

```python
# Block 5.1.1: Add to src/spafw37/param.py after _params registry
_global_prompt_handler = None
```

**Code 5.1.2: Public API to set global prompt handler**

```python
# Block 5.1.2: Add to src/spafw37/param.py after module-level variables
def set_prompt_handler(handler):
    """Set global prompt handler for all params.
    
    This function allows applications to replace the default terminal-based
    prompt handler with a custom implementation (e.g., GUI dialogue, automated
    testing stub, API-based input source).
    
    Args:
        handler: Callable taking param definition dict, returning string value.
                 Set to None to restore default behaviour.
    """
    # Block 5.1.2.1: Update global handler variable
    global _global_prompt_handler
    _global_prompt_handler = handler
```

**Test 5.1.3: Regression test for default handler without overrides**

```gherkin
Scenario: Default handler used when no overrides configured
  Given no global handler set
  And a param without PARAM_PROMPT_HANDLER property
  When _get_prompt_handler() is called
  Then the default input_prompt.prompt_for_value handler is returned
  
  # Tests: Default behaviour without configuration
  # Validates: Framework provides sensible defaults
```

```python
# Test 5.1.3: Add to tests/test_param_prompts.py
def test_default_handler_without_overrides():
    """Test that _get_prompt_handler() returns default handler when no overrides configured.
    
    This regression test verifies that when neither param-level nor global handlers are set,
    the framework returns the built-in input_prompt.prompt_for_value function.
    This behaviour is expected because the framework must provide default terminal-based
    prompting without requiring configuration."""
    # Block 5.1.3.1: Clear global handler
    param._global_prompt_handler = None
    
    # Block 5.1.3.2: Create param without handler override
    param_def = {PARAM_NAME: 'test_param', PARAM_PROMPT: 'Enter value:'}
    
    # Block 5.1.3.3: Get handler
    handler = param._get_prompt_handler(param_def)
    
    # Block 5.1.3.4: Verify default handler returned
    from spafw37 import input_prompt
    assert handler == input_prompt.prompt_for_value
```

**Code 5.1.4: Handler resolution helper**

```python
# Block 5.1.4: Add to src/spafw37/param.py after set_prompt_handler()
def _get_prompt_handler(param_def):
    """Resolve prompt handler for param using three-tier precedence.
    
    Resolution order: param-level → global → default
    
    Args:
        param_def: Parameter definition dictionary
        
    Returns:
        Callable prompt handler function
    """
    # Block 5.1.4.1: Check param-level handler
    if PARAM_PROMPT_HANDLER in param_def and param_def[PARAM_PROMPT_HANDLER] is not None:
        return param_def[PARAM_PROMPT_HANDLER]
    
    # Block 5.1.4.2: Check global handler
    if _global_prompt_handler is not None:
        return _global_prompt_handler
    
    # Block 5.1.4.3: Return default handler
    from spafw37 import input_prompt
    return input_prompt.prompt_for_value
```

**Test 5.1.5: Param-level handler override**

```gherkin
Scenario: Param-level handler overrides default
  Given no global handler set
  And a param with custom PARAM_PROMPT_HANDLER
  When _get_prompt_handler() is called
  Then the param-specific handler is returned
  
  # Tests: Param-level customisation
  # Validates: Individual params can use custom handlers
```

```python
# Test 5.1.5: Add to tests/test_param_prompts.py
def test_param_level_handler_override():
    """Test that _get_prompt_handler() returns param-level handler when configured.
    
    This test verifies that when a param has PARAM_PROMPT_HANDLER property set,
    that custom handler is returned instead of the default.
    This behaviour is expected because params may need specialised input methods
    (e.g., file picker dialogue, password masking)."""
    # Block 5.1.5.1: Clear global handler
    param._global_prompt_handler = None
    
    # Block 5.1.5.2: Define custom handler
    def custom_handler(param_def):
        return 'custom_value'
    
    # Block 5.1.5.3: Create param with handler
    param_def = {
        PARAM_NAME: 'test_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_HANDLER: custom_handler
    }
    
    # Block 5.1.5.4: Verify custom handler returned
    handler = param._get_prompt_handler(param_def)
    assert handler == custom_handler
```

**Test 5.1.6: Global handler override**

```gherkin
Scenario: Global handler overrides default for all params
  Given a global handler set via set_prompt_handler()
  And a param without PARAM_PROMPT_HANDLER property
  When _get_prompt_handler() is called
  Then the global handler is returned
  
  # Tests: Application-wide handler replacement
  # Validates: All prompts can use custom handler
```

```python
# Test 5.1.6: Add to tests/test_param_prompts.py
def test_global_handler_override():
    """Test that _get_prompt_handler() returns global handler when set.
    
    This test verifies that set_prompt_handler() affects handler resolution for all params
    that don't have param-level overrides.
    This behaviour is expected because applications may need to replace all prompts
    (e.g., GUI wrapper, automated testing)."""
    # Block 5.1.6.1: Define and set global handler
    def global_handler(param_def):
        return 'global_value'
    
    param.set_prompt_handler(global_handler)
    
    # Block 5.1.6.2: Create param without handler override
    param_def = {PARAM_NAME: 'test_param', PARAM_PROMPT: 'Enter value:'}
    
    # Block 5.1.6.3: Verify global handler returned
    handler = param._get_prompt_handler(param_def)
    assert handler == global_handler
    
    # Block 5.1.6.4: Clean up
    param.set_prompt_handler(None)
```

**Test 5.1.7: Param-level handler takes precedence over global**

```gherkin
Scenario: Param-level handler overrides global handler
  Given a global handler set via set_prompt_handler()
  And a param with custom PARAM_PROMPT_HANDLER
  When _get_prompt_handler() is called
  Then the param-specific handler is returned (not global)
  
  # Tests: Precedence order enforcement
  # Validates: Param-level customisation wins over global
```

```python
# Test 5.1.7: Add to tests/test_param_prompts.py
def test_param_handler_precedence_over_global():
    """Test that param-level handler takes precedence over global handler.
    
    This test verifies the three-tier precedence system: when both param-level and
    global handlers are set, the param-level handler is used.
    This behaviour is expected because param-specific customisation must be able to
    override application-wide settings for special cases."""
    # Block 5.1.7.1: Define handlers
    def global_handler(param_def):
        return 'global_value'
    
    def param_handler(param_def):
        return 'param_value'
    
    # Block 5.1.7.2: Set global handler
    param.set_prompt_handler(global_handler)
    
    # Block 5.1.7.3: Create param with handler
    param_def = {
        PARAM_NAME: 'test_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_HANDLER: param_handler
    }
    
    # Block 5.1.7.4: Verify param handler takes precedence
    handler = param._get_prompt_handler(param_def)
    assert handler == param_handler
    
    # Block 5.1.7.5: Clean up
    param.set_prompt_handler(None)
```

[↑ Back to top](#table-of-contents)

---

**Step 5.2: Implement prompt timing check helper**

**File:** `src/spafw37/param.py`

Implement the decision logic that determines whether a param should prompt in the current context. This consolidates all timing, repeat, and override checks into a single helper that enforces the architectural decisions: CLI values prevent prompting, timing controls when prompts appear, repeat behaviour controls frequency.

**Algorithm:**

1. Check if `check_value` parameter is True (default):
   - Get current param value from param registry
   - If value is set (not None and not empty): return False (CLI override - skip prompt)
2. Check param's `PARAM_PROMPT_TIMING` property:
   - If `PROMPT_ON_START`:
     - If `command_name` parameter is None (calling from start-of-execution context): return True
     - If `command_name` is provided (calling from command execution context): return False (wrong timing)
   - If `PROMPT_ON_COMMAND`:
     - If `command_name` parameter is None: return False (need command context)
     - Check if `command_name` is in param's `PROMPT_ON_COMMANDS` list:
       - If not in list: return False (prompt not configured for this command)
       - If in list: proceed to repeat behaviour check
3. Check param's `PARAM_PROMPT_REPEAT` property (only relevant for `PROMPT_ON_COMMAND` timing):
   - If `PROMPT_REPEAT_ALWAYS`: return True (always prompt, regardless of previous prompts)
   - If `PROMPT_REPEAT_IF_BLANK`: check current param value; return True if blank, False if set
   - If `PROMPT_REPEAT_NEVER`: check if param name in module-level `_prompted_params` set; return False if already prompted, True if first time
4. Default: return True (prompt should execute)

This function is called from two contexts: start-of-execution (command_name=None) and before-command-execution (command_name="cmd").

**Implementation order:**

1. Add module-level `_prompted_params` set to track prompts
2. Create leaf helper to check if value is set (CLI override check)
3. Create leaf helper to check timing match
4. Create leaf helper to check repeat behaviour
5. Create top-level `_should_prompt_param()` orchestration function
6. Add tests for CLI override preventing prompts
7. Add tests for PROMPT_ON_START timing
8. Add tests for PROMPT_ON_COMMAND timing
9. Add tests for all three repeat modes
10. Add tests for wrong timing context

**Module-level imports for tests/test_param_prompts.py (Step 5.2):**

```python
# Additional module-level imports for Step 5.2 tests in tests/test_param_prompts.py
from spafw37.constants.param import (
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT,
    PROMPT_ON_START,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
    PROMPT_REPEAT_ALWAYS,
    PROMPT_REPEAT_IF_BLANK,
    PROMPT_REPEAT_NEVER,
    PARAM_REQUIRED
)
```

**Code 5.2.1: Module-level prompted params tracking set**

```python
# Block 5.2.1: Add to src/spafw37/param.py after _global_prompt_handler
_prompted_params = set()
```

**Code 5.2.2: Leaf helper to check if param value is set**

```python
# Block 5.2.2: Add to src/spafw37/param.py after _get_prompt_handler()
def _param_value_is_set(param_name):
    """Check if param has a value set (CLI override or previous prompt).
    
    Args:
        param_name: Parameter name string
        
    Returns:
        True if value is set (not None and not empty), False otherwise
    """
    # Block 5.2.2.1: Get param value
    param_value = get_param_value(param_name)
    
    # Block 5.2.2.2: Check if set
    return param_value is not None and param_value != ''
```

**Test 5.2.3: Unit test for param value set returns True**

```gherkin
Scenario: Param with value set returns True
  Given a param with a non-empty value
  When _param_value_is_set() is called
  Then returns True
  
  # Tests: Value detection for set params
  # Validates: Framework detects CLI-provided values
```

```python
# Test 5.2.3: Add to tests/test_param_prompts.py
def test_param_value_is_set_returns_true():
    """Test that _param_value_is_set() returns True when param has a value.
    
    This test verifies the helper correctly identifies params with values set.
    This behaviour is essential for CLI override logic - prompts should skip when
    user already provided a value via command line."""
    # Block 5.2.3.1: Clear state
    param._params = {}
    
    # Block 5.2.3.2: Register param and set value
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param_value('test_param', 'some_value')
    
    # Block 5.2.3.3: Verify returns True
    assert param._param_value_is_set('test_param') is True
```

**Test 5.2.4: Unit test for param value set returns False for None**

```gherkin
Scenario: Param with None value returns False
  Given a param with None value
  When _param_value_is_set() is called
  Then returns False
  
  # Tests: Value detection for unset params (None)
  # Validates: Framework treats None as unset
```

```python
# Test 5.2.4: Add to tests/test_param_prompts.py
def test_param_value_is_set_returns_false_for_none():
    """Test that _param_value_is_set() returns False when param value is None.
    
    This test verifies the helper correctly identifies params without values.
    This behaviour is expected because None indicates no value was provided."""
    # Block 5.2.4.1: Clear state
    param._params = {}
    
    # Block 5.2.4.2: Register param with None value
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param_value('test_param', None)
    
    # Block 5.2.4.3: Verify returns False
    assert param._param_value_is_set('test_param') is False
```

**Test 5.2.5: Unit test for param value set returns False for empty string**

```gherkin
Scenario: Param with empty string returns False
  Given a param with empty string value
  When _param_value_is_set() is called
  Then returns False
  
  # Tests: Value detection for empty strings
  # Validates: Framework treats empty string as unset
```

```python
# Test 5.2.5: Add to tests/test_param_prompts.py
def test_param_value_is_set_returns_false_for_empty_string():
    """Test that _param_value_is_set() returns False when param value is empty string.
    
    This test verifies the helper treats empty strings as unset values.
    This behaviour is expected because empty string indicates no meaningful value."""
    # Block 5.2.5.1: Clear state
    param._params = {}
    
    # Block 5.2.5.2: Register param with empty string
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param_value('test_param', '')
    
    # Block 5.2.5.3: Verify returns False
    assert param._param_value_is_set('test_param') is False
```

**Code 5.2.4: Leaf helper to check timing context match**

```python
# Block 5.2.4: Add to src/spafw37/param.py after _param_value_is_set()
def _timing_matches_context(param_def, command_name):
    """Check if param's timing configuration matches execution context.
    
    Args:
        param_def: Parameter definition dictionary
        command_name: Command name string or None for start-of-execution context
        
    Returns:
        True if timing matches context, False otherwise
    """
    # Block 5.2.4.1: Get timing mode
    timing = param_def.get(PARAM_PROMPT_TIMING, PROMPT_ON_START)
    
    # Block 5.2.4.2: Check PROMPT_ON_START timing
    if timing == PROMPT_ON_START:
        return command_name is None
    
    # Block 5.2.4.3: Check PROMPT_ON_COMMAND timing
    if timing == PROMPT_ON_COMMAND:
        if command_name is None:
            return False
        prompt_commands = param_def.get(PROMPT_ON_COMMANDS, [])
        return command_name in prompt_commands
    
    # Block 5.2.4.4: Unknown timing mode
    return False
```

**Test 5.2.6: Unit test for PROMPT_ON_START matches None context**

```gherkin
Scenario: PROMPT_ON_START matches None context
  Given a param with PROMPT_ON_START timing
  When _timing_matches_context() is called with None context
  Then returns True
  
  # Tests: Start timing matches start context
  # Validates: Framework identifies start-timing prompts
```

```python
# Test 5.2.6: Add to tests/test_param_prompts.py
def test_timing_matches_context_start_with_none():
    """Test that _timing_matches_context() returns True for PROMPT_ON_START with None context.
    
    This test verifies PROMPT_ON_START timing matches the start-of-execution context.
    This behaviour ensures start-timing prompts appear at application startup."""
    from spafw37.constants.param import PARAM_PROMPT_TIMING, PROMPT_ON_START
    
    # Block 5.2.6.1: Create param with PROMPT_ON_START
    param_def = {PARAM_PROMPT_TIMING: PROMPT_ON_START}
    
    # Block 5.2.6.2: Verify matches None context
    assert param._timing_matches_context(param_def, None) is True
```

**Test 5.2.7: Unit test for PROMPT_ON_START does not match command context**

```gherkin
Scenario: PROMPT_ON_START does not match command context
  Given a param with PROMPT_ON_START timing
  When _timing_matches_context() is called with command name
  Then returns False
  
  # Tests: Start timing rejects command context
  # Validates: Framework prevents start prompts during command execution
```

```python
# Test 5.2.7: Add to tests/test_param_prompts.py
def test_timing_matches_context_start_with_command():
    """Test that _timing_matches_context() returns False for PROMPT_ON_START with command context.
    
    This test verifies PROMPT_ON_START timing does not match command execution context.
    This behaviour ensures start-timing prompts don't appear during command execution."""
    from spafw37.constants.param import PARAM_PROMPT_TIMING, PROMPT_ON_START
    
    # Block 5.2.7.1: Create param with PROMPT_ON_START
    param_def = {PARAM_PROMPT_TIMING: PROMPT_ON_START}
    
    # Block 5.2.7.2: Verify rejects command context
    assert param._timing_matches_context(param_def, 'some_cmd') is False
```

**Test 5.2.8: Unit test for PROMPT_ON_COMMAND does not match None context**

```gherkin
Scenario: PROMPT_ON_COMMAND does not match None context
  Given a param with PROMPT_ON_COMMAND timing
  When _timing_matches_context() is called with None context
  Then returns False
  
  # Tests: Command timing rejects start context
  # Validates: Framework prevents command prompts at startup
```

```python
# Test 5.2.8: Add to tests/test_param_prompts.py
def test_timing_matches_context_command_with_none():
    """Test that _timing_matches_context() returns False for PROMPT_ON_COMMAND with None context.
    
    This test verifies PROMPT_ON_COMMAND timing does not match start-of-execution context.
    This behaviour ensures command-timing prompts don't appear at application startup."""
    from spafw37.constants.param import (
        PARAM_PROMPT_TIMING,
        PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS
    )
    
    # Block 5.2.8.1: Create param with PROMPT_ON_COMMAND
    param_def = {
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']
    }
    
    # Block 5.2.8.2: Verify rejects None context
    assert param._timing_matches_context(param_def, None) is False
```

**Test 5.2.9: Unit test for PROMPT_ON_COMMAND matches configured command**

```gherkin
Scenario: PROMPT_ON_COMMAND matches configured command
  Given a param with PROMPT_ON_COMMAND timing for specific commands
  When _timing_matches_context() is called with matching command
  Then returns True
  
  # Tests: Command timing matches configured command
  # Validates: Framework identifies command-timing prompts
```

```python
# Test 5.2.9: Add to tests/test_param_prompts.py
def test_timing_matches_context_command_with_matching():
    """Test that _timing_matches_context() returns True for PROMPT_ON_COMMAND with matching command.
    
    This test verifies PROMPT_ON_COMMAND timing matches when command is in PROMPT_ON_COMMANDS list.
    This behaviour ensures command-timing prompts appear before configured commands."""
    from spafw37.constants.param import (
        PARAM_PROMPT_TIMING,
        PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS
    )
    
    # Block 5.2.9.1: Create param with PROMPT_ON_COMMAND
    param_def = {
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']
    }
    
    # Block 5.2.9.2: Verify matches configured command
    assert param._timing_matches_context(param_def, 'cmd1') is True
```

**Test 5.2.10: Unit test for PROMPT_ON_COMMAND does not match non-configured command**

```gherkin
Scenario: PROMPT_ON_COMMAND does not match non-configured command
  Given a param with PROMPT_ON_COMMAND timing for specific commands
  When _timing_matches_context() is called with non-matching command
  Then returns False
  
  # Tests: Command timing rejects non-configured command
  # Validates: Framework only prompts for configured commands
```

```python
# Test 5.2.10: Add to tests/test_param_prompts.py
def test_timing_matches_context_command_with_non_matching():
    """Test that _timing_matches_context() returns False for PROMPT_ON_COMMAND with non-matching command.
    
    This test verifies PROMPT_ON_COMMAND timing rejects commands not in PROMPT_ON_COMMANDS list.
    This behaviour ensures command-timing prompts only appear for configured commands."""
    from spafw37.constants.param import (
        PARAM_PROMPT_TIMING,
        PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS
    )
    
    # Block 5.2.10.1: Create param with PROMPT_ON_COMMAND
    param_def = {
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']
    }
    
    # Block 5.2.10.2: Verify rejects non-configured command
    assert param._timing_matches_context(param_def, 'cmd3') is False
```

**Code 5.2.6: Leaf helper to check repeat behaviour**

```python
# Block 5.2.6: Add to src/spafw37/param.py after _timing_matches_context()
def _should_repeat_prompt(param_def, param_name):
    """Check if param should repeat prompt based on repeat behaviour configuration.
    
    Args:
        param_def: Parameter definition dictionary
        param_name: Parameter name string
        
    Returns:
        True if should prompt again, False otherwise
    """
    # Block 5.2.6.1: Get repeat mode
    repeat_mode = param_def.get(PARAM_PROMPT_REPEAT, PROMPT_REPEAT_ALWAYS)
    
    # Block 5.2.6.2: PROMPT_REPEAT_ALWAYS
    if repeat_mode == PROMPT_REPEAT_ALWAYS:
        return True
    
    # Block 5.2.6.3: PROMPT_REPEAT_IF_BLANK
    if repeat_mode == PROMPT_REPEAT_IF_BLANK:
        return not _param_value_is_set(param_name)
    
    # Block 5.2.6.4: PROMPT_REPEAT_NEVER
    if repeat_mode == PROMPT_REPEAT_NEVER:
        return param_name not in _prompted_params
    
    # Block 5.2.6.5: Unknown repeat mode
    return True
```

**Test 5.2.11: Unit test for PROMPT_REPEAT_ALWAYS**

```gherkin
Scenario: PROMPT_REPEAT_ALWAYS returns True
  Given a param with PROMPT_REPEAT_ALWAYS
  When _should_repeat_prompt() is called
  Then returns True
  
  # Tests: Always repeat mode
  # Validates: Framework always repeats prompts
```

```python
# Test 5.2.11: Add to tests/test_param_prompts.py
def test_should_repeat_prompt_always():
    """Test that _should_repeat_prompt() returns True for PROMPT_REPEAT_ALWAYS.
    
    This test verifies PROMPT_REPEAT_ALWAYS mode always allows prompt repetition.
    This behaviour enables prompts to repeat every time for cycle scenarios."""
    from spafw37.constants.param import PARAM_PROMPT_REPEAT, PROMPT_REPEAT_ALWAYS
    
    # Block 5.2.11.1: Create param with PROMPT_REPEAT_ALWAYS
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_ALWAYS}
    
    # Block 5.2.11.2: Verify returns True
    assert param._should_repeat_prompt(param_def, 'test_param') is True
```

**Test 5.2.12: Unit test for PROMPT_REPEAT_IF_BLANK with value**

```gherkin
Scenario: PROMPT_REPEAT_IF_BLANK returns False when value set
  Given a param with PROMPT_REPEAT_IF_BLANK and value set
  When _should_repeat_prompt() is called
  Then returns False
  
  # Tests: If-blank mode with value
  # Validates: Framework skips prompts when value exists
```

```python
# Test 5.2.12: Add to tests/test_param_prompts.py
def test_should_repeat_prompt_if_blank_with_value():
    """Test that _should_repeat_prompt() returns False for PROMPT_REPEAT_IF_BLANK when value set.
    
    This test verifies PROMPT_REPEAT_IF_BLANK mode prevents repetition when param has value.
    This behaviour allows prompts to skip when user has already provided a value."""
    from spafw37.constants.param import PARAM_PROMPT_REPEAT, PROMPT_REPEAT_IF_BLANK
    
    # Block 5.2.12.1: Clear state
    param._params = {}
    
    # Block 5.2.12.2: Register param with value
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param_value('test_param', 'value')
    
    # Block 5.2.12.3: Verify returns False
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_IF_BLANK}
    assert param._should_repeat_prompt(param_def, 'test_param') is False
```

**Test 5.2.13: Unit test for PROMPT_REPEAT_IF_BLANK without value**

```gherkin
Scenario: PROMPT_REPEAT_IF_BLANK returns True when value blank
  Given a param with PROMPT_REPEAT_IF_BLANK and no value
  When _should_repeat_prompt() is called
  Then returns True
  
  # Tests: If-blank mode without value
  # Validates: Framework prompts when value is blank
```

```python
# Test 5.2.13: Add to tests/test_param_prompts.py
def test_should_repeat_prompt_if_blank_without_value():
    """Test that _should_repeat_prompt() returns True for PROMPT_REPEAT_IF_BLANK when value blank.
    
    This test verifies PROMPT_REPEAT_IF_BLANK mode allows repetition when param has no value.
    This behaviour enables prompts to repeat until user provides a value."""
    from spafw37.constants.param import PARAM_PROMPT_REPEAT, PROMPT_REPEAT_IF_BLANK
    
    # Block 5.2.13.1: Clear state
    param._params = {}
    
    # Block 5.2.13.2: Register param without value
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param_value('test_param', None)
    
    # Block 5.2.13.3: Verify returns True
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_IF_BLANK}
    assert param._should_repeat_prompt(param_def, 'test_param') is True
```

**Test 5.2.14: Unit test for PROMPT_REPEAT_NEVER first time**

```gherkin
Scenario: PROMPT_REPEAT_NEVER returns True for first prompt
  Given a param with PROMPT_REPEAT_NEVER not yet prompted
  When _should_repeat_prompt() is called
  Then returns True
  
  # Tests: Never repeat mode first time
  # Validates: Framework allows first prompt
```

```python
# Test 5.2.14: Add to tests/test_param_prompts.py
def test_should_repeat_prompt_never_first_time():
    """Test that _should_repeat_prompt() returns True for PROMPT_REPEAT_NEVER on first call.
    
    This test verifies PROMPT_REPEAT_NEVER mode allows the first prompt.
    This behaviour enables one-time prompts that don't repeat."""
    from spafw37.constants.param import PARAM_PROMPT_REPEAT, PROMPT_REPEAT_NEVER
    
    # Block 5.2.14.1: Clear state
    param._prompted_params = set()
    
    # Block 5.2.14.2: Verify returns True first time
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER}
    assert param._should_repeat_prompt(param_def, 'test_param') is True
```

**Test 5.2.15: Unit test for PROMPT_REPEAT_NEVER after prompt**

```gherkin
Scenario: PROMPT_REPEAT_NEVER returns False after prompt
  Given a param with PROMPT_REPEAT_NEVER already prompted
  When _should_repeat_prompt() is called
  Then returns False
  
  # Tests: Never repeat mode subsequent call
  # Validates: Framework prevents repeat prompts
```

```python
# Test 5.2.15: Add to tests/test_param_prompts.py
def test_should_repeat_prompt_never_after_prompt():
    """Test that _should_repeat_prompt() returns False for PROMPT_REPEAT_NEVER after prompting.
    
    This test verifies PROMPT_REPEAT_NEVER mode prevents repetition after first prompt.
    This behaviour ensures prompts never repeat once executed."""
    from spafw37.constants.param import PARAM_PROMPT_REPEAT, PROMPT_REPEAT_NEVER
    
    # Block 5.2.15.1: Clear state and add to prompted set
    param._prompted_params = set()
    param._prompted_params.add('test_param')
    
    # Block 5.2.15.2: Verify returns False
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER}
    assert param._should_repeat_prompt(param_def, 'test_param') is False
```

**Code 5.2.8: Top-level prompt timing check orchestration**

```python
# Block 5.2.8: Add to src/spafw37/param.py after _should_repeat_prompt()
def _should_prompt_param(param_def, command_name=None, check_value=True):
    """Determine whether param should prompt in current context.
    
    Consolidates CLI override, timing, and repeat behaviour checks.
    
    Args:
        param_def: Parameter definition dictionary
        command_name: Command name for command-timing context, None for start-timing
        check_value: If True, skip prompt if param already has value (CLI override)
        
    Returns:
        True if prompt should execute, False otherwise
    """
    # Block 5.2.8.1: Check CLI override
    param_name = param_def.get(PARAM_NAME)
    if check_value and _param_value_is_set(param_name):
        return False
    
    # Block 5.2.8.2: Check timing matches context
    if not _timing_matches_context(param_def, command_name):
        return False
    
    # Block 5.2.8.3: Check repeat behaviour
    return _should_repeat_prompt(param_def, param_name)
```

**Test 5.2.16: Integration test for CLI override preventing prompt**

```gherkin
Scenario: CLI-provided value prevents prompting
  Given a param with PARAM_PROMPT configured
  And param value set via CLI argument
  When _should_prompt_param() is called
  Then returns False (skip prompt)
  
  # Tests: CLI override mechanism
  # Validates: Command-line arguments take precedence
```

```python
# Test 5.2.16: Add to tests/test_param_prompts.py
def test_cli_override_prevents_prompt():
    """Test that _should_prompt_param() returns False when param value already set.
    
    This integration test verifies that CLI-provided values prevent prompting,
    regardless of timing or repeat configuration.
    This behaviour is expected because command-line arguments must take precedence
    over interactive prompts."""
    from spafw37.constants.param import PROMPT_ON_START
    
    # Block 5.2.16.1: Clear state
    param._params = {}
    
    # Block 5.2.16.2: Register param with value
    param.add_param({
        PARAM_NAME: 'username',
        PARAM_PROMPT: 'Username:',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    param.set_param_value('username', 'cli_user')
    
    # Block 5.2.16.3: Verify prompt skipped
    param_def = param._params['username']
    assert param._should_prompt_param(param_def, None) is False
```

**Test 5.2.17: Integration test for PROMPT_ON_START timing**

```gherkin
Scenario: PROMPT_ON_START param prompts at start, not during commands
  Given a param with PROMPT_ON_START timing
  When _should_prompt_param() is called with command_name=None
  Then returns True
  When called with command_name="some_cmd"
  Then returns False
  
  # Tests: Start timing enforcement
  # Validates: Prompts appear at correct phase
```

```python
# Test 5.2.17: Add to tests/test_param_prompts.py
def test_prompt_on_start_timing():
    """Test that _should_prompt_param() enforces PROMPT_ON_START timing.
    
    This integration test verifies params with PROMPT_ON_START timing prompt when
    called from start context (command_name=None) but not from command context.
    This behaviour ensures prompts appear at the correct execution phase."""
    from spafw37.constants.param import PARAM_PROMPT_TIMING, PROMPT_ON_START
    
    # Block 5.2.17.1: Clear state
    param._params = {}
    
    # Block 5.2.17.2: Register param with PROMPT_ON_START
    param.add_param({
        PARAM_NAME: 'api_key',
        PARAM_PROMPT: 'API Key:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 5.2.17.3: Verify prompts at start
    param_def = param._params['api_key']
    assert param._should_prompt_param(param_def, None, check_value=False) is True
    
    # Block 5.2.17.4: Verify skipped during commands
    assert param._should_prompt_param(param_def, 'deploy', check_value=False) is False
```

**Test 5.2.18: Integration test for PROMPT_ON_COMMAND timing**

```gherkin
Scenario: PROMPT_ON_COMMAND param prompts before specified commands only
  Given a param with PROMPT_ON_COMMAND timing for specific commands
  When _should_prompt_param() is called with matching command
  Then returns True
  When called with non-matching command
  Then returns False
  
  # Tests: Command timing enforcement
  # Validates: Prompts appear before correct commands
```

```python
# Test 5.2.18: Add to tests/test_param_prompts.py
def test_prompt_on_command_timing():
    """Test that _should_prompt_param() enforces PROMPT_ON_COMMAND timing.
    
    This integration test verifies params with PROMPT_ON_COMMAND timing prompt only
    before commands listed in PROMPT_ON_COMMANDS.
    This behaviour ensures prompts appear before the correct commands."""
    from spafw37.constants.param import (
        PARAM_PROMPT_TIMING,
        PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS
    )
    
    # Block 5.2.18.1: Clear state
    param._params = {}
    
    # Block 5.2.18.2: Register param with PROMPT_ON_COMMAND
    param.add_param({
        PARAM_NAME: 'password',
        PARAM_PROMPT: 'Password:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['login', 'secure_op'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    # Block 5.2.18.3: Verify skipped at start
    param_def = param._params['password']
    assert param._should_prompt_param(param_def, None, check_value=False) is False
    
    # Block 5.2.18.4: Verify prompts for matching commands
    assert param._should_prompt_param(param_def, 'login', check_value=False) is True
    assert param._should_prompt_param(param_def, 'secure_op', check_value=False) is True
    
    # Block 5.2.18.5: Verify skipped for other commands
    assert param._should_prompt_param(param_def, 'other_cmd', check_value=False) is False
```

[↑ Back to top](#table-of-contents)

---

## Step 5.3: Implement Prompt Execution with Retry Logic

**File:** `src/spafw37/param.py`

Implement prompt execution with validation retry logic. This step creates four helper functions with clear single responsibilities: retry decision logic, error display, error stop handling, and the main prompt orchestration. The architecture eliminates deep nesting by extracting each concern into its own testable function. Validation happens via `set_param_value()` which naturally integrates with existing framework validation.

**Architecture:**
- `_should_continue_after_prompt_error()`: Pure retry decision logic (no side effects)
- `_display_prompt_validation_error()`: User error feedback (logging + output)
- `_handle_prompt_error_stop()`: Required vs optional param handling
- `_execute_prompt()`: Main orchestration (max 2 nesting levels)

**Algorithm for `_execute_prompt()`:**

1. Get retry limit from `PARAM_PROMPT_RETRIES` (param-level) or `_max_prompt_retries` (global default)
2. Initialize retry counter to 0
3. Start infinite loop (break via return/raise):
   a. Call handler to get user input
   b. Call `set_param_value()` to validate and set (may raise ValueError/TypeError)
   c. If successful: return (value already set)
   d. If EOFError or KeyboardInterrupt: propagate immediately
   e. If validation error:
      - Call `_should_continue_after_prompt_error()` to check if should retry
      - If should not continue: call `_handle_prompt_error_stop()` then return
      - If should continue: call `_display_prompt_validation_error()` and loop

**Implementation order:**

1. Add module-level `_max_prompt_retries` variable and `set_max_prompt_retries()` API
2. Create `_should_continue_after_prompt_error()` pure logic function
3. Create `_display_prompt_validation_error()` display function
4. Create `_handle_prompt_error_stop()` error stop function
5. Create `_execute_prompt()` orchestration function
6. Add tests for each function

**Module-level imports for tests/test_param_prompts.py (Step 5.3):**

```python
# Module-level imports for Step 5.3 tests in tests/test_param_prompts.py
import pytest
from spafw37 import param, logging
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_ALLOWED_VALUES,
    PARAM_PROMPT_RETRIES,
    PARAM_REQUIRED,
    PARAM_SENSITIVE,
    PARAM_TYPE,
    PARAM_TYPE_TEXT
)
```

**Code 5.3.1: Module-level retry and output configuration**

```python
# Block 5.3.1: Add to src/spafw37/param.py after _prompted_params
_max_prompt_retries = 3
_output_handler = None
```

**Code 5.3.2: Public API to set output handler**

```python
# Block 5.3.2: Add to src/spafw37/param.py after module-level variables
def set_output_handler(handler):
    """Set output handler for user-facing error messages during prompts.
    
    This allows param module to display error messages without depending on core.
    If not set, defaults to print().
    
    Args:
        handler: Callable that takes a message string and displays it to user.
                 Typically set to core.output by the framework during initialization.
    """
    global _output_handler
    _output_handler = handler
```

**Test 5.3.3: Set output handler**

```gherkin
Scenario: set_output_handler() configures user message display
  Given custom output handler function
  When set_output_handler(custom_handler) is called
  Then _output_handler is custom_handler
  
  # Tests: Output handler configuration
  # Validates: Framework can inject output mechanism
```

```python
# Test 5.3.3: Add to tests/test_param_prompts.py
def test_set_output_handler():
    """Test that set_output_handler() configures output handler."""
    def custom_handler(message):
        pass
    
    param.set_output_handler(custom_handler)
    assert param._output_handler == custom_handler
```

**Code 5.3.4: Public API to set global max retries**

```python
# Block 5.3.4: Add to src/spafw37/param.py after set_output_handler()
def set_max_prompt_retries(count):
    """Set global maximum retry count for validation failures.
    
    This configures the default retry behaviour for all params. Individual params
    can override this using PARAM_PROMPT_RETRIES property.
    
    Args:
        count: Maximum retries. -1 for infinite, 0 for no retries, N for N retries.
    """
    global _max_prompt_retries
    _max_prompt_retries = count
```

**Test 5.3.5: Set global max retries**

```gherkin
Scenario: set_max_prompt_retries() updates global retry limit
  Given _max_prompt_retries initially 3
  When set_max_prompt_retries(5) is called
  Then _max_prompt_retries is 5
  
  # Tests: Global retry configuration
  # Validates: Applications can configure default retry behaviour
```

```python
# Test 5.3.5: Add to tests/test_param_prompts.py
def test_set_max_prompt_retries():
    """Test that set_max_prompt_retries() updates global retry limit."""
    param.set_max_prompt_retries(5)
    assert param._max_prompt_retries == 5
    param.set_max_prompt_retries(3)
```

**Code 5.3.6: Sensitive-aware logging helper**

```python
# Block 5.3.6: Add to src/spafw37/param.py after set_max_prompt_retries()
# Note: Requires module-level import: from spafw37 import logging
def log_param(level, message, param_def):
    """Log message with PARAM_SENSITIVE awareness.
    
    For sensitive params, redacts detailed error information to prevent
    credential leakage in logs.
    
    Args:
        level: Log level (logging.ERROR, logging.INFO, etc.)
        message: Full message to log (may contain sensitive data)
        param_def: Parameter definition dict (checked for PARAM_SENSITIVE)
    """
    param_name = param_def.get(PARAM_NAME, 'unknown')
    is_sensitive = param_def.get(PARAM_SENSITIVE, False)
    
    if is_sensitive:
        sanitized_message = f"Invalid value for sensitive param '{param_name}'"
    else:
        sanitized_message = message
    
    logging.log(_level=level, _message=sanitized_message)
```

**Test 5.3.7: Log param sanitizes sensitive param errors**

```gherkin
Scenario: log_param() redacts error details for sensitive params
  Given param_def with PARAM_SENSITIVE=True and PARAM_NAME='api_key'
  And message = "Invalid value for 'api_key': secret123 is not valid"
  When log_param(logging.ERROR, message, param_def) is called
  Then logging.log() called with ERROR level and sanitized message
  And original error details not logged
  
  # Tests: Sensitive data redaction in logs
  # Validates: Credentials not leaked to log files
```

```python
# Test 5.3.7: Add to tests/test_param_prompts.py
def test_log_param_sanitizes_sensitive(mocker):
    """Test log_param() redacts error details for sensitive params."""
    mock_log = mocker.patch('spafw37.logging.log')
    
    param_def = {
        param.PARAM_NAME: 'api_key',
        param.PARAM_SENSITIVE: True
    }
    message = "Invalid value for 'api_key': secret123 is not valid"
    
    param.log_param(logging.ERROR, message, param_def)
    
    mock_log.assert_called_once_with(
        _level=logging.ERROR,
        _message="Invalid value for sensitive param 'api_key'"
    )
```

**Test 5.3.8: Log param logs full message for non-sensitive params**

```gherkin
Scenario: log_param() logs full message for non-sensitive params
  Given param_def with PARAM_SENSITIVE=False and PARAM_NAME='count'
  And message = "Invalid value for 'count': 'abc' is not a number"
  When log_param(logging.ERROR, message, param_def) is called
  Then logging.log() called with ERROR level and full message
  And error details preserved
  
  # Tests: Normal logging for non-sensitive params
  # Validates: Useful error details available in logs
```

```python
# Test 5.3.8: Add to tests/test_param_prompts.py
def test_log_param_preserves_nonsensitive(mocker):
    """Test log_param() preserves full message for non-sensitive params."""
    mock_log = mocker.patch('spafw37.logging.log')
    
    param_def = {
        param.PARAM_NAME: 'count',
        param.PARAM_SENSITIVE: False
    }
    message = "Invalid value for 'count': 'abc' is not a number"
    
    param.log_param(logging.ERROR, message, param_def)
    
    mock_log.assert_called_once_with(
        _level=logging.ERROR,
        _message=message
    )
```

**Code 5.3.9: Generic sensitive-aware exception raising**

```python
# Block 5.3.9: Add to src/spafw37/param.py after log_param()
def raise_param_error(error, param_def):
    """Raise exception with PARAM_SENSITIVE awareness.
    
    For sensitive params, raises new exception with sanitized message to prevent
    credential leakage in exception traces, monitoring tools, and error logs.
    For non-sensitive params, raises original error with full details.
    
    Args:
        error: The exception to raise (ValueError, TypeError, etc.)
        param_def: Parameter definition dict (checked for PARAM_SENSITIVE)
        
    Raises:
        Exception of same type as error parameter
    """
    is_sensitive = param_def.get(PARAM_SENSITIVE, False)
    if is_sensitive:
        param_name = param_def.get(PARAM_NAME, 'unknown')
        sanitized_error = type(error)(
            f"Invalid value for sensitive param '{param_name}'"
        )
        raise sanitized_error
    else:
        raise error
```

**Test 5.3.9: Raise param error sanitizes for sensitive params**

```gherkin
Scenario: raise_param_error() creates sanitized exception for sensitive param
  Given param_def with PARAM_SENSITIVE=True and PARAM_NAME='password'
  And error = ValueError("'secret123' is too short")
  When raise_param_error(error, param_def) is called
  Then raises ValueError with message "Invalid value for sensitive param 'password'"
  And 'secret123' not in error message
  
  # Tests: Exception sanitization for sensitive params
  # Validates: Credentials not leaked via exception traces
```

```python
# Test 5.3.9: Add to tests/test_param_prompts.py
def test_raise_param_error_sanitizes_sensitive():
    """Test raise_param_error() sanitizes exception for sensitive params."""
    param_def = {
        PARAM_NAME: 'password',
        PARAM_SENSITIVE: True
    }
    error = ValueError("'secret123' is too short")
    
    with pytest.raises(ValueError) as exc_info:
        param.raise_param_error(error, param_def)
    
    error_message = str(exc_info.value)
    assert "sensitive param 'password'" in error_message
    assert "secret123" not in error_message
```

**Test 5.3.10: Raise param error preserves original for non-sensitive**

```gherkin
Scenario: raise_param_error() raises original error for non-sensitive param
  Given param_def with PARAM_SENSITIVE=False
  And error = ValueError("'abc' is not a number")
  When raise_param_error(error, param_def) is called
  Then raises original ValueError
  And full error message preserved
  
  # Tests: Normal exception handling for non-sensitive params
  # Validates: Detailed errors available for debugging
```

```python
# Test 5.3.10: Add to tests/test_param_prompts.py
def test_raise_param_error_preserves_nonsensitive():
    """Test raise_param_error() raises original error for non-sensitive params."""
    param_def = {
        param.PARAM_NAME: 'count',
        param.PARAM_SENSITIVE: False
    }
    error = ValueError("'abc' is not a number")
    
    with pytest.raises(ValueError) as exc_info:
        param.raise_param_error(error, param_def)
    
    assert str(exc_info.value) == "'abc' is not a number"
```

**Test 5.3.11: Raise param error preserves exception type**

```gherkin
Scenario: raise_param_error() preserves exception type
  Given sensitive param_def
  And error = TypeError("expected str, got int")
  When raise_param_error(error, param_def) is called
  Then raises TypeError (not ValueError)
  And message is sanitized
  
  # Tests: Exception type preservation
  # Validates: Callers can catch specific exception types
```

```python
# Test 5.3.11: Add to tests/test_param_prompts.py
def test_raise_param_error_preserves_type():
    """Test raise_param_error() preserves exception type."""
    param_def = {
        param.PARAM_NAME: 'api_key',
        param.PARAM_SENSITIVE: True
    }
    error = TypeError("expected str, got int")
    
    with pytest.raises(TypeError) as exc_info:
        param.raise_param_error(error, param_def)
    
    error_message = str(exc_info.value)
    assert "sensitive param 'api_key'" in error_message
    assert "int" not in error_message
```

**Code 5.3.12: Pure retry decision logic**

```python
# Block 5.3.12: Add to src/spafw37/param.py after raise_param_error()
def _should_continue_after_prompt_error(max_retries, retry_count):
    """Determine if prompt should continue after validation error.
    
    Pure logic function with no side effects. Returns decision based solely on
    retry configuration and current count.
    
    Args:
        max_retries: Maximum retry count (-1 infinite, 0 none, N finite)
        retry_count: Current retry attempt count
        
    Returns:
        Tuple of (should_continue: bool, updated_retry_count: int)
    """
    if max_retries == -1:
        return (True, retry_count)
    if max_retries == 0:
        return (False, retry_count)
    
    retry_count += 1
    should_continue = retry_count < max_retries
    return (should_continue, retry_count)
```

**Test 5.3.13: Retry decision with infinite retries**

```gherkin
Scenario: Infinite retries always continues
  Given max_retries = -1
  When _should_continue_after_prompt_error(-1, 100) is called
  Then returns (True, 100)
  
  # Tests: Infinite retry mode
  # Validates: Count not incremented, always continues
```

```python
# Test 5.3.13: Add to tests/test_param_prompts.py
def test_retry_decision_infinite():
    """Test _should_continue_after_prompt_error() with infinite retries."""
    should_continue, count = param._should_continue_after_prompt_error(-1, 100)
    assert should_continue is True
    assert count == 100
```

**Test 5.3.14: Retry decision with zero retries**

```gherkin
Scenario: Zero retries stops immediately
  Given max_retries = 0
  When _should_continue_after_prompt_error(0, 0) is called
  Then returns (False, 0)
  
  # Tests: No retry mode
  # Validates: First error stops immediately
```

```python
# Test 5.3.14: Add to tests/test_param_prompts.py
def test_retry_decision_zero():
    """Test _should_continue_after_prompt_error() with zero retries."""
    should_continue, count = param._should_continue_after_prompt_error(0, 0)
    assert should_continue is False
    assert count == 0
```

**Test 5.3.15: Retry decision with finite retries continues**

```gherkin
Scenario: Finite retries continues when under limit
  Given max_retries = 3
  And retry_count = 0
  When _should_continue_after_prompt_error(3, 0) called
  Then returns (True, 1)
  
  # Tests: Finite retry counting - continues
  # Validates: Increments count, continues when under limit
```

```python
# Test 5.3.15: Add to tests/test_param_prompts.py
def test_retry_decision_finite_continues():
    """Test _should_continue_after_prompt_error() continues when under limit."""
    should_continue, count = param._should_continue_after_prompt_error(3, 0)
    assert should_continue is True
    assert count == 1
```

**Test 5.3.16: Retry decision with finite retries stops**

```gherkin
Scenario: Finite retries stops when at limit
  Given max_retries = 3
  And retry_count = 2
  When _should_continue_after_prompt_error(3, 2) called
  Then returns (False, 3)
  
  # Tests: Finite retry counting - stops
  # Validates: Increments count, stops at limit
```

```python
# Test 5.3.16: Add to tests/test_param_prompts.py
def test_retry_decision_finite_stops():
    """Test _should_continue_after_prompt_error() stops when at limit."""
    should_continue, count = param._should_continue_after_prompt_error(3, 2)
    assert should_continue is False
    assert count == 3
```

**Code 5.3.17: Display validation error to user**

```python
# Block 5.3.17: Add to src/spafw37/param.py after _should_continue_after_prompt_error()
def _display_prompt_validation_error(param_def, error):
    """Display validation error to user during prompt.
    
    Uses both logging (for audit trail) and injected output handler (for user feedback).
    Redacts sensitive param details from logs via log_param helper.
    If no output handler configured, defaults to print().
    
    Args:
        param_def: Parameter definition dict (checked for PARAM_SENSITIVE)
        error: The validation error exception
    """
    param_name = param_def.get(PARAM_NAME, 'unknown')
    log_message = f"Invalid value for '{param_name}': {error}"
    log_param(logging.ERROR, log_message, param_def)
    
    message = f"Invalid value: {error}. Please try again."
    if _output_handler is not None:
        _output_handler(message)
    else:
        print(message)
```

**Test 5.3.18: Display error uses log_param and output handler**

```gherkin
Scenario: Display function logs and outputs error via handler
  Given param_def with PARAM_NAME='test_param' and PARAM_SENSITIVE=False
  And error = ValueError("must be positive")
  And output handler configured
  When _display_prompt_validation_error(param_def, error) is called
  Then log_param called with error message and param_def
  And output handler called with "Invalid value: must be positive. Please try again."
  
  # Tests: Error display channels
  # Validates: Both logging and injected output used
```

```python
# Test 5.3.18: Add to tests/test_param_prompts.py
def test_display_validation_error_with_handler(mocker):
    """Test _display_prompt_validation_error() uses log_param and output handler."""
    mock_log_param = mocker.patch('spafw37.param.log_param')
    mock_output = mocker.Mock()
    param._output_handler = mock_output
    
    param_def = {
        param.PARAM_NAME: 'test_param',
        param.PARAM_SENSITIVE: False
    }
    error = ValueError("must be positive")
    param._display_prompt_validation_error(param_def, error)
    
    mock_log_param.assert_called_once()
    assert 'test_param' in str(mock_log_param.call_args)
    assert 'must be positive' in str(mock_log_param.call_args)
    
    mock_output.assert_called_once()
    assert 'must be positive' in str(mock_output.call_args)
```

**Test 5.3.19: Display error defaults to print without handler**

```gherkin
Scenario: Display function falls back to print() without handler
  Given no output handler configured
  And param_def with PARAM_NAME='test_param'
  And error = ValueError("invalid")
  When _display_prompt_validation_error(param_def, error) is called
  Then print() called with error message
  And log_param still called
  
  # Tests: Default output fallback
  # Validates: Works without core dependency
```

```python
# Test 5.3.19: Add to tests/test_param_prompts.py
def test_display_validation_error_defaults_to_print(mocker):
    """Test _display_prompt_validation_error() defaults to print() without handler."""
    mock_log_param = mocker.patch('spafw37.param.log_param')
    mock_print = mocker.patch('builtins.print')
    param._output_handler = None
    
    param_def = {
        param.PARAM_NAME: 'test_param',
        param.PARAM_SENSITIVE: False
    }
    error = ValueError("invalid")
    param._display_prompt_validation_error(param_def, error)
    
    mock_log_param.assert_called_once()
    mock_print.assert_called_once()
    assert 'invalid' in str(mock_print.call_args)
```

**Code 5.3.20: Handle max retries exceeded**

```python
# Block 5.3.20: Add to src/spafw37/param.py after _display_prompt_validation_error()
def _handle_prompt_error_stop(param_def, validation_error):
    """Handle stopping prompt execution due to max retries exceeded.
    
    For required params: uses raise_param_error() for sensitive-aware exception raising.
    For optional params: returns silently (param remains unset).
    
    Args:
        param_def: Parameter definition dictionary
        validation_error: The validation exception to potentially raise
        
    Raises:
        ValueError or TypeError: If param is required (sanitized for sensitive params)
    """
    is_required = param_def.get(PARAM_REQUIRED, False)
    if is_required:
        raise_param_error(validation_error, param_def)
```

**Test 5.3.21: Stop handler raises for required non-sensitive param**

```gherkin
Scenario: Stop handler raises original error for required non-sensitive param
  Given required non-sensitive param definition
  And validation_error = ValueError("'abc' is not a number")
  When _handle_prompt_error_stop(param_def, validation_error) is called
  Then raises ValueError with original message
  
  # Tests: Required param error propagation
  # Validates: Detailed errors for non-sensitive params
```

```python
# Test 5.3.21: Add to tests/test_param_prompts.py
def test_handle_stop_required_nonsensitive_raises():
    """Test _handle_prompt_error_stop() raises original error for non-sensitive params."""
    param_def = {
        PARAM_NAME: 'count',
        PARAM_REQUIRED: True,
        PARAM_SENSITIVE: False
    }
    error = ValueError("'abc' is not a number")
    
    with pytest.raises(ValueError) as exc_info:
        param._handle_prompt_error_stop(param_def, error)
    assert "'abc' is not a number" in str(exc_info.value)
```

**Test 5.3.22: Stop handler sanitizes error for required sensitive param**

```gherkin
Scenario: Stop handler sanitizes error message for required sensitive param
  Given required sensitive param definition
  And validation_error = ValueError("'secret123' is not valid")
  When _handle_prompt_error_stop(param_def, validation_error) is called
  Then raises ValueError with sanitized message
  And 'secret123' not in error message
  And error message is "Invalid value for sensitive param 'api_key'"
  
  # Tests: Sensitive param error sanitization
  # Validates: Credentials not leaked via exceptions
```

```python
# Test 5.3.22: Add to tests/test_param_prompts.py
def test_handle_stop_required_sensitive_sanitizes():
    """Test _handle_prompt_error_stop() sanitizes error for sensitive params."""
    param_def = {
        PARAM_NAME: 'api_key',
        PARAM_REQUIRED: True,
        PARAM_SENSITIVE: True
    }
    error = ValueError("'secret123' is not valid")
    
    with pytest.raises(ValueError) as exc_info:
        param._handle_prompt_error_stop(param_def, error)
    
    error_message = str(exc_info.value)
    assert "sensitive param 'api_key'" in error_message
    assert "secret123" not in error_message
```

**Test 5.3.23: Stop handler returns silently for optional param**

```gherkin
Scenario: Stop handler returns for optional param
  Given optional param definition
  And validation_error = ValueError("invalid")
  When _handle_prompt_error_stop(param_def, validation_error) is called
  Then returns None without raising
  
  # Tests: Optional param graceful failure
  # Validates: Optional params can remain unset
```

```python
# Test 5.3.23: Add to tests/test_param_prompts.py
def test_handle_stop_optional_returns():
    """Test _handle_prompt_error_stop() returns silently for optional params."""
    param_def = {PARAM_NAME: 'optional_param'}
    error = ValueError("invalid")
    
    result = param._handle_prompt_error_stop(param_def, error)
    assert result is None
```

**Code 5.3.24: Prompt execution orchestration**

```python
# Block 5.3.24: Add to src/spafw37/param.py after _handle_prompt_error_stop()
def _execute_prompt(param_def, handler):
    """Execute prompt with validation retry loop.
    
    Calls handler to get user input, validates via set_param_value(), and retries
    on validation failure based on configured max retries (param-level or global).
    
    Retry behaviour:
    - -1: Infinite retries (always display error and retry)
    - 0: No retries (first validation error propagates immediately)
    - N: Retry up to N times
    
    Precedence: PARAM_PROMPT_RETRIES → _max_prompt_retries (global default)
    
    Args:
        param_def: Parameter definition dictionary
        handler: Callable that prompts user and returns input string
        
    Raises:
        EOFError: If stdin closed (non-interactive environment)
        KeyboardInterrupt: If user presses Ctrl+C
        ValueError: If required param and max retries exceeded
    """
    param_name = param_def.get(PARAM_NAME)
    max_retries = param_def.get(PARAM_PROMPT_RETRIES, _max_prompt_retries)
    retry_count = 0
    
    while True:
        try:
            user_value = handler(param_def)
            set_param_value(param_name, user_value)
            return
            
        except (EOFError, KeyboardInterrupt):
            raise
            
        except (ValueError, TypeError) as validation_error:
            should_continue, retry_count = _should_continue_after_prompt_error(
                max_retries, retry_count
            )
            if should_continue:
                _display_prompt_validation_error(param_def, validation_error)
                continue
            _handle_prompt_error_stop(param_def, validation_error)
            return
```

**Test 5.3.25: Successful prompt sets value**

```gherkin
Scenario: Successful prompt sets param value
  Given param 'test_param' registered
  And handler returns 'valid_value'
  When _execute_prompt(param_def, handler) is called
  Then set_param_value('test_param', 'valid_value') called
  And function returns without error
  And param value is 'valid_value'
  
  # Tests: Happy path prompt execution
  # Validates: Valid input sets param value
```

```python
# Test 5.3.25: Add to tests/test_param_prompts.py
def test_execute_prompt_success():
    """Test _execute_prompt() sets value on successful prompt."""
    param._params = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    
    def mock_handler(param_def):
        return 'valid_value'
    
    param_def = param._params['test_param']
    param._execute_prompt(param_def, mock_handler)
    
    assert param.get_param_value('test_param') == 'valid_value'
```

**Test 5.3.26: Validation retry with finite retries**

```gherkin
Scenario: Validation failure retries then succeeds
  Given param with PARAM_ALLOWED_VALUES = ['valid', 'other']
  And handler returns 'invalid' then 'valid'
  And max retries = 3 (default)
  When _execute_prompt(param_def, handler) is called
  Then first attempt: 'invalid' rejected, error displayed
  And second attempt: 'valid' accepted
  And param value set to 'valid'
  
  # Tests: Retry mechanism
  # Validates: Users can correct mistakes
```

```python
# Test 5.3.26: Add to tests/test_param_prompts.py
def test_execute_prompt_retry_succeeds():
    """Test _execute_prompt() retries after validation failure."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'test_param',
        PARAM_ALLOWED_VALUES: ['valid', 'other'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    call_count = 0
    def mock_handler(param_def):
        nonlocal call_count
        call_count += 1
        return 'invalid' if call_count == 1 else 'valid'
    
    param_def = param._params['test_param']
    param._execute_prompt(param_def, mock_handler)
    
    assert call_count == 2
    assert param.get_param_value('test_param') == 'valid'
```

**Test 5.3.27: Max retries exceeded for required param**

```gherkin
Scenario: Max retries exceeded for required param raises error
  Given required param
  And handler always returns invalid value
  And PARAM_PROMPT_RETRIES = 2
  When _execute_prompt(param_def, handler) is called
  Then attempts 1 and 2 fail with error displayed
  And attempt 3 exceeds max
  And ValueError raised
  
  # Tests: Required param max retries
  # Validates: Required params must have valid value
```

```python
# Test 5.3.27: Add to tests/test_param_prompts.py
def test_execute_prompt_max_retries_required():
    """Test _execute_prompt() raises ValueError for required param after max retries."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'required_param',
        PARAM_REQUIRED: True,
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 2
    })
    
    def mock_handler(param_def):
        return 'always_invalid'
    
    param_def = param._params['required_param']
    with pytest.raises(ValueError):
        param._execute_prompt(param_def, mock_handler)
```

```python
# Test 5.3.28: Add to tests/test_param_prompts.py
def test_execute_prompt_max_retries_required_sanitizes():
    """Test _execute_prompt() sanitizes error for required sensitive param after max retries."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'api_key',
        PARAM_REQUIRED: True,
        PARAM_SENSITIVE: True,
        PARAM_ALLOWED_VALUES: ['valid_key'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 1
    })
    
    def mock_handler(param_def):
        return 'secret123'  # Always invalid
    
    param_def = param._params['api_key']
    with pytest.raises(ValueError) as exc_info:
        param._execute_prompt(param_def, mock_handler)
    
    error_message = str(exc_info.value)
    assert "sensitive param 'api_key'" in error_message
    assert "secret123" not in error_message
```

**Test 5.3.29: Max retries exceeded for optional param**

```gherkin
Scenario: Max retries exceeded for optional param returns silently
  Given optional param
  And handler always returns invalid value
  And PARAM_PROMPT_RETRIES = 2
  When _execute_prompt(param_def, handler) is called
  Then attempts 1 and 2 fail with error displayed
  And attempt 3 exceeds max
  And function returns without raising
  And param remains unset
  
  # Tests: Optional param max retries
  # Validates: Optional params can remain unset
```

```python
# Test 5.3.29: Add to tests/test_param_prompts.py
def test_execute_prompt_max_retries_optional():
    """Test _execute_prompt() returns silently for optional param after max retries."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'optional_param',
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 2
    })
    
    def mock_handler(param_def):
        return 'always_invalid'
    
    param_def = param._params['optional_param']
    param._execute_prompt(param_def, mock_handler)
    
    assert param.get_param_value('optional_param') is None
```

**Test 5.3.30: Max retries respects param-level override**

```gherkin
Scenario: PARAM_PROMPT_RETRIES overrides global max retries
  Given global _max_prompt_retries = 3
  And param with PARAM_PROMPT_RETRIES = 1
  And handler always returns invalid value
  When _execute_prompt(param_def, handler) is called
  Then only 2 attempts made (initial + 1 retry)
  And not 4 attempts (initial + 3 retries from global)
  
  # Tests: Param-level retry configuration precedence
  # Validates: Per-param override works
```

```python
# Test 5.3.30: Add to tests/test_param_prompts.py
def test_execute_prompt_param_level_retries(mocker):
    """Test _execute_prompt() respects PARAM_PROMPT_RETRIES over global."""
    param._max_prompt_retries = 3
    param._params = {}
    param.add_param({
        PARAM_NAME: 'test_param',
        PARAM_REQUIRED: True,
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 1  # Override global
    })
    
    call_count = 0
    def mock_handler(param_def):
        nonlocal call_count
        call_count += 1
        return 'invalid'
    
    param_def = param._params['test_param']
    with pytest.raises(ValueError):
        param._execute_prompt(param_def, mock_handler)
    
    assert call_count == 2  # Initial + 1 retry, not initial + 3
```

**Test 5.3.31: EOFError propagates immediately**

```gherkin
Scenario: EOFError from handler propagates without retry
  Given handler raises EOFError
  When _execute_prompt(param_def, handler) is called
  Then EOFError propagates immediately
  And no retry attempted
  
  # Tests: Non-interactive environment
  # Validates: stdin closure detected
```

```python
# Test 5.3.31: Add to tests/test_param_prompts.py
def test_execute_prompt_eoferror():
    """Test _execute_prompt() propagates EOFError immediately."""
    def mock_handler(param_def):
        raise EOFError("stdin closed")
    
    param_def = {PARAM_NAME: 'test_param'}
    with pytest.raises(EOFError):
        param._execute_prompt(param_def, mock_handler)
```

**Test 5.3.32: KeyboardInterrupt propagates immediately**

```gherkin
Scenario: KeyboardInterrupt from handler propagates without retry
  Given handler raises KeyboardInterrupt
  When _execute_prompt(param_def, handler) is called
  Then KeyboardInterrupt propagates immediately
  And no retry attempted
  
  # Tests: User abort (Ctrl+C)
  # Validates: Immediate cancellation
```

```python
# Test 5.3.32: Add to tests/test_param_prompts.py
def test_execute_prompt_keyboard_interrupt():
    """Test _execute_prompt() propagates KeyboardInterrupt immediately."""
    def mock_handler(param_def):
        raise KeyboardInterrupt()
    
    param_def = {PARAM_NAME: 'test_param'}
    with pytest.raises(KeyboardInterrupt):
        param._execute_prompt(param_def, mock_handler)
```

**Code 5.3.33: Migrate _set_param_default() to use log_param**

```python
# Block 5.3.33: Update existing function in src/spafw37/param.py
# Change line ~1097 from:
#   logging.log_trace(_message=f"Setting default for param '{param_name}' = {default_value}")
# To:
    log_param(logging.TRACE, f"Setting default for param '{param_name}' = {default_value}", _param)
```

**Module-level imports for tests/test_param.py (Step 5.3.33-35):**

```python
# Module-level imports for Step 5.3.33-35 tests in tests/test_param.py
import pytest
from spafw37 import param, logging
from spafw37.constants.param import PARAM_NAME, PARAM_SENSITIVE, PARAM_TYPE, PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER
```

**Test 5.3.33: Default setting sanitizes sensitive param values**

```gherkin
Scenario: _set_param_default() uses log_param for sensitive params
  Given sensitive param with default value
  When _set_param_default() sets default
  Then logging.log() called with TRACE level and sanitized message
  And default value not logged
  
  # Tests: Default value sanitization in trace logs
  # Validates: Default credentials not leaked during initialization
```

```python
# Test 5.3.33: Add to tests/test_param.py
def test_set_param_default_sanitizes_sensitive(mocker):
    """Test _set_param_default() sanitizes sensitive param defaults."""
    mock_log = mocker.patch('spafw37.logging.log')
    param._params = {}
    
    param_def = {
        PARAM_NAME: 'api_key',
        PARAM_SENSITIVE: True,
        PARAM_DEFAULT: 'default_secret_key',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    
    param._set_param_default(param_def)
    
    # Verify log_param was called (which calls logging.log)
    mock_log.assert_called()
    call_args = mock_log.call_args
    assert call_args[1]['_level'] == logging.TRACE
    logged_message = call_args[1]['_message']
    assert "sensitive param 'api_key'" in logged_message
    assert "default_secret_key" not in logged_message
```

**Code 5.3.34: Migrate set_param() to use log_param**

```python
# Block 5.3.34: Update existing function in src/spafw37/param.py
# Change line ~1774 from:
#   logging.log_debug(_message="Set param '{}' = {}".format(param_name_for_log, value))
# To:
    log_param(logging.DEBUG, f"Set param '{param_name_for_log}' = {value}", param_definition)
```

**Test 5.3.34: Parameter setting sanitizes sensitive param values**

```gherkin
Scenario: set_param() uses log_param for sensitive params
  Given sensitive param registered
  When set_param() sets value
  Then logging.log() called with DEBUG level and sanitized message
  And actual value not logged
  
  # Tests: CRITICAL - All param updates sanitized
  # Validates: Runtime credentials not leaked to debug logs
```

```python
# Test 5.3.34: Add to tests/test_param.py
def test_set_param_sanitizes_sensitive(mocker):
    """Test set_param() sanitizes sensitive param values in logs."""
    mock_log = mocker.patch('spafw37.logging.log')
    param._params = {}
    
    param.add_param({
        PARAM_NAME: 'password',
        PARAM_SENSITIVE: True,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    param.set_param(param_name='password', value='user_secret_password')
    
    # Verify log_param was called (which calls logging.log)
    mock_log.assert_called()
    call_args = mock_log.call_args
    assert call_args[1]['_level'] == logging.DEBUG
    logged_message = call_args[1]['_message']
    assert "sensitive param 'password'" in logged_message
    assert "user_secret_password" not in logged_message
```

**Test 5.3.35: Non-sensitive params still log full details**

```gherkin
Scenario: set_param() logs full details for non-sensitive params
  Given non-sensitive param registered
  When set_param() sets value
  Then logging.log() called with full value in message
  And debugging information preserved
  
  # Tests: Normal debug logging unchanged
  # Validates: Non-sensitive params still provide debugging info
```

```python
# Test 5.3.35: Add to tests/test_param.py
def test_set_param_preserves_nonsensitive_logging(mocker):
    """Test set_param() logs full details for non-sensitive params."""
    mock_log = mocker.patch('spafw37.logging.log')
    param._params = {}
    
    param.add_param({
        PARAM_NAME: 'count',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    })
    
    param.set_param(param_name='count', value=42)
    
    mock_log.assert_called()
    call_args = mock_log.call_args
    assert call_args[1]['_level'] == logging.DEBUG
    logged_message = call_args[1]['_message']
    assert "count" in logged_message
    assert "42" in logged_message
```

**Test 5.3.21: Param-level retries override global**

```gherkin
Scenario: PARAM_PROMPT_RETRIES overrides global _max_prompt_retries
  Given global _max_prompt_retries = 3
  And param with PARAM_PROMPT_RETRIES = 1
  And handler always returns invalid value
  When _execute_prompt(param_def, handler) is called
  Then only 1 retry attempted (not 3)
  And max retries exceeded after 1 retry
  
  # Tests: Retry precedence
  # Validates: Param-level overrides global
```

```python
# Test 5.3.24: Add to tests/test_param_prompts.py
def test_execute_prompt_param_retries_override():
    """Test PARAM_PROMPT_RETRIES overrides global _max_prompt_retries."""
    param._max_prompt_retries = 3
    param._params = {}
    param.add_param({
        PARAM_NAME: 'override_param',
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 1
    })
    
    call_count = 0
    def mock_handler(param_def):
        nonlocal call_count
        call_count += 1
        return 'invalid'
    
    param_def = param._params['override_param']
    param._execute_prompt(param_def, mock_handler)
    
    assert call_count == 1
```

[↑ Back to top](#table-of-contents)

---

## Step 5.4: Implement Param Identification Functions

**File:** `src/spafw37/param.py`

Implement functions that identify which params need prompting for a given timing context. These functions encapsulate the iteration and filtering logic, returning lists of params ready to prompt with their handlers pre-resolved. This separates the "what to prompt" concern from the "how to prompt" concern.

**Architecture:**
- `_get_params_to_prompt(timing)`: For PROMPT_ON_START timing (iterates all params)
- `_get_params_for_command(command_def)`: For PROMPT_ON_COMMAND timing (uses COMMAND_PROMPT_PARAMS)

Both functions filter params using `_should_prompt_param()` and resolve handlers via `_get_prompt_handler()`, returning a list of (param_name, param_def, handler) tuples.

**Algorithm for `_get_params_to_prompt()`:**

1. Initialize empty results list
2. Iterate all params in `_params` registry
3. For each param:
   - Check if has `PARAM_PROMPT` property (skip if not)
   - Check if timing matches (skip if not)
   - Call `_should_prompt_param(param_def, None)` (skip if False)
   - Resolve handler via `_get_prompt_handler(param_def)`
   - Append (param_name, param_def, handler) to results
4. Return results list

**Algorithm for `_get_params_for_command()`:**

1. Get `COMMAND_PROMPT_PARAMS` list from command definition (return empty if not present)
2. Get command name from command definition
3. Initialize empty results list
4. For each param_name in COMMAND_PROMPT_PARAMS:
   - Look up param_def from `_params` registry
   - Call `_should_prompt_param(param_def, command_name)` (skip if False)
   - Resolve handler via `_get_prompt_handler(param_def)`
   - Append (param_name, param_def, handler) to results
5. Return results list

**Implementation order:**

1. Create `_get_params_to_prompt()` for start timing
2. Create `_get_params_for_command()` for command timing
3. Add tests for both functions

**Code 5.4.1: Get params for start timing**

```python
# Block 5.4.1: Add to src/spafw37/param.py after _execute_prompt()
def _get_params_to_prompt(timing):
    """Identify params that need prompting for given timing.
    
    Iterates all registered params, filters by timing and prompt need,
    resolves handlers.
    
    Args:
        timing: PROMPT_ON_START or PROMPT_ON_COMMAND constant
        
    Returns:
        List of (param_name, param_def, handler) tuples
    """
    results = []
    
    for param_name, param_def in _params.items():
        if PARAM_PROMPT not in param_def:
            continue
        if param_def.get(PARAM_PROMPT_TIMING) != timing:
            continue
        if not _should_prompt_param(param_def, None):
            continue
        
        handler = _get_prompt_handler(param_def)
        results.append((param_name, param_def, handler))
    
    return results
```

**Test 5.4.2: Get params filters by timing**

```gherkin
Scenario: _get_params_to_prompt() filters params by timing
  Given param 'start1' with PROMPT_ON_START
  And param 'start2' with PROMPT_ON_START
  And param 'command1' with PROMPT_ON_COMMAND
  And param 'no_prompt' without PARAM_PROMPT
  When _get_params_to_prompt(PROMPT_ON_START) is called
  Then returns list with 'start1' and 'start2'
  And 'command1' and 'no_prompt' not included
  
  # Tests: Timing-based filtering
  # Validates: Only matching timing params included
```

```python
# Test 5.4.2: Add to tests/test_param_prompts.py
def test_get_params_to_prompt_filters_timing():
    """Test _get_params_to_prompt() filters params by timing."""
    from spafw37.constants.param import PARAM_PROMPT_TIMING, PROMPT_ON_START, PROMPT_ON_COMMAND
    
    param._params = {}
    param.add_param({
        PARAM_NAME: 'start1',
        PARAM_PROMPT: 'Enter start1:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START
    })
    param.add_param({
        PARAM_NAME: 'start2',
        PARAM_PROMPT: 'Enter start2:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START
    })
    param.add_param({
        PARAM_NAME: 'command1',
        PARAM_PROMPT: 'Enter command1:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND
    })
    
    results = param._get_params_to_prompt(PROMPT_ON_START)
    param_names = [name for name, _, _ in results]
    
    assert 'start1' in param_names
    assert 'start2' in param_names
    assert 'command1' not in param_names
    assert len(param_names) == 2
```

**Test 5.4.3: Get params resolves handlers**

```gherkin
Scenario: _get_params_to_prompt() resolves handler for each param
  Given param with PROMPT_ON_START and custom handler
  When _get_params_to_prompt(PROMPT_ON_START) is called
  Then returned tuple includes resolved handler
  And handler is the custom handler (not default)
  
  # Tests: Handler resolution
  # Validates: Handlers pre-resolved in results
```

```python
# Test 5.4.3: Add to tests/test_param_prompts.py
def test_get_params_to_prompt_resolves_handlers():
    """Test _get_params_to_prompt() resolves handlers."""
    from spafw37.constants.param import PARAM_PROMPT_TIMING, PROMPT_ON_START
    
    def custom_handler(param_def):
        return "custom"
    
    param._params = {}
    param.add_param({
        PARAM_NAME: 'test_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_PROMPT_HANDLER: custom_handler
    })
    
    results = param._get_params_to_prompt(PROMPT_ON_START)
    assert len(results) == 1
    
    name, param_def, handler = results[0]
    assert name == 'test_param'
    assert handler == custom_handler
```

**Code 5.4.4: Get params for command timing**

```python
# Block 5.4.4: Add to src/spafw37/param.py after _get_params_to_prompt()
def _get_params_for_command(command_def):
    """Identify params that need prompting for command execution.
    
    Uses COMMAND_PROMPT_PARAMS list for O(1) lookup of which params to check.
    Filters by prompt need and resolves handlers.
    
    Args:
        command_def: Command definition dictionary with COMMAND_PROMPT_PARAMS
        
    Returns:
        List of (param_name, param_def, handler) tuples
    """
    from spafw37.constants.command import COMMAND_PROMPT_PARAMS, COMMAND_NAME
    
    prompt_params = command_def.get(COMMAND_PROMPT_PARAMS, [])
    if not prompt_params:
        return []
    
    command_name = command_def.get(COMMAND_NAME)
    results = []
    
    for param_name in prompt_params:
        param_def = _params.get(param_name)
        if not param_def:
            continue
        if not _should_prompt_param(param_def, command_name):
            continue
        
        handler = _get_prompt_handler(param_def)
        results.append((param_name, param_def, handler))
    
    return results
```

**Test 5.4.5: Get params for command uses COMMAND_PROMPT_PARAMS**

```gherkin
Scenario: _get_params_for_command() uses COMMAND_PROMPT_PARAMS list
  Given command with COMMAND_PROMPT_PARAMS = ['param1', 'param2']
  And params 'param1' and 'param2' registered
  When _get_params_for_command(command_def) is called
  Then returns list with 'param1' and 'param2'
  And both have handlers resolved
  
  # Tests: Command param list usage
  # Validates: O(1) lookup via COMMAND_PROMPT_PARAMS
```

```python
# Test 5.4.5: Add to tests/test_param_prompts.py
def test_get_params_for_command_uses_list():
    """Test _get_params_for_command() uses COMMAND_PROMPT_PARAMS list."""
    from spafw37.constants.command import COMMAND_NAME, COMMAND_PROMPT_PARAMS
    
    param._params = {}
    param.add_param({PARAM_NAME: 'param1', PARAM_PROMPT: 'Enter param1:'})
    param.add_param({PARAM_NAME: 'param2', PARAM_PROMPT: 'Enter param2:'})
    
    command_def = {
        COMMAND_NAME: 'test_command',
        COMMAND_PROMPT_PARAMS: ['param1', 'param2']
    }
    
    results = param._get_params_for_command(command_def)
    param_names = [name for name, _, _ in results]
    
    assert 'param1' in param_names
    assert 'param2' in param_names
    assert len(param_names) == 2
```

**Test 5.4.6: Get params for command filters by should_prompt**

```gherkin
Scenario: _get_params_for_command() filters using _should_prompt_param
  Given command with COMMAND_PROMPT_PARAMS = ['already_set', 'needs_prompt']
  And param 'already_set' has CLI value (should not prompt)
  And param 'needs_prompt' has no value (should prompt)
  When _get_params_for_command(command_def) is called
  Then returns list with only 'needs_prompt'
  And 'already_set' filtered out
  
  # Tests: Filtering by prompt need
  # Validates: CLI overrides respected
```

```python
# Test 5.4.6: Add to tests/test_param_prompts.py
def test_get_params_for_command_filters_by_should_prompt():
    """Test _get_params_for_command() filters using _should_prompt_param()."""
    from spafw37.constants.command import COMMAND_NAME, COMMAND_PROMPT_PARAMS
    
    param._params = {}
    param.add_param({PARAM_NAME: 'already_set', PARAM_PROMPT: 'Enter:'})
    param.add_param({PARAM_NAME: 'needs_prompt', PARAM_PROMPT: 'Enter:'})
    
    param.set_param_value('already_set', 'value')
    
    command_def = {
        COMMAND_NAME: 'test_command',
        COMMAND_PROMPT_PARAMS: ['already_set', 'needs_prompt']
    }
    
    results = param._get_params_for_command(command_def)
    param_names = [name for name, _, _ in results]
    
    assert 'needs_prompt' in param_names
    assert 'already_set' not in param_names
    assert len(param_names) == 1
```

[↑ Back to top](#table-of-contents)

---

## Step 5.5: Implement Prompt Orchestration Function

**File:** `src/spafw37/param.py`

Implement the orchestration function that executes prompts for a list of params. This function iterates the list, calls `_execute_prompt()` for each param (which sets the value), and tracks successful prompts in `_prompted_params`. This is the bridge between identification (Step 5.4) and execution (Step 5.3).

**Algorithm:**

1. For each (param_name, param_def, handler) tuple in params list:
   - Call `_execute_prompt(param_def, handler)` (sets value internally, may raise)
   - If successful (no exception): add param_name to `_prompted_params` set

**Error handling:**
- Errors from `_execute_prompt()` propagate to caller
- For required params: ValueError propagates (caller handles application exit)
- For optional params: function returns normally (value remains unset)

**Implementation order:**

1. Create `_execute_prompts()` orchestration function
2. Add test for successful prompt tracking
3. Add test for error propagation

**Code 5.5.1: Prompt orchestration**

```python
# Block 5.5.1: Add to src/spafw37/param.py after _get_params_for_command()
def _execute_prompts(params_to_prompt):
    """Execute prompts for list of params.
    
    Orchestration function that iterates params, executes prompts, and tracks
    successful prompts. Errors from required params propagate to caller.
    
    Args:
        params_to_prompt: List of (param_name, param_def, handler) tuples
    """
    for param_name, param_def, handler in params_to_prompt:
        _execute_prompt(param_def, handler)
        _prompted_params.add(param_name)
```

**Test 5.5.2: Execute prompts tracks successful prompts**

```gherkin
Scenario: _execute_prompts() tracks each successful prompt
  Given list with three params
  And handlers return valid values
  When _execute_prompts(params_list) is called
  Then all three prompts execute
  And all three param names added to _prompted_params
  
  # Tests: Prompt tracking
  # Validates: Successful prompts tracked for REPEAT_NEVER
```

```python
# Test 5.5.2: Add to tests/test_param_prompts.py
def test_execute_prompts_tracks_success():
    """Test _execute_prompts() tracks successful prompts."""
    param._params = {}
    param._prompted_params = set()
    
    param.add_param({PARAM_NAME: 'param1', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.add_param({PARAM_NAME: 'param2', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.add_param({PARAM_NAME: 'param3', PARAM_TYPE: PARAM_TYPE_TEXT})
    
    def mock_handler(param_def):
        return 'value'
    
    params_list = [
        ('param1', param._params['param1'], mock_handler),
        ('param2', param._params['param2'], mock_handler),
        ('param3', param._params['param3'], mock_handler)
    ]
    
    param._execute_prompts(params_list)
    
    assert 'param1' in param._prompted_params
    assert 'param2' in param._prompted_params
    assert 'param3' in param._prompted_params
```

**Test 5.5.3: Execute prompts propagates required param errors**

```gherkin
Scenario: Error from required param propagates
  Given list with required param that fails validation
  When _execute_prompts(params_list) is called
  Then ValueError propagates from _execute_prompt
  And calling code can handle error appropriately
  
  # Tests: Error propagation
  # Validates: Required param errors bubble up
```

```python
# Test 5.5.3: Add to tests/test_param_prompts.py
def test_execute_prompts_propagates_errors():
    """Test _execute_prompts() propagates errors from required params."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'required_param',
        PARAM_REQUIRED: True,
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 1
    })
    
    def mock_handler(param_def):
        return 'invalid'
    
    params_list = [
        ('required_param', param._params['required_param'], mock_handler)
    ]
    
    with pytest.raises(ValueError):
        param._execute_prompts(params_list)
```

[↑ Back to top](#table-of-contents)

---

## Step 5.6: Implement Public API Functions

**File:** `src/spafw37/param.py`

Implement the public API functions that orchestrate the complete prompt flow. These functions are called by cli.py and command.py, encapsulating all prompting logic within the param module. Each function chains the identification and execution steps, providing a clean interface for integration.

**Architecture:**
- `prompt_params_for_start()`: Handle all PROMPT_ON_START prompts (called by cli.py)
- `prompt_params_for_command(command_def)`: Handle all PROMPT_ON_COMMAND prompts (called by command.py)

Both functions follow the pattern: identify params → execute prompts.

**Algorithm for `prompt_params_for_start()`:**

1. Call `_get_params_to_prompt(PROMPT_ON_START)` to identify params
2. If list empty: return (no prompts needed)
3. Call `_execute_prompts(params_list)` to execute prompts
4. Errors from required params propagate to caller (cli.py handles exit)

**Algorithm for `prompt_params_for_command()`:**

1. Call `_get_params_for_command(command_def)` to identify params
2. If list empty: return (no prompts needed)
3. Call `_execute_prompts(params_list)` to execute prompts
4. Errors from required params propagate to caller (command.py handles exit)

**Implementation order:**

1. Create `prompt_params_for_start()` public API
2. Create `prompt_params_for_command()` public API
3. Add tests for both functions

**Code 5.6.1: Public API for start timing prompts**

```python
# Block 5.6.1: Add to src/spafw37/param.py after _execute_prompts()
def prompt_params_for_start():
    """Prompt all params with PROMPT_ON_START timing.
    
    Public API called by cli.py after command-line parsing. Identifies which
    params need prompting, executes prompts with retry logic, and sets values.
    
    Raises:
        ValueError: If required param fails validation after max retries
    """
    from spafw37.constants.param import PROMPT_ON_START
    
    params_to_prompt = _get_params_to_prompt(PROMPT_ON_START)
    if not params_to_prompt:
        return
    
    _execute_prompts(params_to_prompt)
```

**Test 5.6.2: Start prompts calls identification and execution**

```gherkin
Scenario: prompt_params_for_start() orchestrates complete flow
  Given param with PROMPT_ON_START timing
  When prompt_params_for_start() is called
  Then _get_params_to_prompt(PROMPT_ON_START) called
  And _execute_prompts called with results
  And param value set and tracked
  
  # Tests: Public API orchestration
  # Validates: Complete flow for start timing
```

```python
# Test 5.6.2: Add to tests/test_param_prompts.py
def test_prompt_params_for_start_orchestration():
    """Test prompt_params_for_start() orchestrates identification and execution."""
    from spafw37.constants.param import PARAM_PROMPT_TIMING, PROMPT_ON_START
    
    param._params = {}
    param._prompted_params = set()
    
    param.add_param({
        PARAM_NAME: 'start_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    def mock_handler(param_def):
        return 'value'
    
    param._global_prompt_handler = mock_handler
    
    param.prompt_params_for_start()
    
    assert param.get_param_value('start_param') == 'value'
    assert 'start_param' in param._prompted_params
```

**Test 5.6.3: Start prompts returns early if no params**

```gherkin
Scenario: prompt_params_for_start() returns early if no params to prompt
  Given no params with PROMPT_ON_START timing
  When prompt_params_for_start() is called
  Then returns without executing any prompts
  And no side effects
  
  # Tests: Early return optimization
  # Validates: No work done when not needed
```

```python
# Test 5.6.3: Add to tests/test_param_prompts.py
def test_prompt_params_for_start_no_params():
    """Test prompt_params_for_start() returns early with no params."""
    param._params = {}
    param._prompted_params = set()
    
    param.prompt_params_for_start()
    
    assert len(param._prompted_params) == 0
```

**Code 5.6.4: Public API for command timing prompts**

```python
# Block 5.6.4: Add to src/spafw37/param.py after prompt_params_for_start()
def prompt_params_for_command(command_def):
    """Prompt all params for command execution.
    
    Public API called by command.py before each command executes. Uses
    COMMAND_PROMPT_PARAMS list for efficient lookup, executes prompts with
    retry logic and repeat behaviour control.
    
    Args:
        command_def: Command definition dict with COMMAND_PROMPT_PARAMS
        
    Raises:
        ValueError: If required param fails validation after max retries
    """
    params_to_prompt = _get_params_for_command(command_def)
    if not params_to_prompt:
        return
    
    _execute_prompts(params_to_prompt)
```

**Test 5.6.5: Command prompts calls identification and execution**

```gherkin
Scenario: prompt_params_for_command() orchestrates complete flow
  Given command with COMMAND_PROMPT_PARAMS = ['param1']
  And param 'param1' registered
  When prompt_params_for_command(command_def) is called
  Then _get_params_for_command(command_def) called
  And _execute_prompts called with results
  And param value set and tracked
  
  # Tests: Public API orchestration for commands
  # Validates: Complete flow for command timing
```

```python
# Test 5.6.5: Add to tests/test_param_prompts.py
def test_prompt_params_for_command_orchestration():
    """Test prompt_params_for_command() orchestrates identification and execution."""
    from spafw37.constants.command import COMMAND_NAME, COMMAND_PROMPT_PARAMS
    
    param._params = {}
    param._prompted_params = set()
    
    param.add_param({
        PARAM_NAME: 'command_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    command_def = {
        COMMAND_NAME: 'test_command',
        COMMAND_PROMPT_PARAMS: ['command_param']
    }
    
    def mock_handler(param_def):
        return 'value'
    
    param._global_prompt_handler = mock_handler
    
    param.prompt_params_for_command(command_def)
    
    assert param.get_param_value('command_param') == 'value'
    assert 'command_param' in param._prompted_params
```

**Test 5.6.6: Command prompts returns early if no params**

```gherkin
Scenario: prompt_params_for_command() returns early if no COMMAND_PROMPT_PARAMS
  Given command without COMMAND_PROMPT_PARAMS property
  When prompt_params_for_command(command_def) is called
  Then returns without executing any prompts
  And no side effects
  
  # Tests: Early return optimization
  # Validates: No work done when not needed
```

```python
# Test 5.6.6: Add to tests/test_param_prompts.py
def test_prompt_params_for_command_no_params():
    """Test prompt_params_for_command() returns early with no COMMAND_PROMPT_PARAMS."""
    from spafw37.constants.command import COMMAND_NAME
    
    param._params = {}
    param._prompted_params = set()
    
    command_def = {COMMAND_NAME: 'test_command'}
    
    param.prompt_params_for_command(command_def)
    
    assert len(param._prompted_params) == 0
```

[↑ Back to top](#table-of-contents)

---

## Step 6: CLI Integration

**File:** `src/spafw37/cli.py`

Integrate start-timing prompts into the CLI execution flow by calling the public param API. This adds a single function call between command-line parsing and command execution. All complexity (identification, filtering, retry logic) is handled by param.py.

**Integration point:**
- After `_parse_args()` has completed
- Before command queue processing begins
- Before required param validation occurs

**Algorithm:**

The CLI integration follows this logical flow:

1. Parse command-line arguments to capture user-provided values
2. **Prompt for start-timing params**: Call `param.prompt_params_for_start()`
   - Param module identifies all PROMPT_ON_START params
   - For each param: check if should prompt (not set via CLI)
   - If should prompt: execute prompt with handler and retry logic
   - Set prompted values in param registry
   - Track successfully prompted params
3. Continue with command queue processing
4. If any required param fails: error propagates, CLI exits with error code

**Key behaviours:**
- CLI-provided values (from args) skip prompting
- Required param failures cause immediate exit
- Optional param failures allow execution to continue
- All prompting complexity handled by param module

### Code 6.1: Add prompt_params_for_start() call to CLI

```python
# File: src/spafw37/cli.py
# Location: In the _run_cli() function, after _parse_args() and before command execution

# Module-level imports (add if not present)
from spafw37 import param

# Block 6.1.1: Call param.prompt_params_for_start() after parsing args
def _run_cli(args=None):
    """Execute the CLI with the given arguments."""
    # ... existing code for initialization ...
    
    # Block 6.1.1.1: Parse command-line arguments
    _parse_args(args)
    
    # Block 6.1.1.2: Prompt for parameters marked PROMPT_ON_START
    param.prompt_params_for_start()
    
    # ... existing code for command execution ...
```

### Test 6.1.2: Verify param.prompt_params_for_start() is called

**Gherkin:**
```gherkin
Given the CLI is executed
When _run_cli() runs
Then param.prompt_params_for_start() is called exactly once
And it is called after _parse_args()
```

**Implementation:**
```python
def test_run_cli_calls_prompt_params_for_start():
    """
    Verify that _run_cli() calls param.prompt_params_for_start() after parsing arguments.
    
    Given the CLI is executed
    When _run_cli() runs
    Then param.prompt_params_for_start() is called exactly once
    And it is called after _parse_args()
    """
    from unittest.mock import patch, call
    from spafw37 import cli
    
    with patch.object(cli, '_parse_args') as mock_parse_args:
        with patch('spafw37.param.prompt_params_for_start') as mock_prompt:
            with patch.object(cli, '_execute_command'):
                cli._run_cli(['test_cmd'])
    
    mock_prompt.assert_called_once()
    
    call_order = []
    for call_item in mock_parse_args.mock_calls + mock_prompt.mock_calls:
        call_order.append(call_item)
    
    parse_index = next(
        index for index, c in enumerate(call_order) 
        if 'parse_args' in str(c)
    )
    prompt_index = next(
        index for index, c in enumerate(call_order) 
        if 'prompt_params_for_start' in str(c)
    )
    
    assert parse_index < prompt_index
```

**Notes:**
- The call occurs after `_parse_args()` so CLI-provided values are already set
- The call occurs before command execution so prompted values are available
- Unit test verifies the call is made and sequencing is correct

[↑ Back to top](#table-of-contents)

---

## Step 7: Command Integration

**File:** `src/spafw37/command.py`

Integrate command-timing prompts into the command execution pipeline by calling the public param API. This adds a single function call immediately before each command executes. All complexity (COMMAND_PROMPT_PARAMS lookup, repeat behaviour, retry logic) is handled by param.py.

**Integration point:**
- In command execution loop (where individual commands are executed)
- Immediately before each command's action function is called
- After command dependencies are resolved

**Repeat behaviour:**
- Automatically handled by `_should_prompt_param()` called within param.py
- PROMPT_REPEAT_ALWAYS: Prompts every command execution
- PROMPT_REPEAT_IF_BLANK: Prompts only if value blank
- PROMPT_REPEAT_NEVER: Prompts only if not in `_prompted_params` set

**Algorithm:**

The command integration follows this logical flow for each command execution:

1. Command execution begins after dependencies resolved
2. **Prompt for command-timing params**: Call `param.prompt_params_for_command(command_def)`
   - Param module gets COMMAND_PROMPT_PARAMS list from command definition
   - For each param in list: check if should prompt
     - Apply PARAM_PROMPT_REPEAT logic (ALWAYS/IF_BLANK/NEVER)
     - Check if already in `_prompted_params` set
     - Check if value already set (CLI override or previous prompt)
   - If should prompt: execute prompt with handler and retry logic
   - Set prompted values in param registry
   - Track successfully prompted params
3. Execute command handler with prompted values available
4. If any required param fails: error propagates, command execution stops

**Key behaviours:**
- REPEAT_ALWAYS: Prompts on every command execution (even in cycles)
- REPEAT_IF_BLANK: Prompts only when param has no value
- REPEAT_NEVER: Prompts at most once per session
- CLI-provided values skip prompting (overrides prompt request)
- All repeat logic and state management handled by param module

### Code 7.1: Add prompt_params_for_command() call to command execution

```python
# File: src/spafw37/command.py
# Location: In the _execute_command() function, before the command handler is called

# Module-level imports (add if not present)
from spafw37 import param

# Block 7.1.1: Call param.prompt_params_for_command() before executing handler
def _execute_command(command_def):
    """Execute a command with the given command definition."""
    # ... existing code for pre-execution setup ...
    
    # Block 7.1.1.1: Prompt for parameters marked PROMPT_ON_COMMAND
    param.prompt_params_for_command(command_def)
    
    # Block 7.1.1.2: Execute the command handler
    # ... existing code for handler execution ...
```

### Test 7.1.2: Verify param.prompt_params_for_command() is called

**Gherkin:**
```gherkin
Given a command is being executed
When _execute_command() runs
Then param.prompt_params_for_command() is called with the command definition
And it is called before the command handler executes
```

**Implementation:**
```python
def test_execute_command_calls_prompt_params_for_command():
    """
    Verify that _execute_command() calls param.prompt_params_for_command()
    before executing the command handler.
    
    Given a command is being executed
    When _execute_command() runs
    Then param.prompt_params_for_command() is called with the command definition
    And it is called before the command handler executes
    """
    from unittest.mock import patch, MagicMock
    from spafw37 import command
    
    mock_handler = MagicMock()
    command_def = {
        'name': 'test_cmd',
        'handler': mock_handler,
    }
    
    call_sequence = []
    
    def track_prompt_call(cmd_def):
        call_sequence.append('prompt')
    
    def track_handler_call():
        call_sequence.append('handler')
    
    mock_handler.side_effect = track_handler_call
    
    with patch('spafw37.param.prompt_params_for_command', side_effect=track_prompt_call):
        command._execute_command(command_def)
    
    assert call_sequence == ['prompt', 'handler']
```

**Notes:**
- The call occurs before the command handler executes
- The PARAM_PROMPT_REPEAT behaviour is handled inside param module (Step 5.2)
- This integration point applies to all command executions (including cycles)
- Unit test verifies the call is made with correct arguments and sequencing

[↑ Back to top](#table-of-contents)

---

## Step 8: Integration Tests

**File:** `tests/test_integration_prompts.py` (new file)

Create comprehensive integration tests covering complete workflows from CLI invocation through prompt execution to command completion. These tests validate the entire prompt system working together: timing modes, repeat behaviour, CLI overrides, validation retry logic, and custom handlers.

### Module-level imports

```python
# File: tests/test_integration_prompts.py

import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest

from spafw37 import core as spafw37
from spafw37 import param
from spafw37 import command
from spafw37.constants.param import (
    PARAM_PROMPT_ON_START,
    PARAM_PROMPT_ON_COMMAND,
    PARAM_PROMPT_REPEAT_ALWAYS,
    PARAM_PROMPT_REPEAT_IF_BLANK,
    PARAM_PROMPT_REPEAT_NEVER,
)
```

### Test 8.8.1: PROMPT_ON_START prompts before command execution

**Gherkin:**
```gherkin
Given a parameter marked PROMPT_ON_START
And a command that uses the parameter
When the CLI runs
Then the parameter is prompted for before the command executes
And the command receives the prompted value
```

**Implementation:**
```python
def test_prompt_on_start_executes_before_commands():
    """
    Verify that parameters marked PROMPT_ON_START are prompted for
    before any command executes.
    
    Given a parameter marked PROMPT_ON_START
    And a command that uses the parameter
    When the CLI runs
    Then the parameter is prompted for before the command executes
    And the command receives the prompted value
    """
    spafw37.reset()
    
    prompted_value = None
    command_received_value = None
    
    def mock_handler(user_input):
        return user_input.strip()
    
    def test_command():
        nonlocal command_received_value
        command_received_value = param.get_param('test_param')
    
    spafw37.add_params([{
        'name': 'test_param',
        'prompt': 'Enter value',
        'prompt_on': PARAM_PROMPT_ON_START,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
    }])
    
    with patch('builtins.input', return_value='test_value'):
        spafw37.run_cli(['test_cmd'])
    
    assert command_received_value == 'test_value'
```

### Test 8.8.2: PROMPT_ON_COMMAND prompts before each command execution

**Gherkin:**
```gherkin
Given a parameter marked PROMPT_ON_COMMAND
And the parameter is used by a command
When the command executes
Then the parameter is prompted for before the command handler runs
And the command receives the prompted value
```

**Implementation:**
```python
def test_prompt_on_command_executes_per_command():
    """
    Verify that parameters marked PROMPT_ON_COMMAND are prompted for
    before each command that uses them.
    
    Given a parameter marked PROMPT_ON_COMMAND
    And the parameter is used by a command
    When the command executes
    Then the parameter is prompted for before the command handler runs
    And the command receives the prompted value
    """
    spafw37.reset()
    
    command_received_value = None
    
    def test_command():
        nonlocal command_received_value
        command_received_value = param.get_param('cmd_param')
    
    spafw37.add_params([{
        'name': 'cmd_param',
        'prompt': 'Enter command value',
        'prompt_on': PARAM_PROMPT_ON_COMMAND,
        'prompt_repeat': PARAM_PROMPT_REPEAT_ALWAYS,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
        'params': ['cmd_param'],
    }])
    
    with patch('builtins.input', return_value='cmd_value'):
        spafw37.run_cli(['test_cmd'])
    
    assert command_received_value == 'cmd_value'
```

### Test 8.8.3: REPEAT_ALWAYS prompts every cycle iteration

**Gherkin:**
```gherkin
Given a parameter marked PROMPT_ON_COMMAND with REPEAT_ALWAYS
And a command that runs in a cycle with 3 iterations
When the cycle executes
Then the parameter is prompted for 3 times (once per iteration)
And each iteration receives its prompted value
```

**Implementation:**
```python
def test_repeat_always_prompts_every_cycle():
    """
    Verify that PARAM_PROMPT_REPEAT_ALWAYS prompts on every cycle iteration.
    
    Given a parameter marked PROMPT_ON_COMMAND with REPEAT_ALWAYS
    And a command that runs in a cycle with 3 iterations
    When the cycle executes
    Then the parameter is prompted for 3 times (once per iteration)
    And each iteration receives its prompted value
    """
    spafw37.reset()
    
    received_values = []
    prompt_count = [0]
    
    def mock_input(prompt_text):
        prompt_count[0] += 1
        return f'value_{prompt_count[0]}'
    
    def test_command():
        value = param.get_param('cycle_param')
        received_values.append(value)
    
    spafw37.add_params([{
        'name': 'cycle_param',
        'prompt': 'Enter cycle value',
        'prompt_on': PARAM_PROMPT_ON_COMMAND,
        'prompt_repeat': PARAM_PROMPT_REPEAT_ALWAYS,
    }, {
        'name': 'cycle_count',
        'default': '3',
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
        'params': ['cycle_param'],
    }])
    
    spafw37.add_cycles([{
        'command': 'test_cmd',
        'count_param': 'cycle_count',
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        spafw37.run_cli(['test_cmd'])
    
    assert len(received_values) == 3
    assert received_values == ['value_1', 'value_2', 'value_3']
    assert prompt_count[0] == 3
```

### Test 8.8.4: REPEAT_IF_BLANK only prompts when blank

**Gherkin:**
```gherkin
Given a parameter marked PROMPT_ON_COMMAND with REPEAT_IF_BLANK
And a command that runs in a cycle with 3 iterations
When the first prompt provides a value
Then subsequent iterations do not prompt again
And all iterations receive the same value
```

**Implementation:**
```python
def test_repeat_if_blank_prompts_only_when_blank():
    """
    Verify that PARAM_PROMPT_REPEAT_IF_BLANK only prompts when the value is blank.
    
    Given a parameter marked PROMPT_ON_COMMAND with REPEAT_IF_BLANK
    And a command that runs in a cycle with 3 iterations
    When the first prompt provides a value
    Then subsequent iterations do not prompt again
    And all iterations receive the same value
    """
    spafw37.reset()
    
    received_values = []
    prompt_count = [0]
    
    def mock_input(prompt_text):
        prompt_count[0] += 1
        return 'persistent_value'
    
    def test_command():
        value = param.get_param('persistent_param')
        received_values.append(value)
    
    spafw37.add_params([{
        'name': 'persistent_param',
        'prompt': 'Enter persistent value',
        'prompt_on': PARAM_PROMPT_ON_COMMAND,
        'prompt_repeat': PARAM_PROMPT_REPEAT_IF_BLANK,
    }, {
        'name': 'cycle_count',
        'default': '3',
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
        'params': ['persistent_param'],
    }])
    
    spafw37.add_cycles([{
        'command': 'test_cmd',
        'count_param': 'cycle_count',
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        spafw37.run_cli(['test_cmd'])
    
    assert len(received_values) == 3
    assert all(value == 'persistent_value' for value in received_values)
    assert prompt_count[0] == 1
```

### Test 8.8.5: REPEAT_NEVER only prompts once per session

**Gherkin:**
```gherkin
Given a parameter marked PROMPT_ON_COMMAND with REPEAT_NEVER
And multiple commands that use the parameter
When the commands execute in sequence
Then the parameter is only prompted for once
And all commands receive the same value
```

**Implementation:**
```python
def test_repeat_never_prompts_once_per_session():
    """
    Verify that PARAM_PROMPT_REPEAT_NEVER only prompts once per session.
    
    Given a parameter marked PROMPT_ON_COMMAND with REPEAT_NEVER
    And multiple commands that use the parameter
    When the commands execute in sequence
    Then the parameter is only prompted for once
    And all commands receive the same value
    """
    spafw37.reset()
    
    received_values = []
    prompt_count = [0]
    
    def mock_input(prompt_text):
        prompt_count[0] += 1
        return 'session_value'
    
    def test_command_one():
        value = param.get_param('session_param')
        received_values.append(('cmd1', value))
    
    def test_command_two():
        value = param.get_param('session_param')
        received_values.append(('cmd2', value))
    
    spafw37.add_params([{
        'name': 'session_param',
        'prompt': 'Enter session value',
        'prompt_on': PARAM_PROMPT_ON_COMMAND,
        'prompt_repeat': PARAM_PROMPT_REPEAT_NEVER,
    }])
    
    spafw37.add_commands([{
        'name': 'cmd1',
        'handler': test_command_one,
        'params': ['session_param'],
        'next': 'cmd2',
    }, {
        'name': 'cmd2',
        'handler': test_command_two,
        'params': ['session_param'],
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        spafw37.run_cli(['cmd1'])
    
    assert len(received_values) == 2
    assert received_values[0] == ('cmd1', 'session_value')
    assert received_values[1] == ('cmd2', 'session_value')
    assert prompt_count[0] == 1
```

### Test 8.8.6: Nested cycles respect REPEAT settings

**Gherkin:**
```gherkin
Given an outer cycle with 2 iterations
And an inner cycle with 2 iterations per outer iteration
And a parameter marked REPEAT_ALWAYS
When the nested cycles execute
Then the parameter is prompted for 4 times (2 outer × 2 inner)
```

**Implementation:**
```python
def test_nested_cycles_respect_repeat_settings():
    """
    Verify that nested cycles correctly apply PARAM_PROMPT_REPEAT settings.
    
    Given an outer cycle with 2 iterations
    And an inner cycle with 2 iterations per outer iteration
    And a parameter marked REPEAT_ALWAYS
    When the nested cycles execute
    Then the parameter is prompted for 4 times (2 outer × 2 inner)
    """
    spafw37.reset()
    
    received_values = []
    prompt_count = [0]
    
    def mock_input(prompt_text):
        prompt_count[0] += 1
        return f'nested_{prompt_count[0]}'
    
    def inner_command():
        value = param.get_param('nested_param')
        received_values.append(value)
    
    def outer_command():
        pass
    
    spafw37.add_params([{
        'name': 'nested_param',
        'prompt': 'Enter nested value',
        'prompt_on': PARAM_PROMPT_ON_COMMAND,
        'prompt_repeat': PARAM_PROMPT_REPEAT_ALWAYS,
    }, {
        'name': 'outer_count',
        'default': '2',
    }, {
        'name': 'inner_count',
        'default': '2',
    }])
    
    spafw37.add_commands([{
        'name': 'outer_cmd',
        'handler': outer_command,
        'next': 'inner_cmd',
    }, {
        'name': 'inner_cmd',
        'handler': inner_command,
        'params': ['nested_param'],
    }])
    
    spafw37.add_cycles([{
        'command': 'outer_cmd',
        'count_param': 'outer_count',
    }, {
        'command': 'inner_cmd',
        'count_param': 'inner_count',
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        spafw37.run_cli(['outer_cmd'])
    
    assert len(received_values) == 4
    assert received_values == ['nested_1', 'nested_2', 'nested_3', 'nested_4']
    assert prompt_count[0] == 4
```

### Test 8.8.7: CLI values override prompts

**Gherkin:**
```gherkin
Given a parameter marked PROMPT_ON_START
And the parameter is provided via CLI argument
When the CLI runs
Then the parameter is not prompted for
And the CLI value is used
```

**Implementation:**
```python
def test_cli_values_override_prompts():
    """
    Verify that values provided via CLI override prompt requests.
    
    Given a parameter marked PROMPT_ON_START
    And the parameter is provided via CLI argument
    When the CLI runs
    Then the parameter is not prompted for
    And the CLI value is used
    """
    spafw37.reset()
    
    prompt_called = [False]
    command_received_value = None
    
    def mock_input(prompt_text):
        prompt_called[0] = True
        return 'prompted_value'
    
    def test_command():
        nonlocal command_received_value
        command_received_value = param.get_param('cli_param')
    
    spafw37.add_params([{
        'name': 'cli_param',
        'prompt': 'Enter value',
        'prompt_on': PARAM_PROMPT_ON_START,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        spafw37.run_cli(['test_cmd', '--cli-param', 'cli_value'])
    
    assert command_received_value == 'cli_value'
    assert not prompt_called[0]
```

### Test 8.8.8: Custom handlers are used when set

**Gherkin:**
```gherkin
Given a custom prompt handler is set globally
And a parameter marked PROMPT_ON_START
When the CLI runs
Then the custom handler is called for prompting
And the custom handler's return value is used
```

**Implementation:**
```python
def test_custom_handlers_are_used():
    """
    Verify that custom prompt handlers are used when set.
    
    Given a custom prompt handler is set globally
    And a parameter marked PROMPT_ON_START
    When the CLI runs
    Then the custom handler is called for prompting
    And the custom handler's return value is used
    """
    spafw37.reset()
    
    custom_handler_called = [False]
    command_received_value = None
    
    def custom_handler(prompt_text, param_def):
        custom_handler_called[0] = True
        return 'custom_value'
    
    def test_command():
        nonlocal command_received_value
        command_received_value = param.get_param('custom_param')
    
    param.set_prompt_handler(custom_handler)
    
    spafw37.add_params([{
        'name': 'custom_param',
        'prompt': 'Enter value',
        'prompt_on': PARAM_PROMPT_ON_START,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
    }])
    
    spafw37.run_cli(['test_cmd'])
    
    assert command_received_value == 'custom_value'
    assert custom_handler_called[0]
```

### Test 8.8.9: Param-level handlers override global handlers

**Gherkin:**
```gherkin
Given a global prompt handler is set
And a parameter with its own prompt handler
When the parameter is prompted for
Then the parameter-level handler is used
And the global handler is not called
```

**Implementation:**
```python
def test_param_handlers_override_global_handlers():
    """
    Verify that parameter-level prompt handlers override global handlers.
    
    Given a global prompt handler is set
    And a parameter with its own prompt handler
    When the parameter is prompted for
    Then the parameter-level handler is used
    And the global handler is not called
    """
    spafw37.reset()
    
    global_handler_called = [False]
    param_handler_called = [False]
    command_received_value = None
    
    def global_handler(prompt_text, param_def):
        global_handler_called[0] = True
        return 'global_value'
    
    def param_handler(prompt_text, param_def):
        param_handler_called[0] = True
        return 'param_value'
    
    def test_command():
        nonlocal command_received_value
        command_received_value = param.get_param('override_param')
    
    param.set_prompt_handler(global_handler)
    
    spafw37.add_params([{
        'name': 'override_param',
        'prompt': 'Enter value',
        'prompt_on': PARAM_PROMPT_ON_START,
        'prompt_handler': param_handler,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
    }])
    
    spafw37.run_cli(['test_cmd'])
    
    assert command_received_value == 'param_value'
    assert param_handler_called[0]
    assert not global_handler_called[0]
```

### Test 8.8.10: Validation errors trigger retry

**Gherkin:**
```gherkin
Given a parameter with input validation
And the validation fails on first 2 attempts
And the validation passes on 3rd attempt
When the parameter is prompted for
Then the user is prompted 3 times
And the valid value is used
```

**Implementation:**
```python
def test_validation_errors_trigger_retry():
    """
    Verify that validation errors trigger retry with max attempts.
    
    Given a parameter with input validation
    And the validation fails on first 2 attempts
    And the validation passes on 3rd attempt
    When the parameter is prompted for
    Then the user is prompted 3 times
    And the valid value is used
    """
    spafw37.reset()
    
    prompt_count = [0]
    command_received_value = None
    
    def mock_input(prompt_text):
        prompt_count[0] += 1
        if prompt_count[0] < 3:
            return 'invalid'
        return 'valid_value'
    
    def validate_value(value):
        if value != 'valid_value':
            raise ValueError('Invalid value')
        return value
    
    def test_command():
        nonlocal command_received_value
        command_received_value = param.get_param('validated_param')
    
    spafw37.add_params([{
        'name': 'validated_param',
        'prompt': 'Enter value',
        'prompt_on': PARAM_PROMPT_ON_START,
        'input_filter': validate_value,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        spafw37.run_cli(['test_cmd'])
    
    assert command_received_value == 'valid_value'
    assert prompt_count[0] == 3
```

### Test 8.8.11: Max retries exceeded raises exception

**Gherkin:**
```gherkin
Given a parameter with input validation
And the validation always fails
And max retries is set to 3
When the parameter is prompted for
Then the user is prompted 3 times
And a RuntimeError is raised after max retries
```

**Implementation:**
```python
def test_max_retries_exceeded_raises_exception():
    """
    Verify that exceeding max retries raises an exception.
    
    Given a parameter with input validation
    And the validation always fails
    And max retries is set to 3
    When the parameter is prompted for
    Then the user is prompted 3 times
    And a RuntimeError is raised after max retries
    """
    spafw37.reset()
    
    prompt_count = [0]
    
    def mock_input(prompt_text):
        prompt_count[0] += 1
        return 'always_invalid'
    
    def validate_value(value):
        raise ValueError('Always invalid')
    
    def test_command():
        pass
    
    param.set_max_prompt_retries(3)
    
    spafw37.add_params([{
        'name': 'failing_param',
        'prompt': 'Enter value',
        'prompt_on': PARAM_PROMPT_ON_START,
        'input_filter': validate_value,
    }])
    
    spafw37.add_commands([{
        'name': 'test_cmd',
        'handler': test_command,
    }])
    
    with patch('builtins.input', side_effect=mock_input):
        with pytest.raises(RuntimeError) as exc_info:
            spafw37.run_cli(['test_cmd'])
    
    assert 'maximum prompt attempts' in str(exc_info.value).lower()
    assert prompt_count[0] == 3
```

[↑ Back to top](#table-of-contents)

---

#### Phase 3: Documentation

**Step 9: Update documentation**

**Files:** `doc/parameters.md`, `doc/api-reference.md`, `README.md`

Update documentation to reflect new interactive prompt functionality.

**Implementation order:**

1. Update Table of Contents in all affected documentation files
2. Add version notes to new documentation sections
3. Update parameters user guide with prompt functionality
4. Add code examples demonstrating usage patterns
5. Update API reference with new functions and constants
6. Update README with feature summary
7. Add examples to examples list
8. Add "What's New" entry

**Documentation specifications:**

**Doc 9.1: Parameters guide updates**

Add to `doc/parameters.md`:

**First, update the Parameter Definition Constants table to include new prompt-related constants:**

In the "Advanced Configuration" section of the constants table, add:

| Constant | Description |
|----------|-------------|
| `PARAM_PROMPT` | Prompt text to display when soliciting user input. Enables interactive prompting for this parameter. |
| `PARAM_PROMPT_HANDLER` | Custom handler function for this parameter's prompt. Overrides global handler. Signature: `(param_name: str, prompt_text: str, param_def: dict) -> str` |
| `PARAM_PROMPT_TIMING` | When to display prompt: `PROMPT_ON_START` (at application start) or `PROMPT_ON_COMMAND` (before specific commands). |
| `PARAM_PROMPT_REPEAT` | Repeat behaviour: `PROMPT_REPEAT_NEVER` (default, prompt once), `PROMPT_REPEAT_IF_BLANK` (prompt if blank), `PROMPT_REPEAT_ALWAYS` (prompt every time). |
| `PARAM_SENSITIVE` | Boolean flag to suppress terminal echo and hide default values for sensitive data (passwords, API keys, tokens). |

Add new constants section for "Prompt Timing Options":

| Constant | Description |
|----------|-------------|
| `PROMPT_ON_START` | Display prompt at application start (after CLI parsing, before command execution) |
| `PROMPT_ON_COMMAND` | Display prompt before specific command execution (requires `PROMPT_ON_COMMANDS` property) |
| `PROMPT_ON_COMMANDS` | List of command names that trigger this prompt (used with `PROMPT_ON_COMMAND` timing) |

Add new constants section for "Prompt Repeat Behaviour Options":

| Constant | Description |
|----------|-------------|
| `PROMPT_REPEAT_NEVER` | Prompt only on first occurrence, reuse value for subsequent commands/cycles |
| `PROMPT_REPEAT_IF_BLANK` | Prompt again if value becomes blank |
| `PROMPT_REPEAT_ALWAYS` | Prompt every time, preserving previous value as default |

**Then, add the new Interactive Prompts section after the "Custom Input Filters" section:**

````markdown
## Interactive Prompts

**Added in v1.1.0**

Parameters can solicit interactive user input at runtime using the prompt system. This enables workflows requiring dynamic data entry, confirmation dialogues, or sensitive information that shouldn't appear in command history.

The prompt system integrates with existing parameter validation, type handling, and required parameter checking. Prompts respect CLI-provided values (prompting is skipped if the user already supplied a value via `--param-name`), and support custom handlers for advanced use cases such as GUI prompts or automated testing.

### Basic Usage

Enable prompts by setting the `PARAM_PROMPT` property:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PROMPT_ON_START,
)

spafw37.add_params([{
    PARAM_NAME: 'username',
    PARAM_PROMPT: 'Enter username: ',
    PARAM_PROMPT_TIMING: PROMPT_ON_START,
}])
```

When the application runs, users are prompted to enter a value if none was provided via CLI.

**See example:** [params_prompt_basic.py](examples/params_prompt_basic.py)

### Timing Control

The `PARAM_PROMPT_TIMING` property controls when prompts appear:

**PROMPT_ON_START** - Prompt at application start (after CLI parsing, before command execution):

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PROMPT_ON_START,
)

spafw37.add_params([{
    PARAM_NAME: 'api_key',
    PARAM_PROMPT: 'Enter API key: ',
    PARAM_PROMPT_TIMING: PROMPT_ON_START,
}])
```

**PROMPT_ON_COMMAND** - Prompt before specific command execution:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
)

spafw37.add_params([{
    PARAM_NAME: 'confirmation',
    PARAM_PROMPT: 'Proceed with deletion? (yes/no): ',
    PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS: ['delete', 'purge'],
}])
```

The `PROMPT_ON_COMMANDS` property specifies which commands trigger the prompt. This property is automatically populated from `COMMAND_REQUIRED_PARAMS` if not explicitly set.

**See example:** [params_prompt_timing.py](examples/params_prompt_timing.py)

### Repeat Behaviour

The `PARAM_PROMPT_REPEAT` property controls prompt frequency in cycles and when multiple commands use the same param:

**PROMPT_REPEAT_NEVER** (default) - Prompt only on first occurrence:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_REPEAT,
    PROMPT_REPEAT_NEVER,
)

spafw37.add_params([{
    PARAM_NAME: 'batch_size',
    PARAM_PROMPT: 'Enter batch size: ',
    PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER,
}])
```

**PROMPT_REPEAT_IF_BLANK** - Prompt again if value becomes blank:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_REPEAT,
    PROMPT_REPEAT_IF_BLANK,
)

spafw37.add_params([{
    PARAM_NAME: 'iteration_count',
    PARAM_PROMPT: 'Enter count for this iteration: ',
    PARAM_PROMPT_REPEAT: PROMPT_REPEAT_IF_BLANK,
}])
```

**PROMPT_REPEAT_ALWAYS** - Prompt every time (value preserved between prompts):

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_REPEAT,
    PROMPT_REPEAT_ALWAYS,
)

spafw37.add_params([{
    PARAM_NAME: 'continue_processing',
    PARAM_PROMPT: 'Continue processing? (yes/no): ',
    PARAM_PROMPT_REPEAT: PROMPT_REPEAT_ALWAYS,
}])
```

**See example:** [params_prompt_repeat.py](examples/params_prompt_repeat.py)

### Sensitive Data

The `PARAM_SENSITIVE` property suppresses terminal echo and hides default values in prompts:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_SENSITIVE,
)

spafw37.add_params([{
    PARAM_NAME: 'password',
    PARAM_PROMPT: 'Enter password: ',
    PARAM_SENSITIVE: True,
}])
```

When prompting for sensitive params, input is not echoed to the terminal and default values are not displayed in the prompt text.

**See example:** [params_prompt_sensitive.py](examples/params_prompt_sensitive.py)

### Multiple Choice

Use `PARAM_ALLOWED_VALUES` to create selection prompts:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_ALLOWED_VALUES,
)

spafw37.add_params([{
    PARAM_NAME: 'environment',
    PARAM_PROMPT: 'Select environment',
    PARAM_ALLOWED_VALUES: ['development', 'staging', 'production'],
}])
```

The prompt displays numbered options and validates the user's selection.

For dynamic options, use `set_allowed_values()`:

```python
from spafw37 import param

available_regions = get_regions_from_api()
param.set_allowed_values('region', available_regions)
```

**See example:** [params_prompt_choices.py](examples/params_prompt_choices.py)

### Custom Handlers

Replace the default terminal input handler with custom implementations:

**Global handler** (affects all prompt params):

```python
from spafw37 import param

def custom_prompt_handler(param_name, prompt_text, param_def):
    # Custom implementation (e.g., GUI dialogue, automated input)
    return user_input

param.set_prompt_handler(custom_prompt_handler)
```

**Per-param handler** (overrides global handler for specific param):

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_PROMPT_HANDLER,
)

def file_picker_handler(param_name, prompt_text, param_def):
    # Show file picker dialogue
    return selected_file_path

spafw37.add_params([{
    PARAM_NAME: 'input_file',
    PARAM_PROMPT: 'Select input file',
    PARAM_PROMPT_HANDLER: file_picker_handler,
}])
```

Handler precedence: param-level → global → default

**See example:** [params_prompt_handlers.py](examples/params_prompt_handlers.py)

### CLI Override

Prompts are skipped entirely if the parameter value is provided via CLI:

```bash
# This will NOT prompt for username
python myapp.py --username alice process
```

No confirmation is needed; CLI values take absolute precedence.

**See example:** [params_prompt_basic.py](examples/params_prompt_basic.py) (demonstrates CLI override in usage comments)

### Inline Definitions

Commands can define prompt params inline using `COMMAND_PROMPT_PARAMS`, consistent with `COMMAND_REQUIRED_PARAMS`:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_ALLOWED_VALUES,
    PARAM_REQUIRED,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_HANDLER,
    COMMAND_PROMPT_PARAMS,
)

spafw37.add_commands([{
    COMMAND_NAME: 'deploy',
    COMMAND_HANDLER: deploy_handler,
    COMMAND_PROMPT_PARAMS: [
        {
            PARAM_NAME: 'environment',
            PARAM_PROMPT: 'Select environment',
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'prod'],
        },
        {
            PARAM_NAME: 'confirm',
            PARAM_PROMPT: 'Proceed with deployment? (yes/no)',
            PARAM_REQUIRED: True,
        },
    ],
}])
```

This enables rapid prototyping without separate `add_param()` calls whilst maintaining API consistency.

**See also:** Existing inline definition examples in [inline_definitions_basic.py](examples/inline_definitions_basic.py) and [inline_definitions_advanced.py](examples/inline_definitions_advanced.py)

### Validation and Retry

Prompts integrate with existing parameter validation:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_INPUT_FILTER,
)

def validate_port(value):
    port = int(value)
    if not (1 <= port <= 65535):
        raise ValueError("Port must be between 1 and 65535")
    return port

spafw37.add_params([{
    PARAM_NAME: 'port',
    PARAM_PROMPT: 'Enter port number: ',
    PARAM_INPUT_FILTER: validate_port,
}])
```

Invalid input triggers re-prompting with the error message displayed. The framework retries up to the configured maximum (default 3 attempts) before raising an error.

Configure retry limit:

```python
from spafw37 import param

param.set_max_prompt_retries(5)
```

**See example:** [params_prompt_validation.py](examples/params_prompt_validation.py)

---
````

**Update the Table of Contents in `doc/parameters.md` to include:**
```markdown
- [Interactive Prompts](#interactive-prompts)
  - [Basic Usage](#basic-usage)
  - [Timing Control](#timing-control)
  - [Repeat Behaviour](#repeat-behaviour)
  - [Sensitive Data](#sensitive-data)
  - [Multiple Choice](#multiple-choice)
  - [Custom Handlers](#custom-handlers)
  - [CLI Override](#cli-override)
  - [Inline Definitions](#inline-definitions)
  - [Validation and Retry](#validation-and-retry)
```

**Doc 9.2: API reference updates**

Add to `doc/api-reference.md`:

````markdown
### `param.set_prompt_handler(handler)`

**Added in v1.1.0**

Sets a global prompt handler function that replaces the default terminal input handler for all prompt-enabled params.

**Parameters:**
- `handler` - Callable with signature `(param_name: str, prompt_text: str, param_def: dict) -> str`, or `None` to reset to default

**Returns:** None

**Example:**
```python
from spafw37 import param

def automated_handler(param_name, prompt_text, param_def):
    return test_values.get(param_name, 'default')

param.set_prompt_handler(automated_handler)
```

### `param.set_max_prompt_retries(max_retries)`

**Added in v1.1.0**

Sets the maximum number of retry attempts for invalid input before raising an error.

**Parameters:**
- `max_retries` - Integer count of maximum retry attempts (must be >= 1)

**Returns:** None

**Example:**
```python
from spafw37 import param

param.set_max_prompt_retries(5)
```

### `param.set_allowed_values(param_name, allowed_values)`

**Added in v1.1.0**

Dynamically updates the allowed values for a parameter at runtime.

**Parameters:**
- `param_name` - Parameter name string
- `allowed_values` - List of allowed values

**Returns:** None

**Example:**
```python
from spafw37 import param

regions = fetch_available_regions()
param.set_allowed_values('region', regions)
```

---
````

**Update the API reference documentation to add the new functions under the appropriate section (likely "Parameter Module" or "Core Module")**

**If `doc/api-reference.md` has a Table of Contents, update it to include:**
```markdown
- `param.set_prompt_handler(handler)` - Set global prompt handler
- `param.set_max_prompt_retries(max_retries)` - Configure maximum retry attempts  
- `param.set_allowed_values(param_name, allowed_values)` - Dynamically update allowed values
```

**Doc 9.3: README updates**

**Note:** README.md does not have a formal Table of Contents, so no ToC updates needed.

**Features list** - Add bullet point to features section:
```markdown
- Interactive parameter prompts with timing control, repeat behaviour, sensitive data handling, validation retry, and custom handler support
```

**Examples list** - Add entries to examples section:
```markdown
- **`params_prompt_basic.py`** - Basic parameter prompting with PROMPT_ON_START timing
- **`params_prompt_timing.py`** - Prompt timing control (PROMPT_ON_START vs PROMPT_ON_COMMAND)
- **`params_prompt_repeat.py`** - Repeat behaviour modes (NEVER, IF_BLANK, ALWAYS)
- **`params_prompt_sensitive.py`** - Sensitive parameter handling with suppressed echo
- **`params_prompt_choices.py`** - Multiple choice prompts with static and dynamic options
- **`params_prompt_handlers.py`** - Custom prompt handlers (global and per-param)
- **`params_prompt_validation.py`** - Validation integration and retry logic
```

**"What's New in v1.1.0" section** - Add concise bullet points:
```markdown
## What's New in v1.1.0

- Interactive parameter prompts with `PARAM_PROMPT` property, timing control (`PROMPT_ON_START`, `PROMPT_ON_COMMAND`), and repeat behaviour (`PROMPT_REPEAT_NEVER`, `PROMPT_REPEAT_IF_BLANK`, `PROMPT_REPEAT_ALWAYS`)
- Sensitive parameter handling with `PARAM_SENSITIVE` property (suppresses terminal echo and hides default values)
- Custom prompt handlers via `param.set_prompt_handler()` for GUI integration or automated testing
- Inline prompt parameter definitions via `COMMAND_PROMPT_PARAMS` field for rapid prototyping
- Automatic population of `PROMPT_ON_COMMANDS` from `COMMAND_REQUIRED_PARAMS` for seamless integration
- Prompt validation retry with configurable maximum attempts via `param.set_max_prompt_retries()`
```

**Tests:** Manual review to verify documentation clarity and consistency

[↑ Back to top](#table-of-contents)

---

**Step 10: Create example files**

**Files:** `examples/params_prompt_basic.py`, `examples/params_prompt_timing.py`, `examples/params_prompt_repeat.py`, `examples/params_prompt_sensitive.py`, `examples/params_prompt_choices.py`, `examples/params_prompt_handlers.py`, `examples/params_prompt_validation.py`

Create focused examples demonstrating each type of prompt behaviour.

**Implementation order:**

1. Create basic prompting example
2. Create timing control example
3. Create repeat behaviour example
4. Create sensitive data example
5. Create multiple choice example
6. Create custom handlers example
7. Create validation and retry example
8. Test all examples run successfully

**Code 10.1: Basic prompting example (`examples/params_prompt_basic.py`)**

```python
"""Basic parameter prompt demonstration.

This example shows:
- Basic prompt usage with PROMPT_ON_START timing
- Text input and multiple choice prompts
- CLI override behaviour (pass --username value to skip prompt)
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PROMPT_ON_START,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


def process_command():
    """Command handler that displays param values."""
    username = spafw37.get_param_value('username')
    print(f'Processing for user: {username}')


if __name__ == '__main__':
    spafw37.add_params([{
        PARAM_NAME: 'username',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Enter username: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
    }])
    
    spafw37.add_commands([{
        COMMAND_NAME: 'process',
        COMMAND_HANDLER: process_command,
    }])
    
    # If no CLI args provided, will prompt for username
    # Try: python params_prompt_basic.py process
    # Or skip prompt: python params_prompt_basic.py --username alice process
    spafw37.run_cli()
```

**Code 10.2: Timing control example (`examples/params_prompt_timing.py`)**

```python
"""Prompt timing control demonstration.

This example shows:
- PROMPT_ON_START timing (prompt at application start)
- PROMPT_ON_COMMAND timing (prompt before specific commands)
- PROMPT_ON_COMMANDS property (specify which commands trigger prompts)
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PROMPT_ON_START,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


def init_command():
    """Initialisation command."""
    api_key = spafw37.get_param_value('api_key')
    print(f'Initialised with API key: {api_key[:10]}...')


def delete_command():
    """Deletion command requiring confirmation."""
    confirmation = spafw37.get_param_value('confirmation')
    if confirmation.lower() == 'yes':
        print('Deletion confirmed and executed')
    else:
        print('Deletion cancelled')


if __name__ == '__main__':
    # This param prompts at application start
    spafw37.add_params([{
        PARAM_NAME: 'api_key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Enter API key: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
    }])
    
    # This param prompts only before delete command
    spafw37.add_params([{
        PARAM_NAME: 'confirmation',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Proceed with deletion? (yes/no): ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['delete'],
    }])
    
    spafw37.add_commands([
        {
            COMMAND_NAME: 'init',
            COMMAND_HANDLER: init_command,
        },
        {
            COMMAND_NAME: 'delete',
            COMMAND_HANDLER: delete_command,
        },
    ])
    
    # Try: python params_prompt_timing.py init delete
    # api_key prompts at start, confirmation prompts before delete
    spafw37.run_cli()
```

**Code 10.3: Repeat behaviour example (`examples/params_prompt_repeat.py`)**

```python
"""Prompt repeat behaviour demonstration.

This example shows:
- PROMPT_REPEAT_NEVER (prompt only once, reuse value)
- PROMPT_REPEAT_IF_BLANK (prompt again if value becomes blank)
- PROMPT_REPEAT_ALWAYS (prompt every time)
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
    PROMPT_REPEAT_NEVER,
    PROMPT_REPEAT_ALWAYS,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


iteration_count = [0]


def iterate_command():
    """Command that runs multiple times."""
    iteration_count[0] += 1
    batch_size = spafw37.get_param_value('batch_size')
    continue_flag = spafw37.get_param_value('continue_flag')
    print(f'Iteration {iteration_count[0]}: batch_size={batch_size}, continue={continue_flag}')


if __name__ == '__main__':
    # This param prompts only once (default behaviour)
    spafw37.add_params([{
        PARAM_NAME: 'batch_size',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_PROMPT: 'Enter batch size: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['iterate'],
        PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER,
    }])
    
    # This param prompts every time
    spafw37.add_params([{
        PARAM_NAME: 'continue_flag',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Continue processing? (yes/no): ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['iterate'],
        PARAM_PROMPT_REPEAT: PROMPT_REPEAT_ALWAYS,
    }])
    
    spafw37.add_commands([{
        COMMAND_NAME: 'iterate',
        COMMAND_HANDLER: iterate_command,
    }])
    
    # Try: python params_prompt_repeat.py iterate iterate iterate
    # batch_size prompts once, continue_flag prompts every time
    spafw37.run_cli()
```

**Code 10.4: Sensitive data example (`examples/params_prompt_sensitive.py`)**

```python
"""Sensitive parameter handling demonstration.

This example shows:
- PARAM_SENSITIVE property to suppress echo
- Password input without terminal display
- Default value suppression for sensitive params
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_SENSITIVE,
    PROMPT_ON_START,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


def login_command():
    """Login command using password."""
    username = spafw37.get_param_value('username')
    password = spafw37.get_param_value('password')
    print(f'Login attempt for user: {username}')
    print(f'Password length: {len(password)} characters')
    print('(Password not displayed for security)')


if __name__ == '__main__':
    spafw37.add_params([
        {
            PARAM_NAME: 'username',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_PROMPT: 'Enter username: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
        {
            PARAM_NAME: 'password',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_PROMPT: 'Enter password: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_SENSITIVE: True,
        },
    ])
    
    spafw37.add_commands([{
        COMMAND_NAME: 'login',
        COMMAND_HANDLER: login_command,
    }])
    
    # Try: python params_prompt_sensitive.py login
    # Username displays as you type, password does not
    spafw37.run_cli()
```

**Code 10.5: Multiple choice example (`examples/params_prompt_choices.py`)**

```python
"""Multiple choice prompt demonstration.

This example shows:
- Static multiple choice with PARAM_ALLOWED_VALUES
- Numbered selection display
- Dynamic population with set_allowed_values()
"""

from spafw37 import core as spafw37
from spafw37 import param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_ALLOWED_VALUES,
    PROMPT_ON_START,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


def deploy_command():
    """Deployment command."""
    environment = spafw37.get_param_value('environment')
    region = spafw37.get_param_value('region')
    print(f'Deploying to {environment} environment in {region} region')


if __name__ == '__main__':
    # Static multiple choice
    spafw37.add_params([{
        PARAM_NAME: 'environment',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Select environment',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_ALLOWED_VALUES: ['development', 'staging', 'production'],
    }])
    
    # Dynamic multiple choice
    spafw37.add_params([{
        PARAM_NAME: 'region',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Select region',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
    }])
    
    # Populate region choices dynamically
    available_regions = ['us-east', 'us-west', 'eu-central', 'ap-south']
    param.set_allowed_values('region', available_regions)
    
    spafw37.add_commands([{
        COMMAND_NAME: 'deploy',
        COMMAND_HANDLER: deploy_command,
    }])
    
    # Try: python params_prompt_choices.py deploy
    # Both prompts display numbered options
    spafw37.run_cli()
```

**Code 10.6: Custom handlers example (`examples/params_prompt_handlers.py`)**

```python
"""Custom prompt handler demonstration.

This example shows:
- Global prompt handler with set_prompt_handler()
- Per-param handler with PARAM_PROMPT_HANDLER
- Handler precedence (param-level → global → default)
"""

from spafw37 import core as spafw37
from spafw37 import param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_HANDLER,
    PROMPT_ON_START,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


automated_values = {
    'api_key': 'test-api-key-12345',
    'region': 'us-west',
    'batch_size': '100',
}


def automated_handler(param_name, prompt_text, param_def):
    """Global automated handler for testing."""
    value = automated_values.get(param_name, 'default')
    print(f'{prompt_text}{value} (automated)')
    return value


def custom_batch_handler(param_name, prompt_text, param_def):
    """Custom handler for batch size param only."""
    print(f'{prompt_text}50 (custom handler)')
    return '50'


def process_command():
    """Process command."""
    api_key = spafw37.get_param_value('api_key')
    region = spafw37.get_param_value('region')
    batch_size = spafw37.get_param_value('batch_size')
    print(f'API Key: {api_key[:10]}...')
    print(f'Region: {region}')
    print(f'Batch Size: {batch_size}')


if __name__ == '__main__':
    # Set global handler
    param.set_prompt_handler(automated_handler)
    
    # These params use global handler
    spafw37.add_params([
        {
            PARAM_NAME: 'api_key',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_PROMPT: 'Enter API key: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
        {
            PARAM_NAME: 'region',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_PROMPT: 'Select region: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
    ])
    
    # This param uses custom handler (overrides global)
    spafw37.add_params([{
        PARAM_NAME: 'batch_size',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_PROMPT: 'Enter batch size: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_PROMPT_HANDLER: custom_batch_handler,
    }])
    
    spafw37.add_commands([{
        COMMAND_NAME: 'process',
        COMMAND_HANDLER: process_command,
    }])
    
    # Try: python params_prompt_handlers.py process
    # All prompts automated, batch_size uses custom handler
    spafw37.run_cli()
    
    # Clean up
    param.set_prompt_handler(None)
```

**Code 10.7: Validation and retry example (`examples/params_prompt_validation.py`)**

```python
"""Prompt validation and retry demonstration.

This example shows:
- Integration with PARAM_INPUT_FILTER validation
- Retry logic on invalid input
- Maximum retry configuration with set_max_prompt_retries()
- Error messages displayed to user
"""

from spafw37 import core as spafw37
from spafw37 import param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_INPUT_FILTER,
    PROMPT_ON_START,
)
from spafw37.constants.command import COMMAND_NAME, COMMAND_HANDLER


def validate_port(value):
    """Validate port number is in valid range."""
    try:
        port = int(value)
        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return port
    except ValueError as error:
        raise ValueError(f"Invalid port: {error}")


def validate_email(value):
    """Validate email address format."""
    if '@' not in value or '.' not in value.split('@')[-1]:
        raise ValueError("Invalid email format")
    return value.lower()


def connect_command():
    """Connection command."""
    host = spafw37.get_param_value('host')
    port = spafw37.get_param_value('port')
    email = spafw37.get_param_value('email')
    print(f'Connecting to {host}:{port}')
    print(f'Notification email: {email}')


if __name__ == '__main__':
    # Configure maximum retry attempts
    param.set_max_prompt_retries(3)
    
    spafw37.add_params([
        {
            PARAM_NAME: 'host',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_PROMPT: 'Enter hostname: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
        {
            PARAM_NAME: 'port',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_PROMPT: 'Enter port number: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_INPUT_FILTER: validate_port,
        },
        {
            PARAM_NAME: 'email',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_PROMPT: 'Enter notification email: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_INPUT_FILTER: validate_email,
        },
    ])
    
    spafw37.add_commands([{
        COMMAND_NAME: 'connect',
        COMMAND_HANDLER: connect_command,
    }])
    
    # Try: python params_prompt_validation.py connect
    # Enter invalid port (e.g., 99999) to see retry behaviour
    # Enter invalid email (e.g., notanemail) to see validation error
    spafw37.run_cli()
```

**Tests:** Manual verification that all examples run without errors

[↑ Back to top](#table-of-contents)

---

## Further Considerations

### 1. Design Pattern Research - RESOLVED

([#issuecomment-3587791560](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791560))

**Question:** How do other CLI frameworks handle interactive user input?

**Answer:** Use Python's built-in `input()` function as the default handler, with extensibility support.

**Implementation:**
- Default prompt handler implemented in new file `input_prompt.py` using `input()` function
- Extensible via `PARAM_PROMPT_HANDLER` property (per-param override) or `set_prompt_handler()` method (global override)
- **Text:** Use `input()` with string return value
- **Boolean:** Accept yes/no, y/n, true/false with case-insensitive matching
- **Number:** Use `input()` with int() or float() conversion, retry on ValueError
- **Multiple choice:** Display numbered list, accept either number or text value
- **Error handling:** Retry on invalid input with clear error message

**Rationale:** Python's built-in `input()` function is simple, requires no dependencies, works on all platforms, and is what most Python CLI tools use. Extensible design allows custom handlers for advanced use cases (GUI prompts, API-based input, etc.) whilst providing sensible default behaviour.

**Resolves:** Q7 (User Input Mechanism)

[↑ Back to top](#table-of-contents)

---

### 2. Architecture Approach Trade-offs - RESOLVED

([#issuecomment-3587791581](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791581))

**Question:** What are the pros and cons of each architecture approach?

**Answer:** Option A - Param-level approach.

**Design details:**
- Add `PARAM_PROMPT` property to param definitions (e.g., `{PARAM_PROMPT: "What is the air-speed velocity of an unladen swallow?"}`)
- Add `PARAM_PROMPT_HANDLER` property (optional) to override default prompt handler for specific params
- Add `set_prompt_handler()` method to `param.py` (delegated in `core.py`) to set global prompt handler function
- Default prompt handler (using `input()` function) will be implemented in new file `input_prompt.py`
- Use existing `PARAM_TYPE` to determine input handling:
  - `PARAM_TYPE_TEXT` - accepts any text input
  - `PARAM_TYPE_NUMBER` - validates numeric input
  - `PARAM_TYPE_TOGGLE` - accepts boolean values
- Multiple choice automatically enabled when `PARAM_ALLOWED_VALUES` is present:
  - Display numbered list of allowed values
  - User can enter either the text value or the corresponding number
  - List displayed automatically with assigned numbers
- **Inline definition support:** Commands can define prompt-enabled params inline in `COMMAND_PROMPT_PARAMS` using dictionary definitions, consistent with inline definitions in `COMMAND_REQUIRED_PARAMS`, `COMMAND_TRIGGER_PARAM`, and dependency fields. This enables rapid prototyping without separately registering every param.
- **Future consideration:** May expand to support lists with multiple choice (enter choices by number separated by spaces or commas) - provisional only

**Rationale:** Integrates with existing param system, validation, and type handling. Leverages existing properties where possible (`PARAM_TYPE`, `PARAM_ALLOWED_VALUES`). Extensible design allows custom prompt handlers for advanced use cases (GUI prompts, API-based input, etc.) whilst providing sensible default behaviour. Inline definition support maintains API consistency with existing framework patterns (see `examples/inline_definitions_basic.py` and `examples/inline_definitions_advanced.py`).

**Breaking changes:** Low (new optional properties only).

**Resolves:** Q1 (Architecture Approach)

[↑ Back to top](#table-of-contents)

---

### 3. Implementation Complexity Assessment - RESOLVED

([#issuecomment-3587791599](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791599))

**Question:** What is the relative complexity of different aspects of this feature?

**Answer:**

**Low complexity:**
- Text input with `input()` function ✅ (Decided: use Python's `input()` as default in `input_prompt.py`)
- Basic type conversion (only relevant for `get_param()` retrieval and multi-choice number resolution)
- CLI override behaviour ✅ (Decided: "if set, don't prompt")
- Prompt handler extensibility ✅ (Decided: `PARAM_PROMPT_HANDLER` property and `set_prompt_handler()` method)

**Medium complexity:**
- Type validation ✅ (Decided: use existing framework validation functions)
- Default handling ✅ (Decided: bash convention `[default: value]`, blank selects default)
- Retry logic ✅ (Decided: re-prompt on error, max retry limit with required/optional behaviour)
- Boolean/number parsing ✅ (Decided: use existing `INPUT_FILTER`, toggles use y/n with natural defaults)
- Multiple choice with static lists ✅ (Decided: use `PARAM_ALLOWED_VALUES`)
- Timing control ✅ (Decided: `PARAM_PROMPT_TIMING` with `PROMPT_ON_START` / `PROMPT_ON_COMMAND`, command list in `PROMPT_ON_COMMANDS` property)
- Cycle integration ✅ (Decided: `PARAM_PROMPT_REPEAT` with `PROMPT_REPEAT_ALWAYS` / `PROMPT_REPEAT_IF_BLANK` / `PROMPT_REPEAT_NEVER`)

**High complexity:**
- Multiple choice with dynamic population ✅ (Decided: new public API `set_allowed_values()` method)

**Very high complexity (deferred):**
- Command-driven population ❌ (Not implementing as special feature in this version, achievable via `set_allowed_values()`)

**Status:** All decisions made. Ready for implementation.

**Rationale:** Helps prioritise features and identify implementation risks. Most features leverage existing framework infrastructure, reducing complexity. Timing/cycle control moved to medium complexity due to clean param-level property design.

**Implementation:** Phased approach - core features first (text, validation, defaults, retries), then timing/cycle control, then advanced features (dynamic population).

**Resolves:** Q2, Q3, Q4, Q5, Q6, Q7, Q8

[↑ Back to top](#table-of-contents)

---

### 4. User Experience Considerations - RESOLVED

([#issuecomment-3587791616](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791616))

**Question:** How should prompts interact with existing framework features?

**Answer:** Several UX questions resolved:
- **Batch mode:** Interactive prompts incompatible with batch/automated execution by design. Missing required params fail with existing validation errors. No special handling needed.
- **Testing:** Mock user input using stdin redirection or test fixtures
- **Help text:** Add "Will prompt if not provided" to param description
- **Error messages:** Provide clear guidance when prompts fail or are unavailable (e.g., EOF, stdin closed)

**Note:** `--silent` suppresses console logging, not interactive prompts.

**Rationale:** Prompts must work seamlessly with existing framework features and not break automated workflows. Ensures framework remains scriptable.

**Implementation:** Depends on Q8 answer (RESOLVED) and overall architecture choice (RESOLVED).

**Resolves:** Q8 (Silent/Batch Mode)

[↑ Back to top](#table-of-contents)

---

### 5. Alternative Solutions - RESOLVED

([#issuecomment-3587791636](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791636))

**Question:** Should this be built into the framework at all?

**Answer:** Yes, this adds important functionality to the framework. Users can currently achieve interactive prompts by using Python's `input()` directly in command actions, using external prompt libraries (Click, Inquirer, PyInquirer), or creating helper functions in their application code. However, framework integration provides significant value through unified parameter handling, validation, and timing control.

**Rationale:** Whilst adding this increases complexity and maintenance burden, the complexity is manageable and the feature remains minimal risk due to:
- Single-threaded execution model
- Entirely opt-in behaviour (no impact on existing code)
- Complexity isolated behind simple helper method `is_prompt_required()` at command execution points
- Implementation complexity hidden in dedicated prompt handling functions

The additional complexity is justified by the benefits: integrated validation, type handling, timing control, cycle support, and extensible handler architecture. All complexity introduction points can be bypassed by a single check of `is_prompt_required()` when a command is dequeued and run—the complex logic is safely encapsulated in separate functions.

**Implementation:** Framework integration provides sufficient value over alternatives. Proceed with implementation as planned.

**Resolves:** Decision to proceed with framework integration

[↑ Back to top](#table-of-contents)

---

### 6. Backward Compatibility and Breaking Changes - RESOLVED

([#issuecomment-3587791658](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791658))

**Question:** What breaking changes might this introduce?

**Answer:** With param-level architecture chosen (see FC2), risk is **low to medium**:

**Low risk aspects:**
- New optional param properties (`PARAM_PROMPT`, `PARAM_PROMPT_HANDLER`, `PARAM_PROMPT_TIMING`, `PARAM_PROMPT_REPEAT`)
- New public API methods (`set_prompt_handler()`, `set_allowed_values()`)
- New file `input_prompt.py` containing default handler
- Existing params without these properties remain completely unaffected

**Medium risk aspects:**
- Param processing logic changes to check for and execute prompts
- Timing of param value availability (prompts occur before command execution)
- Interaction with existing validation and required param checking

**Mitigation:** All prompt functionality is opt-in. Params without `PARAM_PROMPT` property behave exactly as before. No changes to existing command execution flow for non-prompted params.

**Rationale:** Param-level approach with new optional properties minimises risk. Existing applications continue to work without modification.

**Implementation:** Comprehensive regression testing required to ensure no impact on existing param/command behaviour.

**Resolves:** Clarifies breaking change risk for chosen architecture

[↑ Back to top](#table-of-contents)

---

### 7. Testing Strategy - RESOLVED

([#issuecomment-3587791692](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791692))

**Question:** How will interactive prompts be tested?

**Answer:** Mocking `stdin` is straightforward in Python and the project already uses pytest's `monkeypatch` fixture extensively (see `tests/test_core.py`). Interactive prompts can be tested using standard Python testing approaches.

**Implementation approach:**

**Simple stdin mocking with StringIO:**
```python
from io import StringIO
import sys

# In test function:
test_input = StringIO("user response\n")
monkeypatch.setattr('sys.stdin', test_input)
result = input_prompt_handler(param_def)  # Calls input() internally
assert result == "user response"
```

**Multiple inputs for retry logic:**
```python
# Test retry on invalid input, then valid input
test_inputs = StringIO("invalid\nvalid\n")
monkeypatch.setattr('sys.stdin', test_inputs)
result = prompt_with_validation(param_def)
assert result == "valid"
```

**EOF and error handling:**
```python
# Test EOF behaviour
empty_input = StringIO("")
monkeypatch.setattr('sys.stdin', empty_input)
with pytest.raises(EOFError):
    input_prompt_handler(param_def)
```

**Test structure:**
- **Unit tests (`tests/test_input_prompt.py`):** Test default handler in isolation with various input types, validation, and error conditions
- **Integration tests (`tests/test_param_prompts.py`):** Test prompt execution with timing/repeat settings, CLI override, validation integration
- **Cycle tests (`tests/test_integration_prompts.py`):** Test prompt behaviour in cycles with different repeat settings

**Test fixtures for common scenarios:**
- Valid input (text, number, toggle, multiple choice)
- Invalid input requiring retry
- EOF/interrupt conditions
- Default value selection (blank input)
- CLI override scenarios

**Rationale:** Python's `StringIO` provides simple, reliable stdin mocking. The project already uses `monkeypatch` extensively, so no new testing infrastructure required. Interactive code is straightforward to test with this approach.

**Implementation:** Use pytest with `monkeypatch` fixture and `StringIO` for stdin mocking. Create helper fixtures for common test scenarios to reduce boilerplate.

**Resolves:** Testing infrastructure and approach confirmed

[↑ Back to top](#table-of-contents)

## Fixing Regressions

[PENDING REVIEW - To be completed if regressions are discovered during testing]

## Implementation Plan Changes

### Phase 1: Core Infrastructure (COMPLETED)

**Changes during implementation:**

1. **Test file organisation**: Created separate test files for better organisation:
   - `tests/test_constants.py` - All constant definition tests (7 tests added)
   - `tests/test_input_prompt.py` - Input handler module tests (13 tests added)
   - `tests/test_param_prompts.py` - Param registration and API tests (14 tests added)
   - Total: 34 new tests, all passing

2. **Module implementation**: `input_prompt.py` implemented with all handlers as specified:
   - `_format_prompt_text()` - Bash-style default value display with sensitive param support
   - `_handle_text_input()` - Text input with stripped whitespace
   - `_handle_number_input()` - Int/float conversion with error handling
   - `_handle_toggle_input()` - Multiple boolean format support (y/yes/true, n/no/false)
   - `_handle_multiple_choice_input()` - Numeric and text selection
   - `_display_multiple_choice_options()` - Numbered list display
   - `prompt_for_value()` - Main entry point with getpass integration for sensitive params

3. **Param module enhancements**: Added to `param.py`:
   - Module-level state variables (`_global_prompt_handler`, `_prompted_params`, `_PROMPT_AUTO_POPULATE`)
   - Validation functions (`_validate_prompt_timing()`, `_validate_prompt_repeat()`)
   - Integration function (`_validate_and_process_prompt_properties()`) called from `add_param()`
   - Public APIs (`set_prompt_handler()`, `set_allowed_values()`)
   - All 13 new prompt-related constants imported from `constants/param.py`

4. **Test coverage**: All new code tested with full mocking:
   - `monkeypatch.setattr('sys.stdin', StringIO(...))` for input() mocking
   - `monkeypatch.setattr('spafw37.input_prompt.getpass', mock_fn)` for getpass mocking
   - All tests non-interactive (complete in 0.20-0.33 seconds)
   - No regressions: All 663 existing tests still pass
   - Overall coverage: 95.86% (well above 80% requirement)

5. **Constants verified**: All constants defined and tested:
   - 9 param-level constants in `constants/param.py`
   - 3 timing constants in `constants/param.py`
   - 3 repeat behaviour constants in `constants/param.py`
   - 1 command-level constant in `constants/command.py`

**No deviations from original plan** - Phase 1 implementation followed the plan exactly as specified.

### Phase 2: Prompt Execution (COMPLETED)

**Completed Components (Steps 5.1-5.6):**

1. **Handler resolution system** (`src/spafw37/param.py`):
   - `_global_prompt_handler` module variable for global handler storage
   - `set_prompt_handler()` public API for setting global handler
   - `_get_prompt_handler()` with three-tier precedence: param-level → global → default
   - All 4 handler resolution tests passing

2. **Helper functions for prompt orchestration** (`src/spafw37/param.py`):
   - `_param_value_is_set()` - CLI override detection (checks if param has non-empty value)
   - `_timing_matches_context()` - matches param timing to execution context (start vs command)
   - `_should_repeat_prompt()` - checks repeat behaviour based on history and mode
   - `_should_prompt_param()` - top-level orchestration combining CLI override, timing, and repeat checks
   - All 13 helper function tests passing (8 unit + 5 integration tests)

3. **Prompt execution with retry logic** (`src/spafw37/param.py`):
   - Module variables: `_max_prompt_retries = 3`, `_output_handler = None`
   - `set_output_handler()` - public API for custom user-facing message display
   - `set_max_prompt_retries()` - public API for configuring global retry limit
   - `log_param()` - sensitive-aware logging helper (redacts PARAM_SENSITIVE values)
   - `raise_param_error()` - sensitive-aware exception helper (preserves error type, sanitises message)
   - `_should_continue_after_prompt_error()` - pure retry decision function (returns should_retry, prompt_count tuple)
   - `_display_prompt_validation_error()` - user feedback helper (via output handler or print)
   - `_handle_prompt_error_stop()` - max retry error handling (raises for required params, returns for optional)
   - `_execute_prompt()` - main orchestration with validation retry loop
   - All 21 execution tests passing (retry logic, error handling, sensitive data sanitisation)

4. **Param identification functions** (`src/spafw37/param.py`):
   - `_get_params_to_prompt(timing)` - identifies params for start timing (PROMPT_ON_START)
   - `_get_params_for_command(command_def)` - identifies params for command timing (COMMAND_PROMPT_PARAMS list)
   - Both functions filter by `_should_prompt_param()` and resolve handlers via `_get_prompt_handler()`
   - Return list of (param_name, param_def, handler) tuples ready for execution
   - All 4 identification tests passing

5. **Prompt orchestration function** (`src/spafw37/param.py`):
   - `_execute_prompts(params_to_prompt)` - executes prompts for list of params
   - Calls `_execute_prompt()` for each param (sets value, may raise)
   - Tracks successful prompts in `_prompted_params` set for PROMPT_REPEAT_NEVER logic
   - All 2 orchestration tests passing

6. **Public API functions** (`src/spafw37/param.py`):
   - `prompt_params_for_start()` - prompts all PROMPT_ON_START params (called by cli.py)
   - `prompt_params_for_command(command_def)` - prompts all COMMAND_PROMPT_PARAMS params (called by command.py)
   - Both functions chain identification → execution steps
   - Early return optimisation when no params to prompt
   - All 5 public API tests passing

7. **Test coverage**: Complete Phase 2 implementation tested:
   - Unit tests for each helper function in isolation
   - Integration tests for timing enforcement (PROMPT_ON_START, PROMPT_ON_COMMAND)
   - Integration tests for repeat behaviour (NEVER, IF_BLANK, ALWAYS)
   - Integration test for CLI override preventing prompt
   - Retry logic tests (infinite retries, zero retries, finite retries continue/stop)
   - Error handling tests (required param raises, optional param returns, sensitive data sanitised)
   - Full execution flow tests (success, retry succeeds, max retries for required/optional)
   - Identification tests (timing filtering, handler resolution)
   - Orchestration tests (tracking, error propagation)
   - Public API tests (start and command timing, empty list handling)
   - Total: 65 tests in test_param_prompts.py (all passing)
   - No regressions: All 683 existing tests still pass (1 skipped)
   - Overall coverage maintained above 80% requirement

8. **CLI integration** (`src/spafw37/cli.py`):
   - Added `param.prompt_params_for_start()` call at line 277 (after `_parse_command_line()`, before `command.run_command_queue()`)
   - Prompts for all `PROMPT_ON_START` params after CLI parsing and before command execution
   - Integration point: Between tokenized argument parsing and command queue execution
   - Enables start-timing prompts to respect CLI overrides from command-line arguments
   - Verified with manual testing: All 44 command tests pass, no regressions

9. **Command integration** (`src/spafw37/command.py`):
   - Added `param.prompt_params_for_command(cmd)` call at line 544 (after `_verify_command_params()`, before `action()`)
   - Prompts for all `COMMAND_PROMPT_PARAMS` params before each command action execution
   - Integration point: In `run_command_queue()` function's command execution loop
   - Enables command-timing prompts to execute before each command action in the queue
   - Verified with manual testing: All 44 command tests pass, no regressions

10. **Integration testing** (`tests/test_integration_prompts.py`):
   - Created simplified integration test validating end-to-end PROMPT_ON_START workflow
   - Test verifies complete integration from CLI invocation → prompt execution → command completion
   - Single comprehensive test validates: CLI parsing, prompt timing, value propagation to commands
   - Simplified from original 11-test spec due to framework lifecycle limitations (phases complete after first run)
   - More comprehensive coverage exists in test_param_prompts.py (65 unit tests covering all functionality)
   - Created Issue #63 for add_cycles() API to enable more flexible integration testing in future

**Phase 2 Status: COMPLETED**

All Phase 2 steps (5.1-5.8) completed successfully:
- Steps 5.1-5.6: Prompt execution layer (65 unit tests passing)
- Step 6: CLI integration (prompt_params_for_start added)
- Step 7: Command integration (prompt_params_for_command added)
- Step 8: Integration testing (1 end-to-end test passing, 65 unit tests provide comprehensive coverage)

**Pending Components:**

- Phase 3: Documentation updates (doc/parameters.md, doc/api-reference.md, README.md, 7 example scripts)

**Implementation notes:**
- Used `get_param(param_name=...)` instead of `config.get()` for param value retrieval (correct API)
- Used `set_param(param_name=..., value=...)` for setting prompted values (correct API)
- All helper functions use simple control flow (max 2 nesting levels)
- Repeat tracking uses module-level `_prompted_params` set
- Timing matching uses command_name=None for start context, command name string for command context
- Retry logic supports infinite retries (max_retries=0), zero retries (max_retries=-1), and finite retries (max_retries>0)
- Sensitive data sanitisation applied consistently in logging, exceptions, and error messages
- Output handler allows custom user message display (defaults to print if not set)
- Identification functions filter by timing, CLI override, and repeat behaviour before resolving handlers
- Orchestration layers: identification → execution → tracking (clean separation of concerns)
- Public APIs provide clean interface for CLI and command integration

### Phase 3: Documentation (NOT YET IMPLEMENTED)

Status: Awaiting implementation. This phase requires:
- `doc/parameters.md` updates
- `doc/api-reference.md` updates
- `README.md` updates
- 7 example scripts creation

**Current implementation status:**
- **Phase 1:** ✅ COMPLETED (34/34 tests passing) - Core infrastructure and constants
- **Phase 2:** ✅ COMPLETED (66/66 tests passing) - Prompt execution layer, CLI integration (Step 6), Command integration (Step 7), Integration testing (Step 8)
- **Phase 3:** ⚠️ PENDING - Documentation updates (doc/parameters.md, doc/api-reference.md, README.md, 7 example scripts)

## Documentation Updates

[PENDING REVIEW - To be completed in Step 5]

## CHANGES for v1.1.0 Release

**Note:** This section must follow the format specified in `features/CHANGES-TEMPLATE.md`. The content will be posted as the closing comment and consumed by the release workflow.

Issue #15: User Input Params

### Issues Closed

- #15: User Input Params

### Additions

**Constants in `src/spafw37/constants/param.py`:**
- `PARAM_PROMPT` - Prompt text to display when soliciting user input.
- `PARAM_PROMPT_HANDLER` - Custom handler function for parameter-specific prompt behaviour.
- `PARAM_PROMPT_TIMING` - Controls when prompts appear (start or command execution).
- `PARAM_PROMPT_REPEAT` - Controls repeat behaviour in cycles and multiple commands.
- `PARAM_SENSITIVE` - Boolean flag to suppress terminal echo for sensitive data.
- `PROMPT_ON_START` - Timing constant for prompting at application start.
- `PROMPT_ON_COMMAND` - Timing constant for prompting before specific commands.
- `PROMPT_ON_COMMANDS` - Property containing list of commands that trigger prompts.
- `PROMPT_REPEAT_NEVER` - Repeat behaviour constant for prompting only once.
- `PROMPT_REPEAT_IF_BLANK` - Repeat behaviour constant for prompting when value becomes blank.
- `PROMPT_REPEAT_ALWAYS` - Repeat behaviour constant for prompting every time.

**Constants in `src/spafw37/constants/command.py`:**
- `COMMAND_PROMPT_PARAMS` - Command property for inline prompt parameter definitions.

**Module `src/spafw37/input_prompt.py`:**
- `prompt_for_value()` function provides default terminal-based prompt handling using `input()` for regular parameters and `getpass.getpass()` for sensitive parameters, with support for multiple choice display and validation retry.

**Functions in `src/spafw37/param.py`:**
- `set_prompt_handler()` function sets global prompt handler for all parameters.
- `_get_prompt_handler()` internal function resolves handler precedence (param-level → global → default).
- `_global_prompt_handler` module-level variable stores global prompt handler.
- `_prompted_params` module-level set tracks prompt history for `PROMPT_REPEAT_NEVER` behaviour.
- `_param_value_is_set()` internal function checks if parameter has a value (CLI override detection).
- `_timing_matches_context()` internal function verifies timing configuration matches execution context.
- `_should_prompt_param()` internal function orchestrates all prompt decision logic.
- `set_max_prompt_retries()` function configures maximum retry attempts for invalid input.
- `set_allowed_values()` function dynamically updates allowed values at runtime.

**Integration in `src/spafw37/cli.py` and `src/spafw37/command.py`:**
- Prompt execution integrated at application start for `PROMPT_ON_START` timing.
- Prompt execution integrated before command execution for `PROMPT_ON_COMMAND` timing.
- `COMMAND_PROMPT_PARAMS` inline definitions processed during command registration.
- `PROMPT_ON_COMMANDS` property auto-populated from `COMMAND_REQUIRED_PARAMS`.
- Reciprocal `COMMAND_PROMPT_PARAMS` list built on commands for O(1) lookup.

**Examples:**
- `examples/params_prompt_basic.py` - Basic parameter prompting with `PROMPT_ON_START` timing.
- `examples/params_prompt_timing.py` - Prompt timing control (`PROMPT_ON_START` vs `PROMPT_ON_COMMAND`).
- `examples/params_prompt_repeat.py` - Repeat behaviour modes (NEVER, IF_BLANK, ALWAYS).
- `examples/params_prompt_sensitive.py` - Sensitive parameter handling with suppressed echo.
- `examples/params_prompt_choices.py` - Multiple choice prompts with static and dynamic options.
- `examples/params_prompt_handlers.py` - Custom prompt handlers (global and per-param).
- `examples/params_prompt_validation.py` - Validation integration and retry logic.

### Removals

None.

### Changes

- Parameters can now solicit interactive user input at runtime using the `PARAM_PROMPT` property and associated timing/repeat controls.
- Prompts integrate with existing parameter validation, type handling, and required parameter checking.
- Prompts respect CLI-provided values (prompting skipped entirely if user already supplied value via `--param-name`).
- Multiple choice prompts automatically enabled when `PARAM_ALLOWED_VALUES` is present, displaying numbered options.
- Sensitive parameters suppress terminal echo and hide default values when `PARAM_SENSITIVE` is `True`.
- Custom prompt handlers supported via per-param `PARAM_PROMPT_HANDLER` property or global `set_prompt_handler()` method.
- Prompt timing controlled via `PARAM_PROMPT_TIMING` property with `PROMPT_ON_START` (at application start) or `PROMPT_ON_COMMAND` (before specific commands) options.
- Repeat behaviour in cycles controlled via `PARAM_PROMPT_REPEAT` property with `PROMPT_REPEAT_NEVER` (prompt once), `PROMPT_REPEAT_IF_BLANK` (prompt if blank), or `PROMPT_REPEAT_ALWAYS` (prompt every time) options.
- Commands can define prompt parameters inline using `COMMAND_PROMPT_PARAMS` field, consistent with existing inline definition patterns.
- `PROMPT_ON_COMMANDS` property automatically populated from `COMMAND_REQUIRED_PARAMS` if not explicitly set.
- Invalid input triggers re-prompting with error message displayed, up to configurable maximum retry limit (default 3 attempts).

### Migration

No migration required. This is new functionality only. All prompt features are opt-in via new parameter properties.

**Note:** Parameters without `PARAM_PROMPT` property behave exactly as before with no changes to existing functionality. Applications that do not use prompt features will see no behaviour changes.

### Documentation

- `doc/parameters.md` - Added "Interactive Prompts" section with comprehensive usage guide covering basic usage, timing control, repeat behaviour, sensitive data, multiple choice, custom handlers, CLI override, inline definitions, and validation/retry. Updated Parameter Definition Constants table with new prompt-related constants. Updated Table of Contents to include new Interactive Prompts section with all subsections.
- `doc/api-reference.md` - Added documentation for `param.set_prompt_handler()`, `param.set_max_prompt_retries()`, and `param.set_allowed_values()` functions. Updated Table of Contents (if present) to include new API functions.
- `README.md` - Updated Features list with interactive parameter prompts entry. Added 7 new example files to Examples list. Added "What's New in v1.1.0" section with 6 bullet points covering prompt functionality.

### Testing

- New unit tests in `tests/test_constants.py` covering all new prompt constants.
- New unit tests in `tests/test_input_prompt.py` covering `prompt_for_value()` function with various input types, validation, error conditions, and sensitive parameter handling.
- New unit tests in `tests/test_param_prompts.py` covering handler resolution, timing checks, repeat behaviour, CLI override detection, and orchestration logic.
- New integration tests in `tests/test_integration_prompts.py` covering:
  - `PROMPT_ON_START` timing execution
  - `PROMPT_ON_COMMAND` timing execution
  - All three repeat modes (`PROMPT_REPEAT_NEVER`, `PROMPT_REPEAT_IF_BLANK`, `PROMPT_REPEAT_ALWAYS`)
  - Sensitive parameter handling with echo suppression
  - Custom handler precedence (param-level, global, default)
  - Inline definition processing via `COMMAND_PROMPT_PARAMS`
  - Auto-population of `PROMPT_ON_COMMANDS` from `COMMAND_REQUIRED_PARAMS`
  - Validation retry logic with configurable maximum attempts
  - Max retry enforcement and error raising
- Regression tests verify existing parameter functionality unaffected by prompt feature additions.
- Tests use pytest with `monkeypatch` fixture and `StringIO` for stdin mocking (Python 3.7.9 compatible).
- All tests pass with overall test coverage remaining above 80% (target 90%+ for new code).
- Final test results: [To be updated after implementation - target: XXX passed, X skipped, XX.XX% coverage]

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...v1.1.0
Issues: https://github.com/minouris/spafw37/issues/15

[PENDING REVIEW - To be completed in Step 6]

### Testing

[PENDING REVIEW - To be completed in Step 6]

---

Full changelog: https://github.com/minouris/spafw37/compare/v[PREV]...v1.1.0  
Issues: https://github.com/minouris/spafw37/issues/15
