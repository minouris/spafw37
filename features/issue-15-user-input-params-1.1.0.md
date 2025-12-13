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
    - [Phase 3: Testing and Documentation](#phase-3-testing-and-documentation)
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

The solution provides an extensible design with a default handler using Python's built-in `input()` function, whilst allowing custom handlers for advanced use cases such as GUI prompts or API-based input. Prompts can be configured to appear at application start or before specific commands, with fine-grained control over repeat behaviour in cycles.

**Key architectural decisions (all resolved):**

- **Architecture approach:** Param-level properties (`PARAM_PROMPT`, `PARAM_PROMPT_HANDLER`, `PARAM_PROMPT_TIMING`, `PARAM_PROMPT_REPEAT`) extend existing param system rather than creating separate structure
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

[PENDING REVIEW - To be completed in Step 5]

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

**Answer:** See [Further Consideration 1: Design Pattern Research](#1-design-pattern-research---resolved) - Use Python's built-in `input()` function as the default handler, with extensibility support.

**Implementation:**
- Default prompt handler implemented in new file `input_prompt.py` using `input()` function
- Extensible via `PARAM_PROMPT_HANDLER` property (per-param override) or `set_prompt_handler()` method (global override)
- **Text:** Use `input()` with string return value
- **Boolean:** Accept yes/no, y/n, true/false with case-insensitive matching
- **Number:** Use `input()` with int() or float() conversion, retry on ValueError
- **Multiple choice:** Display numbered list, accept either number or text value
- **Error handling:** Retry on invalid input with clear error message

**Rationale:** Python's built-in `input()` function is simple, requires no dependencies, works on all platforms, and is what most Python CLI tools use. Extensible design allows custom handlers for advanced use cases (GUI prompts, API-based input, etc.).

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
```

**Test 1.1.2: Tests for param prompt constants definition**

```gherkin
Scenario: All PARAM_PROMPT* constants are defined in param constants module
  Given the param constants module is imported
  When checking for PARAM_PROMPT, PARAM_PROMPT_HANDLER, PARAM_PROMPT_TIMING, PARAM_PROMPT_REPEAT
  Then all constants are defined as string keys
  And each constant has a unique value
  
  # Tests: Constant definition completeness
  # Validates: All param-level prompt properties have corresponding constants
```

```python
# Test 1.1.2: Add to tests/test_constants.py
def test_param_prompt_constants_exist():
    """Test that all PARAM_PROMPT* constants required for prompt configuration are defined.
    
    This test verifies that PARAM_PROMPT, PARAM_PROMPT_HANDLER, PARAM_PROMPT_TIMING,
    and PARAM_PROMPT_REPEAT constants exist as strings with unique values.
    This behaviour is expected because these constants form the core vocabulary for
    configuring interactive prompts on parameters and must be available for param definitions."""
    # Block 1.1.2.1: Check all four prompt property constants exist
    assert hasattr(param, 'PARAM_PROMPT'), "PARAM_PROMPT constant missing"
    assert hasattr(param, 'PARAM_PROMPT_HANDLER'), "PARAM_PROMPT_HANDLER constant missing"
    assert hasattr(param, 'PARAM_PROMPT_TIMING'), "PARAM_PROMPT_TIMING constant missing"
    assert hasattr(param, 'PARAM_PROMPT_REPEAT'), "PARAM_PROMPT_REPEAT constant missing"
    
    # Block 1.1.2.2: Verify all are strings (required for dict keys)
    assert isinstance(param.PARAM_PROMPT, str), "PARAM_PROMPT must be string"
    assert isinstance(param.PARAM_PROMPT_HANDLER, str), "PARAM_PROMPT_HANDLER must be string"
    assert isinstance(param.PARAM_PROMPT_TIMING, str), "PARAM_PROMPT_TIMING must be string"
    assert isinstance(param.PARAM_PROMPT_REPEAT, str), "PARAM_PROMPT_REPEAT must be string"
    
    # Block 1.1.2.3: Verify all values are unique
    constant_values = [
        param.PARAM_PROMPT,
        param.PARAM_PROMPT_HANDLER,
        param.PARAM_PROMPT_TIMING,
        param.PARAM_PROMPT_REPEAT
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
    
    Args:
        param_def: Parameter definition dictionary.
        
    Returns:
        Formatted prompt string with [default: value] if default exists.
    """
    # Block 2.2.1.1: Get prompt text from param definition
    prompt_text = param_def.get(PARAM_PROMPT, 'Enter value')
    
    # Block 2.2.1.2: Add default value indicator if present
    default_value = param_def.get(PARAM_DEFAULT)
    if default_value is not None:
        prompt_text = "{0} [default: {1}]".format(prompt_text, default_value)
    
    # Block 2.2.1.3: Add trailing space for user input
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
    PARAM_ALLOWED_VALUES
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

**Code 2.3.1: Handle text input**

```python
# Block 2.3.1: Add to src/spafw37/input_prompt.py
def _handle_text_input(param_def, user_input):
    """Handle text input type (no conversion needed).
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        
    Returns:
        User input string or default value if blank.
    """
    # Block 2.3.1.1: Return user input if not blank
    if user_input.strip():
        return user_input.strip()
    
    # Block 2.3.1.2: Return default if blank input
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

**File:** `src/spafw37/param.py` (or new `src/spafw37/prompt.py`)

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


[↑ Back to top](#table-of-contents)

---

**Step 5.2: Implement prompt timing check helper**

**File:** `src/spafw37/param.py` (or new `src/spafw37/prompt.py`)

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

[↑ Back to top](#table-of-contents)

---

**Step 5.3: Implement prompt execution with validation helper**

**File:** `src/spafw37/param.py` (or new `src/spafw37/prompt.py`)

Implement the core prompt execution loop with validation and retry logic. This integrates prompts with the existing framework validation system, ensuring user input is validated immediately using the same rules as CLI arguments. The retry mechanism provides user-friendly error recovery whilst preventing infinite loops.

**Algorithm:**

1. Define maximum retry attempts (e.g., `max_retries = 3`)
2. Initialize retry counter to 0
3. Start retry loop (while retry counter < max_retries):
   a. Call the handler function with param definition: `user_value = handler(param_def)`
   b. Attempt validation:
      - Call existing framework validation function(s) for the param type
      - Check `PARAM_ALLOWED_VALUES` if present (multiple choice validation)
      - Apply any custom validation from param definition
   c. If validation succeeds:
      - Add param name to module-level `_prompted_params` set (track that prompt occurred)
      - Return the validated user value
   d. If validation fails:
      - Display clear error message to user indicating what was wrong
      - Increment retry counter
      - If retry counter < max_retries: continue loop (prompt again)
4. If loop exits (max retries exceeded):
   - Check if param is required (via `PARAM_REQUIRED` or presence in any command's `COMMAND_REQUIRED_PARAMS`):
     - If required: log error and exit application with non-zero status
     - If optional: log warning, return None (param remains unset)

**Error handling considerations:**
- Handler may raise `EOFError` (stdin closed, non-interactive environment): propagate immediately, don't retry
- Handler may raise `KeyboardInterrupt` (Ctrl+C): propagate immediately, allow user to abort
- Validation errors are expected and trigger retry; other exceptions propagate
- Set param value on success

[↑ Back to top](#table-of-contents)

---

**Step 5.4: Implement prompt text formatting helper**

**File:** `src/spafw37/param.py` (or new `src/spafw37/prompt.py`)

Implement prompt text formatting following bash/Unix conventions for default value display. This provides users with clear indication of what will happen if they press Enter without typing, following familiar patterns from standard command-line tools.

**Algorithm:**

1. Get base prompt text from param definition's `PARAM_PROMPT` property
2. Check if param has `PARAM_DEFAULT` property set:
   - If present and not None:
     - Append " [default: {value}]" to prompt text (bash convention format)
     - Use the actual default value in the message
   - If not present: leave prompt text unchanged
3. Append ": " (colon and space) to prompt text for cursor positioning
4. Return formatted string

**Example outputs:**
- Without default: "Enter username: "
- With default: "Enter username [default: admin]: "
- Toggle with default: "Confirm deletion? (y/n) [default: n]: "

This formatting is used by the default `input_prompt.py` handler. Custom handlers may format differently.

[↑ Back to top](#table-of-contents)

---

**Step 6.1: Integrate PROMPT_ON_START timing in CLI workflow**

**File:** `src/spafw37/cli.py` or appropriate orchestration module

Integrate start-timing prompts into the CLI execution flow. This adds a new phase between command-line parsing and command execution where params with `PROMPT_ON_START` timing are processed. The integration point is carefully chosen to respect CLI overrides (already parsed) whilst occurring before command validation (which needs prompt values).

**Algorithm:**

1. Locate the integration point in `run_cli()` function:
   - After `_parse_command_line()` has completed
   - Before command queue processing begins
   - Before required param validation occurs
2. Iterate through all params in `param._params` registry:
   - For each param:
     - Check if param has `PARAM_PROMPT` property; if not, skip
     - Check if param has `PARAM_PROMPT_TIMING == PROMPT_ON_START`; if not, skip
     - Call `_should_prompt_param(param_def, command_name=None)` to check if prompting needed
     - If returns False (CLI override or already set), skip to next param
     - If returns True:
       - Resolve handler via `_get_prompt_handler(param_def)`
       - Execute prompt with `_execute_prompt_with_validation(param_def, handler)`
       - Set param value to returned result (or None if optional and max retries exceeded)

**Integration considerations:**
- This phase runs once per application execution, not per command
- Multiple params may prompt in sequence (order determined by param registration order)
- CLI values from `--param value` arguments prevent prompts (already handled by `_should_prompt_param`)
- Errors in required params will cause application exit (handled by `_execute_prompt_with_validation`)

[↑ Back to top](#table-of-contents)

---

**Step 7.1: Integrate PROMPT_ON_COMMAND timing in command execution**

**File:** `src/spafw37/command.py` or appropriate command execution module

Integrate command-timing prompts into the command execution pipeline. This adds prompting immediately before individual commands execute, using the reciprocal `COMMAND_PROMPT_PARAMS` list for O(1) lookup of which params need prompting. The repeat behaviour controls whether prompts repeat in cycles or multi-command sequences.

**Algorithm:**

1. Locate the command execution loop (where individual commands are executed):
   - In `run_cli()` or command execution orchestration function
   - Immediately before each command's action function is called
   - After command dependencies are resolved
2. Before each command executes:
   a. Check if command has `COMMAND_PROMPT_PARAMS` property; if not or empty, skip prompting
   b. Get command name from command definition
   c. For each param name in `COMMAND_PROMPT_PARAMS` list:
      - Look up param definition from `param._params` registry
      - Call `_should_prompt_param(param_def, command_name=command_name)` to check if prompting needed
        - This checks CLI override, timing match, and repeat behaviour based on `PARAM_PROMPT_REPEAT`
      - If returns False, skip to next param
      - If returns True:
        - Resolve handler via `_get_prompt_handler(param_def)`
        - Execute prompt with `_execute_prompt_with_validation(param_def, handler)`
        - Set param value to returned result
        - Note: `_execute_prompt_with_validation` adds param to `_prompted_params` set for `PROMPT_REPEAT_NEVER` tracking

**Repeat behaviour handling (via `_should_prompt_param`):**
- `PROMPT_REPEAT_ALWAYS`: Always prompts, previous value shown as default by handler
- `PROMPT_REPEAT_IF_BLANK`: Only prompts if param value is None/empty (checked by `_should_prompt_param`)
- `PROMPT_REPEAT_NEVER`: Only prompts if param name not in `_prompted_params` set (checked by `_should_prompt_param`)

**Cycle integration:**
- This mechanism works naturally with cycles - if a command is in a cycle, prompting occurs before each cycle iteration
- The repeat behaviour controls whether users are re-prompted on subsequent iterations
- No special cycle-specific code needed; repeat behaviour handles all cases

[↑ Back to top](#table-of-contents)

---

**Steps 7.2-7.4: Repeat behaviour implementation**

**Note:** The repeat behaviour for `PROMPT_REPEAT_ALWAYS`, `PROMPT_REPEAT_IF_BLANK`, and `PROMPT_REPEAT_NEVER` is implemented within the `_should_prompt_param()` helper function (Step 5.2) and does not require separate implementation steps.

The algorithm in Step 5.2 handles all three modes:
- **PROMPT_REPEAT_ALWAYS:** `_should_prompt_param` always returns True for the command context, causing prompts every time
- **PROMPT_REPEAT_IF_BLANK:** `_should_prompt_param` checks current param value and returns True only if blank
- **PROMPT_REPEAT_NEVER:** `_should_prompt_param` checks `_prompted_params` set and returns False if param was already prompted

All repeat logic is centralised in the timing check helper, avoiding code duplication across command execution contexts.

[↑ Back to top](#table-of-contents)

---

**Step 7.5: Add end-to-end integration tests**

**File:** `tests/test_integration_prompts.py` (new file)

Create comprehensive integration tests covering complete workflows from CLI invocation through prompt execution to command completion. These tests validate the entire prompt system working together: timing modes, repeat behaviour, CLI overrides, validation retry logic, custom handlers, and auto-population mechanisms.

**Test coverage areas:**
- PROMPT_ON_START with CLI override preventing prompts
- PROMPT_ON_COMMAND with multiple commands in sequence
- All three repeat modes (ALWAYS, IF_BLANK, NEVER) in cycles
- Mixed prompt timings in same application
- Validation failures with retry logic and max retry handling
- Custom handlers (param-level and global)
- Auto-population from COMMAND_REQUIRED_PARAMS
- Inline param definitions in COMMAND_PROMPT_PARAMS
- Error handling (EOFError, KeyboardInterrupt, validation errors)

**Detailed implementation and tests will be added in Steps 3-4**

[↑ Back to top](#table-of-contents)

---

**Step 8.1: Add cycle-specific tests**

**File:** `tests/test_integration_prompts.py` (extend)

**Tests:** Comprehensive tests for prompt behaviour in cycle contexts with all repeat options.

This step validates that the prompt system works correctly within spafw37's cycle infrastructure. Cycles repeat commands multiple times, creating unique challenges for prompt timing and repeat behaviour. These tests ensure all three repeat modes (ALWAYS, IF_BLANK, NEVER) work correctly in cycles, nested cycles maintain proper state, and CLI overrides prevent prompting across all iterations. Cycles are the most complex context for prompts due to iteration state management.

**Test 8.8.1: test_cycle_repeat_always_prompts_every_iteration**

This test validates PROMPT_REPEAT_ALWAYS behaviour in cycles. Each cycle iteration should prompt before the command executes, allowing users to provide different values or confirm the action on every iteration. This is useful for per-item confirmation workflows. The test confirms REPEAT_ALWAYS prompts on every cycle iteration without state interference between iterations.

```gherkin
Scenario: PROMPT_REPEAT_ALWAYS prompts on every cycle iteration with previous value
  Given a param "filename" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["process"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_ALWAYS
  And a cycle that runs "process" command 3 times
  And stdin mocked with StringIO("file1.txt\nfile2.txt\nfile3.txt\n")
  When cycle executes
  Then iteration 1: prompt appears, input "file1.txt"
  And iteration 2: prompt appears with [default: file1.txt], input "file2.txt"
  And iteration 3: prompt appears with [default: file2.txt], input "file3.txt"
  And each iteration processes with different filename
  
  # Tests: REPEAT_ALWAYS in cycles
  # Validates: Per-iteration prompting with default value preservation
```

**Test 8.8.2: test_cycle_repeat_if_blank_first_iteration_only**

This test validates PROMPT_REPEAT_IF_BLANK behaviour in cycles. Only the first iteration should prompt (value starts blank), and all subsequent iterations should reuse the same value without prompting. This is efficient for batch processing where the same parameter applies to all items. The test confirms REPEAT_IF_BLANK prompts once and reuses the value across iterations.

```gherkin
Scenario: PROMPT_REPEAT_IF_BLANK prompts first iteration then reuses value
  Given a param "format" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["convert"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_IF_BLANK
  And a cycle that runs "convert" command 5 times
  And stdin mocked with StringIO("json\n")
  When cycle executes
  Then iteration 1: value blank, prompt appears, input "json" captured
  And iteration 2-5: value set to "json", prompt skipped
  And all five iterations use format="json"
  
  # Tests: REPEAT_IF_BLANK in cycles
  # Validates: Single prompt with value reuse across all iterations
```

**Test 8.8.3: test_cycle_repeat_never_prompts_before_cycle_starts**

This test validates PROMPT_REPEAT_NEVER behaviour in cycles. The prompt should appear once before the cycle starts, and all iterations should use the same value without re-prompting. This enables initialization-style prompts for cycle parameters. The test confirms REPEAT_NEVER prompts once and the tracking state persists correctly throughout the cycle.

```gherkin
Scenario: PROMPT_REPEAT_NEVER prompts once before cycle starts
  Given a param "mode" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["task"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_NEVER
  And a cycle that runs "task" command 4 times
  And stdin mocked with StringIO("batch\n")
  When cycle executes
  Then before cycle iteration 1: prompt appears, input "batch" captured
  And param "mode" added to _prompted_params set
  And iterations 1-4: all execute with mode="batch", no prompts
  
  # Tests: REPEAT_NEVER in cycles
  # Validates: One-time initialization for cycle parameters
```

**Test 8.8.4: test_nested_cycles_repeat_behaviour_independent**

This test validates that nested cycles maintain independent prompt state. Inner and outer cycles should each respect their own repeat behaviour without interfering with each other. This ensures complex nested workflows work correctly. The test confirms nested cycles maintain separate prompt tracking and repeat behaviour operates correctly at each level.

```gherkin
Scenario: Nested cycles maintain independent prompt state and repeat behaviour
  Given outer param "batch" with PROMPT_REPEAT_NEVER for outer cycle command
  And inner param "item" with PROMPT_REPEAT_ALWAYS for inner cycle command
  And outer cycle runs 2 times, inner cycle runs 3 times per outer iteration
  And stdin mocked with StringIO("batch1\nitem1\nitem2\nitem3\nitem4\nitem5\nitem6\n")
  When nested cycles execute
  Then outer iteration 1 prompts once for "batch": "batch1"
  And inner iterations 1-3 each prompt for "item": "item1", "item2", "item3"
  And outer iteration 2 does not prompt (REPEAT_NEVER)
  And inner iterations 4-6 each prompt for "item": "item4", "item5", "item6"
  And prompt state tracked independently for each cycle level
  
  # Tests: Nested cycles with different repeat behaviours
  # Validates: Independent prompt state at each nesting level
```

**Test 8.8.5: test_cycle_with_cli_override_no_prompting**

This test validates that CLI overrides prevent prompting across all cycle iterations. When a param value is set via command-line arguments, no prompts should appear during the cycle regardless of repeat behaviour configuration. This maintains consistent CLI override semantics. The test confirms CLI values work correctly in cycle contexts without any prompting.

```gherkin
Scenario: CLI override prevents prompting across all cycle iterations
  Given a param "limit" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["check"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_ALWAYS (would normally prompt every time)
  And a cycle that runs "check" command 4 times
  And stdin mocked with StringIO("") (empty, should not be read)
  When application runs with command line "--limit 100 [cycle command]"
  Then CLI parsing sets limit="100"
  And all 4 cycle iterations execute with limit="100"
  And no prompts occur (CLI override in effect)
  And stdin never read
  
  # Tests: CLI override in cycles
  # Validates: Command-line arguments prevent all cycle prompts
```

[↑ Back to top](#table-of-contents)

---

**Step 8.2: Add extensibility tests**

**File:** `tests/test_param_prompts.py` (extend)

**Tests:** Test custom handler functionality and extensibility system.

This step validates the extensibility architecture that allows applications to replace the default `input()` handler with custom logic. Custom handlers enable advanced scenarios like GUI prompts, API-based input, or specialized input validation. These tests ensure the three-tier precedence system (param-level → global → default) works correctly, handlers receive proper context, return values are processed correctly, and error handling is robust.

**Test 8.8.6: test_global_custom_handler_replaces_default**

This test validates that a global custom handler replaces the default `input()` handler for all prompts without param-specific handlers. Applications can call `set_prompt_handler(custom_function)` once to change prompt behaviour globally. The test confirms global handler registration works correctly and the custom handler is invoked instead of the default for all applicable prompts.

```gherkin
Scenario: Global custom handler used for all prompts without param-specific handlers
  Given a custom handler function gui_prompt(param_def)
  When set_prompt_handler(gui_prompt) is called
  And a param "name" with PARAM_PROMPT (no PARAM_PROMPT_HANDLER)
  And prompt execution occurs for "name"
  Then gui_prompt function is called with param definition
  And default input_prompt.prompt_for_value NOT called
  And return value from gui_prompt set as param value
  
  # Tests: Global handler registration and invocation
  # Validates: Applications can replace default handler globally
```

**Test 8.8.7: test_param_level_handler_overrides_global_and_default**

This test validates that param-specific handlers have highest precedence, overriding both global and default handlers. Individual params can specify `PARAM_PROMPT_HANDLER` for specialized input handling whilst other params use the global or default handler. The test confirms param-level handlers are invoked correctly and take precedence over all other handlers.

```gherkin
Scenario: Param-specific handler takes precedence over global and default
  Given a global handler set to global_custom_handler
  And param "password" with PARAM_PROMPT_HANDLER set to secure_input_handler
  And param "username" with PARAM_PROMPT (no handler, uses global)
  When prompts execute for both params
  Then "password" uses secure_input_handler (param-level)
  And "username" uses global_custom_handler (global fallback)
  And default input_prompt.prompt_for_value NOT used for either
  
  # Tests: Param-level handler precedence
  # Validates: Individual params can override global handler configuration
```

**Test 8.8.8: test_handler_precedence_chain_all_levels**

This test validates the complete three-tier precedence chain (param-level → global → default) in a single scenario. Different params should use different handlers based on what's configured. The test confirms the precedence resolution logic works correctly across all three levels simultaneously.

```gherkin
Scenario: Handler precedence chain resolves correctly across three levels
  Given set_prompt_handler(global_handler) called
  And param "special" with PARAM_PROMPT_HANDLER=special_handler (level 1)
  And param "normal" with PARAM_PROMPT only (level 2 - uses global)
  And param "default_test" with PARAM_PROMPT only
  When global handler is then cleared (set to None)
  Then "special" uses special_handler (param-level precedence)
  And "normal" uses global_handler (global precedence)
  And "default_test" uses input_prompt.prompt_for_value (default fallback)
  And precedence: param > global > default confirmed
  
  # Tests: Complete precedence chain
  # Validates: Three-tier handler resolution works correctly
```

**Test 8.8.9: test_custom_handler_receives_param_definition**

This test validates that custom handlers receive the complete param definition as context. Handlers need access to param properties like PARAM_TYPE, PARAM_DEFAULT, PARAM_ALLOWED_VALUES to provide appropriate prompts. The test confirms handlers receive the full param definition object with all properties intact.

```gherkin
Scenario: Custom handler receives complete param definition with all properties
  Given a custom handler that inspects its param_def argument
  And param "choice" with multiple properties:
    - PARAM_PROMPT="Select option:"
    - PARAM_TYPE=PARAM_TYPE_TEXT
    - PARAM_ALLOWED_VALUES=["a", "b", "c"]
    - PARAM_DEFAULT="a"
  When custom handler is invoked for "choice"
  Then param_def argument contains all properties
  And handler can access PARAM_PROMPT, PARAM_TYPE, etc.
  And handler uses properties to customize prompt behaviour
  
  # Tests: Handler receives param context
  # Validates: Custom handlers have access to all param configuration
```

**Test 8.8.10: test_custom_handler_return_value_sets_param**

This test validates that the return value from a custom handler is used as the param value. Handlers can perform custom input collection and return the result, which the framework should validate and set as the param value. The test confirms the handler return value flows correctly through validation and into param storage.

```gherkin
Scenario: Return value from custom handler validated and set as param value
  Given a custom handler that returns "custom_result"
  And param "data" with PARAM_PROMPT_HANDLER=custom_handler
  And param has validation rules
  When prompt execution occurs
  Then custom_handler called and returns "custom_result"
  And "custom_result" passed through framework validation
  And if validation passes, param "data" set to "custom_result"
  And command receives value from custom handler
  
  # Tests: Handler return value processing
  # Validates: Custom handler results validated and stored correctly
```

**Test 8.8.11: test_custom_handler_exceptions_handled_gracefully**

This test validates exception handling for custom handlers. If a custom handler raises an exception, the framework should catch it, log an appropriate error, and either retry or fail gracefully based on param requirements. Poor handler implementations shouldn't crash the entire application. The test confirms exception handling provides robust behaviour even with faulty handlers.

```gherkin
Scenario: Exceptions in custom handlers caught and handled gracefully
  Given a custom handler that raises ValueError("Handler error")
  And param "test" with PARAM_PROMPT_HANDLER=faulty_handler
  When prompt execution occurs
  Then ValueError raised by handler is caught
  And error logged with clear message "Custom handler error: Handler error"
  And if param PARAM_REQUIRED=True, application exits with clear error
  And if param optional, param set to None and execution continues
  
  # Tests: Custom handler exception handling
  # Validates: Faulty handlers don't crash application unexpectedly
```

[↑ Back to top](#table-of-contents)

---

#### Phase 3: Documentation and Final Testing

**Step 9: Regression testing**

**Files:** Existing test suite

Run full test suite to ensure no regressions:
- All existing param tests pass
- All existing command tests pass
- All existing cycle tests pass
- All existing CLI parsing tests pass
- Params without `PARAM_PROMPT` behave exactly as before
- Commands without prompt params behave exactly as before

[Detailed test specifications will be added in Step 3]

[↑ Back to top](#table-of-contents)

---

**Step 10: Update documentation**

**Files:** `doc/parameters.md`, `README.md`, `examples/params_prompts.py`

Add comprehensive documentation:
- **New param properties:** Usage guide for all `PARAM_PROMPT*` properties
- **Timing options:** Examples of `PROMPT_ON_START` vs `PROMPT_ON_COMMAND` with `PROMPT_ON_COMMANDS` property
- **Repeat behaviour:** Examples of each `PROMPT_REPEAT_*` option in cycles
- **Custom handlers:** Guide for implementing and registering custom prompt handlers
- **Multiple choice:** Dynamic population with `set_allowed_values()` examples
- **CLI override:** Explain how CLI args prevent prompting
- **Auto-population:** Document `PROMPT_ON_COMMANDS` property auto-population from `COMMAND_REQUIRED_PARAMS`
- **Inline definitions:** Document `COMMAND_PROMPT_PARAMS` inline definition support (see `examples/inline_definitions_basic.py` and `examples/inline_definitions_advanced.py` for pattern)
- **Complete examples:** Working examples demonstrating common use cases

**Note:** The `COMMAND_PROMPT_PARAMS` field supports inline parameter definitions, consistent with `COMMAND_REQUIRED_PARAMS`, `COMMAND_TRIGGER_PARAM`, and dependency fields. This allows commands to define prompt-enabled params directly within their definition without separate `add_param()` calls, enabling rapid prototyping whilst maintaining API consistency.

[Detailed documentation plan will be added in Step 5]

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

[PENDING REVIEW - To be completed if plan changes during implementation]

## Documentation Updates

[PENDING REVIEW - To be completed in Step 5]

## CHANGES for v1.1.0 Release

**Note:** This section must follow the format specified in `features/CHANGES-TEMPLATE.md`. The content will be posted as the closing comment and consumed by the release workflow.

[PENDING REVIEW - To be completed in Step 6]

### Issues Closed

- #15: User Input Params

### Additions

[PENDING REVIEW - To be completed in Step 6]

### Removals

[PENDING REVIEW - To be completed in Step 6]

### Changes

[PENDING REVIEW - To be completed in Step 6]

### Migration

[PENDING REVIEW - To be completed in Step 6]

### Documentation

[PENDING REVIEW - To be completed in Step 6]

### Testing

[PENDING REVIEW - To be completed in Step 6]

---

Full changelog: https://github.com/minouris/spafw37/compare/v[PREV]...v1.1.0  
Issues: https://github.com/minouris/spafw37/issues/15
