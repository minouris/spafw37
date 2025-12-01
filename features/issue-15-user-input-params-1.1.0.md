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
- **Timing control:** Param properties control when prompts appear (`PROMPT_ON_START` or `PROMPT_ON_COMMANDS`) with auto-population from `COMMAND_REQUIRED_PARAMS`
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

**With PROMPT_ON_COMMANDS timing:**
1. Application starts → `run_cli()` called in `core.py`
2. CLI parsing → `_parse_command_line()` in `cli.py`
3. Param validation → Framework validates required params exist
4. Command execution begins
5. **NEW:** Before each command execution:
   - Check if command name in param's `PROMPT_ON_COMMANDS` list
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

**Answer:** Use param-level properties for timing control.

**Design:**

`PARAM_PROMPT_TIMING` - Controls when the prompt appears:
- `PROMPT_ON_START`: Prompts immediately after CLI parsing (before command execution)
- `PROMPT_ON_COMMANDS`: List of command names. Auto-populates with commands that have this param in `COMMAND_REQUIRED_PARAMS`. Will prompt before any command on this list.

`PARAM_PROMPT_REPEAT` - Controls repeat behaviour (works with `PROMPT_ON_COMMANDS`):
- `PROMPT_REPEAT_ALWAYS`: Repeats before every command in `PROMPT_ON_COMMANDS`. Preserves previous value.
- `PROMPT_REPEAT_IF_BLANK`: Repeats before commands in `PROMPT_ON_COMMANDS` if the value is blank
- `PROMPT_REPEAT_NEVER`: Never repeat after the first prompt

**Reciprocal list auto-population:**
- When a param is added with `PROMPT_ON_COMMANDS`, those command names are stored on the param
- When a command is added with `COMMAND_REQUIRED_PARAMS`, framework auto-populates `PROMPT_ON_COMMANDS` for matching params (if they have `PARAM_PROMPT` and `PROMPT_ON_COMMANDS` is not explicitly set)
- Commands will have a reciprocal list of params that prompt before them, built at registration time
- This allows efficient lookup: "which params need prompting before this command executes?"

**Rationale:** Param-level approach provides fine-grained control whilst integrating with existing `COMMAND_REQUIRED_PARAMS` structure. Auto-population from `COMMAND_REQUIRED_PARAMS` reduces configuration burden. Reciprocal lists enable efficient command-side lookup without scanning all params.

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

Combined with `PROMPT_ON_COMMANDS` listing the cycle command name, this provides full control over cycle prompt behaviour.

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

**Step 1a: Add prompt constants**

**Files:** `src/spafw37/constants/param.py`, `src/spafw37/constants/command.py`

Add new constants for prompt configuration:

**In `param.py`:**
- `PARAM_PROMPT` - prompt text
- `PARAM_PROMPT_HANDLER` - custom handler function
- `PARAM_PROMPT_TIMING` - timing constant
- `PARAM_PROMPT_REPEAT` - repeat behaviour constant
- `PROMPT_ON_START` - timing: prompt after CLI parsing
- `PROMPT_ON_COMMANDS` - timing: list of command names
- `PROMPT_REPEAT_ALWAYS` - repeat every time
- `PROMPT_REPEAT_IF_BLANK` - repeat if blank
- `PROMPT_REPEAT_NEVER` - never repeat after first

**In `command.py`:**
- `COMMAND_PROMPT_PARAMS` - internal list of params that prompt before this command

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 1b: Test constants**

**File:** `tests/test_constants.py` (extend existing)

**Tests:** Verify all new prompt-related constants are defined with correct types and values.

This step validates the foundation of the prompt system by ensuring all required constants exist with proper values. Constants are critical because they're used throughout the codebase for property lookups and comparisons. These tests catch typos, missing definitions, and value collisions that would cause runtime errors.

**Test 1.1.1: test_param_prompt_constants_exist**

This test verifies that all four param-level prompt property constants are defined and accessible. These constants (`PARAM_PROMPT`, `PARAM_PROMPT_HANDLER`, `PARAM_PROMPT_TIMING`, `PARAM_PROMPT_REPEAT`) form the core vocabulary for configuring interactive prompts on parameters. The test ensures each constant is a string (required for dictionary keys in param definitions) and that all values are unique to prevent ambiguous property lookups.

```gherkin
Scenario: All PARAM_PROMPT* constants are defined in param constants module
  Given the param constants module is imported
  When checking for PARAM_PROMPT, PARAM_PROMPT_HANDLER, PARAM_PROMPT_TIMING, PARAM_PROMPT_REPEAT
  Then all constants are defined as string keys
  And each constant has a unique value
  
  # Tests: Constant definition completeness
  # Validates: All param-level prompt properties have corresponding constants
```

**Test 1.1.2: test_prompt_timing_constants_exist**

This test validates the timing control constants that determine when prompts appear during application execution. `PROMPT_ON_START` indicates prompts should run immediately after CLI parsing (before any commands execute), whilst `PROMPT_ON_COMMANDS` signals that prompts are tied to specific command executions. The test ensures both constants exist, are strings (for consistent comparison logic), and have distinct values to enable unambiguous timing checks throughout the codebase.

```gherkin
Scenario: All PROMPT_* timing constants are defined with correct values
  Given the param constants module is imported
  When checking for PROMPT_ON_START and PROMPT_ON_COMMANDS
  Then both constants are defined
  And PROMPT_ON_START is a string constant
  And PROMPT_ON_COMMANDS is a string constant
  And values are distinct from each other
  
  # Tests: Timing constant definition
  # Validates: Timing options have proper constant values for comparison logic
```

**Test 1.1.3: test_prompt_repeat_constants_exist**

This test verifies the three repeat behaviour constants that control how prompts behave in cycles and repeated command executions. `PROMPT_REPEAT_ALWAYS` forces prompts on every iteration (useful for confirmation workflows), `PROMPT_REPEAT_IF_BLANK` only re-prompts when the value is empty (efficient for optional updates), and `PROMPT_REPEAT_NEVER` ensures single-prompt behaviour (standard for initialization values). The test confirms all three exist, are strings, and have unique values to prevent logic errors in cycle handling.

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

**Test 1.1.4: test_command_prompt_params_constant_exists**

This test validates the reciprocal list constant on the command side. `COMMAND_PROMPT_PARAMS` stores the list of parameter names that should prompt before a command executes, enabling O(1) lookup during command execution without scanning all parameters. The test ensures the constant is defined in the command module as a string key with a unique value, establishing the infrastructure for efficient prompt-command coordination.

```gherkin
Scenario: COMMAND_PROMPT_PARAMS constant defined in command constants module
  Given the command constants module is imported
  When checking for COMMAND_PROMPT_PARAMS
  Then the constant is defined as a string key
  And the value is unique within command constants
  
  # Tests: Command reciprocal list constant
  # Validates: Commands can store list of params that prompt before them
```

[↑ Back to top](#table-of-contents)

---

**Step 2a: Create default input handler module**

**File:** `src/spafw37/input_prompt.py`

Implement default prompt handler using Python's `input()` function:
- `prompt_for_value(param_def)` - main handler function
- Handle text input (return string)
- Handle number input (convert with int/float)
- Handle toggle input (accept y/n, yes/no, true/false)
- Handle multiple choice (display numbered list, accept number or text)
- Display default value in prompt (bash convention: `[default: value]`)
- Return user input or default if blank entered

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 2b: Test default input handler**

**File:** `tests/test_input_prompt.py`

**Tests:** Unit tests for default handler in isolation using `monkeypatch` and `StringIO` for stdin mocking.

This step validates the default input handler (`input_prompt.py`) in complete isolation before integration with the parameter system. By mocking stdin with `StringIO`, tests can simulate user input without actual keyboard interaction, enabling automated testing of all input types, validation, error handling, and edge cases. These tests ensure the handler correctly processes text, numbers, toggles, and multiple choice inputs whilst properly displaying defaults and handling EOF conditions.

**Test 2.2.1: test_prompt_text_input_returns_string**

This test validates the most basic functionality: capturing plain text input from the user. Text parameters are the simplest type—no conversion, no validation beyond framework rules. The test mocks stdin with a sample string and verifies the handler returns exactly what the user typed. This establishes the foundation for all other input types and confirms the `input()` function integration works correctly.

```gherkin
Scenario: Text input handler returns user-entered string
  Given a param with PARAM_TYPE_TEXT and no default value
  And stdin is mocked with StringIO("test value\n")
  When prompt_for_value() is called
  Then the function returns "test value"
  And the param value is set to "test value"
  
  # Tests: Basic text input handling with input() function
  # Validates: String input is captured and returned correctly
```

**Test 2.2.2: test_prompt_text_with_default_blank_input**

This test validates the default value mechanism using the bash convention of displaying `[default: value]` in the prompt. When a user presses Enter without typing anything (blank input), the system should use the default value automatically. This behaviour mirrors standard Unix/Linux command-line tools and provides a familiar user experience. The test confirms both the display format and the default selection logic work correctly.

```gherkin
Scenario: Blank input with default value returns the default
  Given a param with PARAM_TYPE_TEXT and PARAM_DEFAULT "default_value"
  And stdin is mocked with StringIO("\n")
  When prompt_for_value() is called
  Then the function returns "default_value"
  And the prompt text displayed "[default: default_value]"
  
  # Tests: Default value handling for text input
  # Validates: Blank input selects default using bash convention
```

**Test 2.2.3: test_prompt_number_integer_valid**

This test validates integer conversion for numeric parameters. When a user types "42", the handler must convert the string to an actual integer (42) for proper numeric operations downstream. The test confirms the handler correctly identifies integer input (no decimal point) and performs `int()` conversion without errors. This is essential for parameters used in mathematical operations, counters, or array indices.

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

**Test 2.2.4: test_prompt_number_float_valid**

This test validates floating-point conversion for numeric parameters requiring decimal precision. When a user types "3.14", the handler must convert it to a float (3.14) rather than an integer. The test confirms the handler correctly identifies float input (contains decimal point) and performs `float()` conversion. This ensures parameters can represent precise measurements, percentages, or scientific values.

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

**Test 2.2.5: test_prompt_toggle_yes_variations**

This test validates that toggle (boolean) parameters accept multiple affirmative formats with case-insensitive matching. Users might type "y", "Y", "yes", "YES", "true", or "True" to indicate affirmative—all should be recognized as True. This provides a flexible, user-friendly interface rather than forcing exact input. The test confirms all common affirmative variations work correctly and return the Python boolean `True`.

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

**Test 2.2.6: test_prompt_toggle_no_variations**

This test validates that toggle parameters accept multiple negative formats with case-insensitive matching. Users might type "n", "N", "no", "NO", "false", or "False" to indicate negative—all should be recognized as False. Complementing the affirmative test, this ensures comprehensive toggle support. The test confirms all common negative variations work correctly and return the Python boolean `False`.

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

**Test 2.2.7: test_prompt_multiple_choice_by_number**

This test validates selection from a list of choices using numeric indices. When `PARAM_ALLOWED_VALUES` contains multiple options, the handler should display them as a numbered list (1, 2, 3...) and allow users to select by typing the number. This provides an efficient selection interface—users can type "2" instead of "option2". The test confirms the numbered display format and the index-to-value mapping work correctly.

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

**Test 2.2.8: test_prompt_multiple_choice_by_text**

This test validates selection from a list of choices by typing the exact text value. Some users prefer typing the full option name rather than remembering its number in the list. The handler should accept either approach—numeric index or exact text match. The test confirms that typing "green" when ["red", "green", "blue"] is displayed returns "green" correctly.

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

**Test 2.2.9: test_prompt_eof_raises_error**

This test validates proper handling of EOF (End Of File) conditions, which occur when stdin closes unexpectedly or reaches its end without providing input. This happens in automated scripts with empty stdin, when users press Ctrl+D (Unix) or Ctrl+Z (Windows), or when piped input ends. The handler must detect this condition and raise `EOFError` rather than failing silently or entering an infinite loop. Proper EOF handling ensures the application fails predictably in non-interactive environments.

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

**Test 2.2.10: test_prompt_default_displayed_in_text**

This test validates the user-facing display format for default values. When a parameter has a default, the prompt should clearly show what value will be used if the user presses Enter without typing. The bash convention `[default: value]` is widely recognized and unambiguous. The test confirms the prompt text formatting includes this indicator correctly, ensuring users always know what will happen when they select the default.

```gherkin
Scenario: Default value shown in prompt text using bash convention
  Given a param with PARAM_DEFAULT "example_default"
  When prompt text is formatted
  Then prompt includes "[default: example_default]"
  And format follows bash convention style
  
  # Tests: Default value display formatting
  # Validates: Users see what default will be used if they press enter
```

[↑ Back to top](#table-of-contents)

---

**Step 3a: Add param registration logic**

**File:** `src/spafw37/param.py`

**Add internal state:**
- `_global_prompt_handler = None` - global handler storage
- `_prompted_params = set()` - track which params have been prompted (for PROMPT_REPEAT_NEVER)

**Extend `add_param()` function:**
- Store `PROMPT_ON_COMMANDS` list on param definition (if present)
- If `PARAM_PROMPT` exists but `PROMPT_ON_COMMANDS` not explicitly set, mark param with special flag for auto-population
- Validate prompt properties (e.g., timing must be valid constant)

**Add public API:**
- `set_prompt_handler(handler)` - set global prompt handler (delegated through `core.py`)
- `set_allowed_values(param_name, values)` - update `PARAM_ALLOWED_VALUES` at runtime

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 3b: Test param registration**

**File:** `tests/test_param_prompts.py`

**Tests:** Test param registration with prompt properties and public API functions.

This step validates that the parameter registration system correctly stores and preserves all prompt-related properties. Registration is the first point of integration between user-defined parameters and the framework's internal structures. These tests ensure prompt properties survive the registration process intact, timing/repeat constants are stored correctly, auto-population flags work, and the public API functions (`set_prompt_handler()`, `set_allowed_values()`) operate as designed.

**Test 3.3.1: test_param_with_prompt_property_registered**

This test validates the most fundamental integration point: registering a parameter with the new `PARAM_PROMPT` property. The registration system must accept this new property without errors and store it correctly in the internal `_params` dictionary. This test confirms that prompt-enabled parameters are treated as first-class citizens in the framework, establishing the foundation for all subsequent prompt functionality.

```gherkin
Scenario: Param with PARAM_PROMPT property registers successfully  
  Given a param definition with PARAM_PROMPT "Enter value:"
  When add_param() is called
  Then param is stored in _params dictionary
  And PARAM_PROMPT property is preserved on param definition
  And param can be retrieved by name
  
  # Tests: Basic registration with prompt property
  # Validates: Params with PARAM_PROMPT are accepted and stored correctly
```

**Test 3.3.2: test_prompt_on_start_timing_stored**

This test validates storage of the `PROMPT_ON_START` timing constant. When a parameter specifies this timing, the framework must preserve the exact constant value (not convert it to a string, boolean, or other type). This is critical because timing checks throughout the codebase use identity comparison (`timing == PROMPT_ON_START`). The test confirms the constant survives registration without mutation, ensuring timing logic will work correctly at runtime.

```gherkin
Scenario: PROMPT_ON_START timing value stored correctly
  Given a param with PARAM_PROMPT_TIMING set to PROMPT_ON_START constant
  When add_param() is called
  Then param stored with PARAM_PROMPT_TIMING property
  And property value equals PROMPT_ON_START constant
  
  # Tests: PROMPT_ON_START timing storage
  # Validates: Timing constant preserved for runtime checking
```

**Test 3.3.3: test_prompt_on_commands_list_stored**

This test validates storage of command name lists when using `PROMPT_ON_COMMANDS` timing. Unlike `PROMPT_ON_START` (a constant), `PROMPT_ON_COMMANDS` can be a list of specific command names like `["cmd1", "cmd2"]`. The registration system must store this list correctly without converting it to a string or losing elements. The test confirms list storage works correctly, enabling command-specific prompt timing at runtime.

```gherkin
Scenario: PROMPT_ON_COMMANDS list stored correctly
  Given a param with PARAM_PROMPT_TIMING set to list ["cmd1", "cmd2"]
  When add_param() is called
  Then param stored with PARAM_PROMPT_TIMING property
  And property value is ["cmd1", "cmd2"]
  And list is stored not copied (references same object)
  
  # Tests: PROMPT_ON_COMMANDS list storage
  # Validates: Command name list preserved for lookup during command execution
```

**Test 3.3.4: test_prompt_repeat_always_constant_stored**

This test validates storage of the `PROMPT_REPEAT_ALWAYS` constant, which controls prompt behaviour in cycles. Like timing constants, repeat constants must be preserved exactly as provided—no type conversion or mutation. This constant tells the framework to prompt on every cycle iteration, and the test confirms this directive is stored correctly for cycle logic to reference at runtime.

```gherkin
Scenario: PROMPT_REPEAT_ALWAYS constant stored correctly
  Given a param with PARAM_PROMPT_REPEAT set to PROMPT_REPEAT_ALWAYS
  When add_param() is called
  Then param stored with PARAM_PROMPT_REPEAT property
  And property value equals PROMPT_REPEAT_ALWAYS constant
  
  # Tests: PROMPT_REPEAT_ALWAYS storage
  # Validates: Repeat behaviour constant preserved for cycle logic
```

**Test 3.3.5: test_auto_population_flag_set**

This test validates the auto-population mechanism that reduces configuration burden. When a parameter has `PARAM_PROMPT` but doesn't explicitly specify `PARAM_PROMPT_TIMING`, the framework should mark it for auto-population from `COMMAND_REQUIRED_PARAMS`. This allows commands to automatically trigger prompts for their required params without duplicate configuration. The test confirms the auto-population flag is set correctly during registration, enabling the reciprocal registration logic to work in Step 4.

```gherkin
Scenario: Param without explicit PROMPT_ON_COMMANDS marked for auto-population
  Given a param with PARAM_PROMPT but no PARAM_PROMPT_TIMING
  When add_param() is called
  Then param is marked with auto-population flag
  And flag indicates PROMPT_ON_COMMANDS should be populated from commands
  
  # Tests: Auto-population flag mechanism
  # Validates: Framework can identify params needing command list population
```

**Test 3.3.6: test_set_prompt_handler_global**

This test validates the global prompt handler registration API. `set_prompt_handler()` allows applications to replace the default `input()` handler with custom logic (e.g., GUI prompts, API-based input). The test confirms the function stores the custom handler reference in `_global_prompt_handler` correctly, making it available for all subsequent prompts that don't have param-specific handlers. This establishes the foundation of the extensibility system.

```gherkin
Scenario: Global prompt handler set via set_prompt_handler()
  Given a custom handler function custom_handler()
  When set_prompt_handler(custom_handler) is called
  Then _global_prompt_handler stores custom_handler reference
  And subsequent prompts will use custom_handler by default
  
  # Tests: Global handler registration
  # Validates: Custom handlers can replace default input() behaviour globally
```

**Test 3.3.7: test_set_allowed_values_updates_param**

This test validates the dynamic allowed values API that enables runtime population of multiple choice lists. Commands can call `set_allowed_values("param_name", ["a", "b", "c"])` to populate choices after parameter registration, enabling data-driven menus without hardcoding options. The test confirms this function correctly updates the `PARAM_ALLOWED_VALUES` property on an existing parameter, enabling multiple choice prompting without requiring re-registration.

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

**Test 3.3.8: test_invalid_prompt_timing_raises_error**

This test validates input validation during parameter registration. If a parameter specifies an invalid `PARAM_PROMPT_TIMING` value (not `PROMPT_ON_START`, not `PROMPT_ON_COMMANDS`, not a list), the framework must reject it immediately with a clear error message. This prevents subtle bugs from invalid configuration propagating through the system. The test confirms the validation logic catches invalid timing values and raises `ValueError` during registration, failing fast rather than at runtime.

```gherkin
Scenario: Invalid prompt timing value raises validation error
  Given a param with PARAM_PROMPT_TIMING "invalid_value"
  When add_param() is called
  Then ValueError is raised
  And error message indicates invalid timing constant
  
  # Tests: Prompt timing validation
  # Validates: Only valid PROMPT_* constants accepted for timing
```

[↑ Back to top](#table-of-contents)

---

**Step 4a: Add command reciprocal registration**

**File:** `src/spafw37/command.py`

**Extend `add_command()` function:**
- Initialize `COMMAND_PROMPT_PARAMS` as empty list on command definition
- For each param name in `COMMAND_REQUIRED_PARAMS`:
  - Look up param definition from `param._params`
  - If param has `PARAM_PROMPT` and auto-population flag set:
    - Add this command name to param's `PROMPT_ON_COMMANDS` list
  - If param has `PARAM_PROMPT` and this command in its `PROMPT_ON_COMMANDS`:
    - Add param name to command's `COMMAND_PROMPT_PARAMS` list
- Store `COMMAND_PROMPT_PARAMS` for O(1) runtime lookup

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 4b: Test reciprocal registration**

**File:** `tests/test_param_prompts.py` (extend)

**Tests:** Test reciprocal list building between params and commands at registration time.

This step validates the reciprocal registration mechanism that builds bidirectional relationships between parameters and commands. When params specify `PROMPT_ON_COMMANDS` or when commands list params in `COMMAND_REQUIRED_PARAMS`, the framework automatically creates reciprocal references enabling efficient O(1) lookup at runtime. These tests ensure auto-population works correctly, reciprocal lists are built accurately regardless of registration order, and the mechanism handles edge cases like multiple params/commands and missing prompt properties.

**Test 4.4.1: test_auto_population_from_command_required_params**

This test validates the auto-population mechanism that reduces configuration burden. When a param has `PARAM_PROMPT` but no explicit `PARAM_PROMPT_TIMING`, and a command lists that param in `COMMAND_REQUIRED_PARAMS`, the framework should automatically add the command name to the param's `PROMPT_ON_COMMANDS` list. This allows commands to trigger prompts for their required params without duplicate configuration. The test confirms auto-population works correctly during command registration.

```gherkin
Scenario: Param marked for auto-population gets command name added to PROMPT_ON_COMMANDS
  Given a param "input_val" with PARAM_PROMPT but no PARAM_PROMPT_TIMING
  And param is marked with auto-population flag during registration
  When a command "process" is registered with COMMAND_REQUIRED_PARAMS ["input_val"]
  Then param "input_val" has PROMPT_ON_COMMANDS updated to ["process"]
  And auto-population flag is cleared after update
  
  # Tests: Auto-population mechanism during command registration
  # Validates: Commands automatically trigger prompts for required params without explicit configuration
```

**Test 4.4.2: test_reciprocal_list_built_on_command**

This test validates that commands build their `COMMAND_PROMPT_PARAMS` list when registering. When a command's required params have `PARAM_PROMPT` with this command in their `PROMPT_ON_COMMANDS`, the framework should add those param names to the command's `COMMAND_PROMPT_PARAMS` list. This reciprocal list enables O(1) lookup during command execution—"which params need prompting before I run?"—without scanning all parameters. The test confirms the reciprocal list building works correctly.

```gherkin
Scenario: Command builds COMMAND_PROMPT_PARAMS from params that prompt before it
  Given a param "user_input" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["execute"]
  When command "execute" is registered with COMMAND_REQUIRED_PARAMS ["user_input"]
  Then command "execute" has COMMAND_PROMPT_PARAMS ["user_input"]
  And reciprocal relationship established between param and command
  
  # Tests: Reciprocal list building on command side
  # Validates: Commands know which params will prompt before execution (O(1) lookup)
```

**Test 4.4.3: test_multiple_params_all_added_to_command**

This test validates that commands correctly handle multiple prompt-enabled required params. When a command requires several params that all have `PARAM_PROMPT`, the command's `COMMAND_PROMPT_PARAMS` list should contain all of them. This ensures complex commands with multiple interactive inputs work correctly. The test confirms the reciprocal list building scales to multiple parameters without dropping any.

```gherkin
Scenario: Command with multiple required params builds complete COMMAND_PROMPT_PARAMS list
  Given params "name", "age", "email" all with PARAM_PROMPT and auto-population flags
  When command "register" registered with COMMAND_REQUIRED_PARAMS ["name", "age", "email"]
  Then command "register" has COMMAND_PROMPT_PARAMS ["name", "age", "email"]
  And all three params have PROMPT_ON_COMMANDS ["register"]
  And all reciprocal relationships established correctly
  
  # Tests: Multiple param handling in reciprocal registration
  # Validates: Commands with multiple prompt params build complete reciprocal lists
```

**Test 4.4.4: test_param_with_multiple_commands_in_prompt_on_commands**

This test validates that params can explicitly list multiple commands in `PROMPT_ON_COMMANDS` and all reciprocal relationships are established. When a param specifies `PROMPT_ON_COMMANDS: ["cmd1", "cmd2", "cmd3"]`, all three commands should add this param to their `COMMAND_PROMPT_PARAMS` lists. This enables params to prompt before multiple different commands. The test confirms multi-command relationships work correctly.

```gherkin
Scenario: Param with explicit multi-command PROMPT_ON_COMMANDS creates multiple reciprocal links
  Given a param "confirm" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["delete", "reset", "purge"]
  When commands "delete", "reset", "purge" are registered
  Then command "delete" has COMMAND_PROMPT_PARAMS including "confirm"
  And command "reset" has COMMAND_PROMPT_PARAMS including "confirm"
  And command "purge" has COMMAND_PROMPT_PARAMS including "confirm"
  
  # Tests: One-to-many param-command relationships
  # Validates: Single param can prompt before multiple commands with correct reciprocal links
```

**Test 4.4.5: test_param_without_prompt_property_no_reciprocal_building**

This test validates that the reciprocal registration mechanism only activates for prompt-enabled params. Params without `PARAM_PROMPT` should not trigger any reciprocal list building, even if they're in `COMMAND_REQUIRED_PARAMS`. This ensures the prompt system remains opt-in and doesn't affect non-interactive params. The test confirms params without `PARAM_PROMPT` are excluded from reciprocal registration.

```gherkin
Scenario: Param without PARAM_PROMPT does not trigger reciprocal list building
  Given a param "config_file" with no PARAM_PROMPT property
  When command "process" registered with COMMAND_REQUIRED_PARAMS ["config_file"]
  Then param "config_file" has no PROMPT_ON_COMMANDS list
  And command "process" has empty COMMAND_PROMPT_PARAMS list
  And no reciprocal relationship created
  
  # Tests: Opt-in nature of prompt system
  # Validates: Only params with PARAM_PROMPT participate in reciprocal registration
```

**Test 4.4.6: test_registration_order_independence**

This test validates that reciprocal registration works correctly regardless of whether params or commands are registered first. The framework should handle both scenarios: params registered before commands (forward reference) and commands registered before params (backward reference). This order independence prevents fragile registration sequences. The test confirms reciprocal lists are built correctly in both registration orders.

```gherkin
Scenario: Reciprocal registration works with both param-first and command-first order
  Given test runs twice with different registration orders
  
  # Order 1: Param first, then command
  When param "value" registered with PARAM_PROMPT and auto-population flag
  And then command "calc" registered with COMMAND_REQUIRED_PARAMS ["value"]
  Then reciprocal lists built correctly
  
  # Order 2: Command first, then param
  When command "calc" registered with COMMAND_REQUIRED_PARAMS ["value"]
  And then param "value" registered with PARAM_PROMPT and auto-population flag
  Then reciprocal lists built correctly (deferred until param registration)
  
  And both orders produce identical reciprocal relationship structures
  
  # Tests: Registration order independence
  # Validates: Reciprocal registration handles forward and backward references correctly
```

[↑ Back to top](#table-of-contents)

---

#### Phase 2: Prompt Execution

**Step 5a: Implement prompt execution helpers**

**File:** `src/spafw37/param.py` (or new `src/spafw37/prompt.py`)

Create internal helper functions:
- `_get_prompt_handler(param_def)` - resolve handler (param-level → global → default)
- `_should_prompt_param(param_def, command_name=None, check_value=True)` - determine if prompting needed
- `_execute_prompt_with_validation(param_def, handler)` - run handler, validate, retry on error
- `_format_prompt_text(param_def)` - build prompt string with default value

**Validation and retry logic:**
- Use existing framework validation functions
- Max retry limit (e.g., 3 attempts)
- On max retry: exit if required, set None if optional

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 5b: Test prompt execution helpers**

**File:** `tests/test_param_prompts.py` (extend)

**Tests:** Test internal helper functions that orchestrate prompt execution, handler resolution, validation, and retry logic.

This step validates the prompt execution infrastructure that coordinates between handlers, validation, and param value management. These helper functions encapsulate the complex logic of determining when prompts should appear, which handler to use, how to validate input, and what to do when validation fails. By testing these helpers in isolation, we ensure the prompt execution engine works correctly before integration with the full CLI workflow.

**Test 5.5.1: test_handler_resolution_param_level_precedence**

This test validates the handler resolution precedence order. When a param has `PARAM_PROMPT_HANDLER` set, that handler must take precedence over the global handler (set via `set_prompt_handler()`) and the default handler (`input_prompt.py`). This three-tier precedence system (param-level → global → default) enables fine-grained control whilst providing sensible defaults. The test confirms param-level handlers override all others.

```gherkin
Scenario: Param-level handler takes precedence over global and default handlers
  Given a param with PARAM_PROMPT_HANDLER set to custom_param_handler
  And global handler set to custom_global_handler via set_prompt_handler()
  And default handler is input_prompt.prompt_for_value
  When _get_prompt_handler(param_def) is called
  Then function returns custom_param_handler
  And global handler not used
  And default handler not used
  
  # Tests: Handler resolution precedence (param > global > default)
  # Validates: Param-specific handlers override global configuration
```

**Test 5.5.2: test_handler_resolution_global_precedence**

This test validates that the global handler takes precedence over the default handler when no param-level handler is set. Applications can call `set_prompt_handler()` to replace the default `input()` behaviour globally without modifying every param. The test confirms this middle tier of precedence works correctly, enabling application-wide handler customization whilst respecting param-specific overrides.

```gherkin
Scenario: Global handler takes precedence over default when no param-level handler
  Given a param with no PARAM_PROMPT_HANDLER property
  And global handler set to custom_global_handler via set_prompt_handler()
  And default handler is input_prompt.prompt_for_value
  When _get_prompt_handler(param_def) is called
  Then function returns custom_global_handler
  And default handler not used
  
  # Tests: Handler resolution precedence (global > default)
  # Validates: Global handler customization works without param-level overrides
```

**Test 5.5.3: test_handler_resolution_default_fallback**

This test validates the default handler fallback when neither param-level nor global handlers are set. The default handler (`input_prompt.prompt_for_value`) should always be available as the final fallback, ensuring prompts work out-of-the-box without configuration. The test confirms the resolution logic correctly falls through to the default when no customization is present.

```gherkin
Scenario: Default handler used when no param-level or global handler configured
  Given a param with no PARAM_PROMPT_HANDLER property
  And no global handler set (_global_prompt_handler is None)
  And default handler is input_prompt.prompt_for_value
  When _get_prompt_handler(param_def) is called
  Then function returns input_prompt.prompt_for_value
  And default handler provides out-of-box functionality
  
  # Tests: Default handler fallback
  # Validates: Prompts work without configuration using built-in handler
```

**Test 5.5.4: test_should_prompt_timing_on_start**

This test validates the timing check for `PROMPT_ON_START`. When a param has `PARAM_PROMPT_TIMING == PROMPT_ON_START`, the `_should_prompt_param()` function should return true (assuming param has no value and other conditions are met). This enables prompts immediately after CLI parsing. The test confirms the timing check correctly identifies start-timing prompts.

```gherkin
Scenario: Should prompt returns true for PROMPT_ON_START timing without command context
  Given a param with PARAM_PROMPT_TIMING == PROMPT_ON_START
  And param has no current value
  When _should_prompt_param(param_def, command_name=None) is called
  Then function returns True
  And prompt should execute at application start
  
  # Tests: Timing check for PROMPT_ON_START
  # Validates: Framework identifies params that prompt after CLI parsing
```

**Test 5.5.5: test_should_prompt_timing_on_commands_match**

This test validates the timing check for `PROMPT_ON_COMMANDS` when the current command name matches. When a param has `PROMPT_ON_COMMANDS` containing the executing command's name, `_should_prompt_param()` should return true. This enables command-specific prompts. The test confirms the timing check correctly matches command names against the param's list.

```gherkin
Scenario: Should prompt returns true when command name in PROMPT_ON_COMMANDS list
  Given a param with PROMPT_ON_COMMANDS ["process", "execute"]
  And param has no current value
  When _should_prompt_param(param_def, command_name="execute") is called
  Then function returns True
  And prompt should execute before "execute" command
  
  # Tests: Timing check for PROMPT_ON_COMMANDS with matching command
  # Validates: Framework identifies params that prompt before specific commands
```

**Test 5.5.6: test_should_prompt_timing_on_commands_no_match**

This test validates that `_should_prompt_param()` returns false when the command name doesn't match any in `PROMPT_ON_COMMANDS`. Prompts should only appear before the commands explicitly listed, not all commands. The test confirms the timing check correctly excludes commands not in the list.

```gherkin
Scenario: Should prompt returns false when command name not in PROMPT_ON_COMMANDS
  Given a param with PROMPT_ON_COMMANDS ["process", "execute"]
  And param has no current value
  When _should_prompt_param(param_def, command_name="other") is called
  Then function returns False
  And prompt should not execute before "other" command
  
  # Tests: Timing check exclusion for unlisted commands
  # Validates: Prompts only appear before explicitly listed commands
```

**Test 5.5.7: test_should_prompt_value_already_set**

This test validates the CLI override behaviour. When a param already has a value (set via CLI arguments), `_should_prompt_param()` should return false regardless of timing configuration. This implements the "if set, don't prompt" policy that prevents unnecessary prompts when users provide values upfront. The test confirms value checks short-circuit prompt execution.

```gherkin
Scenario: Should prompt returns false when param value already set via CLI
  Given a param with PARAM_PROMPT_TIMING == PROMPT_ON_START
  And param has current value "cli_value" (set via CLI)
  When _should_prompt_param(param_def, check_value=True) is called
  Then function returns False
  And prompt should not execute (CLI override in effect)
  
  # Tests: CLI override behaviour
  # Validates: Params set via CLI don't prompt (no confirmation needed)
```

**Test 5.5.8: test_should_prompt_repeat_never_second_call**

This test validates the `PROMPT_REPEAT_NEVER` behaviour. After a param has been prompted once (tracked in `_prompted_params` set), subsequent calls to `_should_prompt_param()` should return false. This ensures single-prompt behaviour for initialization values. The test confirms the tracking mechanism correctly prevents repeat prompts.

```gherkin
Scenario: Should prompt returns false on second call for PROMPT_REPEAT_NEVER
  Given a param with PARAM_PROMPT_REPEAT == PROMPT_REPEAT_NEVER
  And param name in _prompted_params set (already prompted once)
  When _should_prompt_param(param_def) is called
  Then function returns False
  And prompt should not repeat
  
  # Tests: PROMPT_REPEAT_NEVER tracking
  # Validates: Params marked as prompted once don't re-prompt
```

**Test 5.5.9: test_execute_prompt_with_validation_success**

This test validates the happy path: user enters valid input, validation passes, param value is set. The `_execute_prompt_with_validation()` function should call the handler, validate the result using framework validation functions, and set the param value if validation succeeds. The test confirms successful prompt execution with valid input.

```gherkin
Scenario: Valid input accepted, validated, and param value set correctly
  Given a param with PARAM_TYPE_NUMBER and validation rules
  And stdin mocked with StringIO("42\n")
  And handler is default input_prompt.prompt_for_value
  When _execute_prompt_with_validation(param_def, handler) is called
  Then handler called once
  And validation functions called with "42"
  And validation passes
  And param value set to 42
  And function returns successfully
  
  # Tests: Successful prompt execution with validation
  # Validates: Valid input flows through handler → validation → param value
```

**Test 5.5.10: test_execute_prompt_with_validation_retry**

This test validates the retry logic when validation fails. After invalid input, the function should display an error message, call the handler again, and continue until valid input is received (up to max retry limit). The test confirms retry logic works correctly, allowing users to correct mistakes without restarting the application.

```gherkin
Scenario: Invalid input triggers retry, eventually accepts valid input
  Given a param with PARAM_TYPE_NUMBER
  And stdin mocked with StringIO("invalid\n42\n")
  And handler is default input_prompt.prompt_for_value
  And max retry limit is 3
  When _execute_prompt_with_validation(param_def, handler) is called
  Then handler called twice (once for "invalid", once for "42")
  And validation fails on first attempt with clear error message
  And validation passes on second attempt
  And param value set to 42
  
  # Tests: Validation retry logic
  # Validates: Users can correct invalid input without restarting
```

**Test 5.5.11: test_execute_prompt_max_retry_required_param**

This test validates the max retry behaviour for required params. When a required param fails validation max_retry times, the framework should exit the application with a clear error message. This prevents infinite retry loops whilst ensuring required values are always provided or the application fails predictably. The test confirms the exit behaviour for required params after max retries.

```gherkin
Scenario: Required param exits application after max retry limit reached
  Given a param with PARAM_REQUIRED == True
  And stdin mocked with StringIO("invalid1\ninvalid2\ninvalid3\n")
  And max retry limit is 3
  When _execute_prompt_with_validation(param_def, handler) is called
  Then handler called 3 times (max retries)
  And all three inputs fail validation
  And application exits with error message indicating max retries exceeded
  And param value not set
  
  # Tests: Max retry behaviour for required params
  # Validates: Required params force application exit after max retry failures
```

**Test 5.5.12: test_execute_prompt_max_retry_optional_param**

This test validates the max retry behaviour for optional params. When an optional param fails validation max_retry times, the framework should set the param value to `None` and continue execution. This allows applications to proceed with missing optional values without forcing exit. The test confirms optional params set to `None` after max retries rather than exiting.

```gherkin
Scenario: Optional param sets None and continues after max retry limit
  Given a param with PARAM_REQUIRED == False (optional)
  And stdin mocked with StringIO("invalid1\ninvalid2\ninvalid3\n")
  And max retry limit is 3
  When _execute_prompt_with_validation(param_def, handler) is called
  Then handler called 3 times (max retries)
  And all three inputs fail validation
  And param value set to None
  And function returns without exiting application
  
  # Tests: Max retry behaviour for optional params
  # Validates: Optional params set None after max retries (graceful degradation)
```

**Test 5.5.13: test_format_prompt_text_with_default**

This test validates the prompt text formatting function when a default value exists. The formatted prompt should include the bash convention `[default: value]` to clearly indicate what will happen if the user presses Enter. The test confirms the formatting function produces correct output with default values displayed.

```gherkin
Scenario: Prompt text includes default value in bash convention format
  Given a param with PARAM_PROMPT "Enter name:" and PARAM_DEFAULT "John"
  When _format_prompt_text(param_def) is called
  Then function returns "Enter name: [default: John] "
  And format follows bash convention
  And trailing space included for cursor positioning
  
  # Tests: Prompt text formatting with defaults
  # Validates: Users see clear indication of default value behaviour
```

**Test 5.5.14: test_format_prompt_text_without_default**

This test validates the prompt text formatting when no default value exists. The formatted prompt should display just the prompt text without the `[default: ...]` indicator. The test confirms the formatting function handles missing defaults correctly.

```gherkin
Scenario: Prompt text without default value shows only prompt message
  Given a param with PARAM_PROMPT "Enter value:" and no PARAM_DEFAULT
  When _format_prompt_text(param_def) is called
  Then function returns "Enter value: "
  And no default indicator shown
  And trailing space included for cursor positioning
  
  # Tests: Prompt text formatting without defaults
  # Validates: Prompts without defaults display cleanly without extra brackets
```

[↑ Back to top](#table-of-contents)

---

**Step 6a: Integrate PROMPT_ON_START timing**

**File:** `src/spafw37/cli.py` or appropriate orchestration module

After CLI parsing completes, before command execution:
- Iterate `param._params` dictionary
- For each param with `PARAM_PROMPT_TIMING == PROMPT_ON_START`:
  - Check if param has value (CLI didn't set it)
  - If no value, call `_execute_prompt_with_validation()`
  - Set param value from prompt result

**Integration point:** After `_parse_command_line()` returns, before command queue processing

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 6b: Test PROMPT_ON_START integration**

**File:** `tests/test_integration_prompts.py`

**Tests:** Integration tests for PROMPT_ON_START timing within the full CLI workflow.

This step validates that PROMPT_ON_START timing integrates correctly with the CLI parsing and command execution pipeline. These tests use the complete framework stack, ensuring prompts appear at the right moment (after CLI parsing, before command execution), CLI overrides work correctly, multiple params prompt in sequence, and validation/required param checking integrates seamlessly with the prompt system.

**Test 6.6.1: test_prompt_on_start_basic_execution**

This test validates the fundamental PROMPT_ON_START workflow: param prompts after CLI parsing, user provides input, param value is set, command executes with the prompted value. This is the happy path for start-timing prompts. The test confirms the complete flow from prompt to command execution works correctly without any special conditions or edge cases.

```gherkin
Scenario: Param with PROMPT_ON_START prompts after CLI parsing before command execution
  Given a param "username" with PARAM_PROMPT and PROMPT_ON_START timing
  And a command "greet" that uses param "username"
  And stdin mocked with StringIO("Alice\n")
  When application runs with command line "greet"
  Then CLI parsing completes first
  And prompt appears with "Enter username:"
  And user input "Alice" captured and validated
  And param "username" value set to "Alice"
  And command "greet" executes with username="Alice"
  
  # Tests: Basic PROMPT_ON_START integration
  # Validates: Start-timing prompts work in complete CLI workflow
```

**Test 6.6.2: test_prompt_on_start_cli_override_skips_prompt**

This test validates the CLI override behaviour for PROMPT_ON_START. When a user provides a param value via command-line arguments, the prompt should be skipped entirely—no confirmation, no display. This implements the "if set, don't prompt" policy. The test confirms CLI values prevent prompts from appearing, ensuring predictable behaviour and respecting explicit user input.

```gherkin
Scenario: Param set via CLI skips PROMPT_ON_START prompt entirely
  Given a param "username" with PARAM_PROMPT and PROMPT_ON_START timing
  And a command "greet" that uses param "username"
  When application runs with command line "--username Bob greet"
  Then CLI parsing sets username="Bob"
  And prompt phase checks param has value
  And prompt skipped (CLI override in effect)
  And no stdin read occurs
  And command "greet" executes with username="Bob"
  
  # Tests: CLI override behaviour for PROMPT_ON_START
  # Validates: Command-line arguments prevent prompts (no confirmation needed)
```

**Test 6.6.3: test_prompt_on_start_multiple_params_sequential**

This test validates that multiple PROMPT_ON_START params prompt sequentially in a predictable order. When several params need prompting at start, users should see them one at a time, provide input for each, and the application should continue only after all prompts complete. The test confirms multiple start-timing prompts work correctly without interfering with each other.

```gherkin
Scenario: Multiple PROMPT_ON_START params prompt sequentially in order
  Given params "name", "age", "city" all with PARAM_PROMPT and PROMPT_ON_START
  And stdin mocked with StringIO("Alice\n30\nLondon\n")
  When application runs with command line "process"
  Then prompt 1 appears for "name", input "Alice" captured
  And prompt 2 appears for "age", input "30" captured
  And prompt 3 appears for "city", input "London" captured
  And all three params have values set
  And command "process" executes with all three values
  
  # Tests: Multiple PROMPT_ON_START params
  # Validates: Sequential prompting works without interference
```

**Test 6.6.4: test_prompt_on_start_required_validation_failure**

This test validates the required param validation integration. When a required param with PROMPT_ON_START fails validation after max retries, the framework should exit with a clear error message rather than proceeding with invalid/missing data. This ensures data integrity for required params. The test confirms the framework enforces required param constraints even with interactive prompts.

```gherkin
Scenario: Required param with PROMPT_ON_START exits after max retry validation failures
  Given a param "port" with PARAM_PROMPT, PROMPT_ON_START, PARAM_REQUIRED=True
  And param has validation rules (must be integer 1-65535)
  And stdin mocked with StringIO("invalid\nbad\nwrong\n")
  And max retry limit is 3
  When application runs
  Then three prompts occur, all inputs fail validation
  And application exits with error "Max retries exceeded for required param 'port'"
  And command execution does not occur
  
  # Tests: Required param validation with PROMPT_ON_START
  # Validates: Framework enforces required param constraints with prompts
```

**Test 6.6.5: test_prompt_on_start_optional_continues_after_failure**

This test validates graceful degradation for optional params. When an optional param with PROMPT_ON_START fails validation after max retries, the framework should set the param to None and continue execution. This allows applications to handle missing optional values without forcing exit. The test confirms optional params enable graceful degradation whilst still attempting to collect user input.

```gherkin
Scenario: Optional param with PROMPT_ON_START sets None after max retries and continues
  Given a param "theme" with PARAM_PROMPT, PROMPT_ON_START, PARAM_REQUIRED=False
  And stdin mocked with StringIO("invalid\nbad\nwrong\n")
  And max retry limit is 3
  When application runs with command "start"
  Then three prompts occur, all inputs fail validation
  And param "theme" set to None
  And application continues without exit
  And command "start" executes with theme=None
  
  # Tests: Optional param graceful degradation
  # Validates: Applications can continue with missing optional values
```

**Test 6.6.6: test_prompt_on_start_default_value_handling**

This test validates default value behaviour in PROMPT_ON_START prompts. When a param has a default value and the user presses Enter without typing, the default should be used automatically. The prompt should display the default using bash convention `[default: value]` so users know what will happen. The test confirms default value handling works correctly in the integrated workflow.

```gherkin
Scenario: Blank input with default value uses default in PROMPT_ON_START
  Given a param "language" with PARAM_PROMPT, PROMPT_ON_START, PARAM_DEFAULT="en"
  And stdin mocked with StringIO("\n")
  When application runs with command "configure"
  Then prompt displays "Enter language: [default: en]"
  And user presses Enter (blank input)
  And param "language" set to "en" (default)
  And command "configure" executes with language="en"
  
  # Tests: Default value handling in PROMPT_ON_START
  # Validates: Bash convention defaults work in integrated workflow
```

[↑ Back to top](#table-of-contents)

---

**Step 7a: Integrate PROMPT_ON_COMMANDS timing**

**File:** `src/spafw37/command.py` or appropriate command execution module

Before each command action executes:
- Look up `COMMAND_PROMPT_PARAMS` on command definition (O(1))
- For each param in list:
  - Check `PARAM_PROMPT_REPEAT` setting and current value
  - If should prompt, call `_execute_prompt_with_validation()`
  - Update param value from prompt result

**Repeat behaviour implementation:**
- `PROMPT_REPEAT_ALWAYS`: Always prompt, show previous value as default
- `PROMPT_REPEAT_IF_BLANK`: Only prompt if value is None/empty
- `PROMPT_REPEAT_NEVER`: Check `_prompted_params` set, skip if already prompted

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

---

**Step 7b: Test PROMPT_ON_COMMANDS integration**

**File:** `tests/test_integration_prompts.py` (extend)

**Tests:** Integration tests for PROMPT_ON_COMMANDS timing and all repeat behaviour options.

This step validates that PROMPT_ON_COMMANDS timing integrates correctly with command execution, enabling prompts immediately before specific commands run. These tests cover the complete repeat behaviour spectrum (ALWAYS, IF_BLANK, NEVER), ensuring prompts appear at the right moment, CLI overrides work, and the framework correctly tracks prompt state across multiple command executions. This is the most complex timing mode due to repeat behaviour interactions.

**Test 7.7.1: test_prompt_on_commands_basic_execution**

This test validates the fundamental PROMPT_ON_COMMANDS workflow: param prompts immediately before the specified command executes, user provides input, param value is set, command proceeds with the prompted value. This establishes the basic command-timing behaviour without repeat complexities. The test confirms prompts appear at the correct moment in the command execution pipeline.

```gherkin
Scenario: Param prompts immediately before specified command execution
  Given a param "confirm" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["delete"]
  And commands "list" and "delete" registered
  And stdin mocked with StringIO("yes\n")
  When application runs with command line "list delete"
  Then command "list" executes first without prompting
  And before "delete" executes, prompt appears "Enter confirm:"
  And user input "yes" captured and validated
  And param "confirm" set to "yes"
  And command "delete" executes with confirm="yes"
  
  # Tests: Basic PROMPT_ON_COMMANDS integration
  # Validates: Command-timing prompts appear immediately before execution
```

**Test 7.7.2: test_prompt_on_commands_cli_override_skips_prompt**

This test validates CLI override behaviour for PROMPT_ON_COMMANDS. When a param value is set via command-line arguments, prompts should be skipped even when the command is about to execute. This maintains the consistent "if set, don't prompt" policy across all timing modes. The test confirms CLI overrides work correctly with command-timing prompts.

```gherkin
Scenario: Param set via CLI skips PROMPT_ON_COMMANDS prompt before command
  Given a param "confirm" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["delete"]
  And stdin mocked with StringIO("") (empty, should not be read)
  When application runs with command line "--confirm yes delete"
  Then CLI parsing sets confirm="yes"
  And before "delete" executes, prompt check occurs
  And prompt skipped because value already set
  And no stdin read occurs
  And command "delete" executes with confirm="yes"
  
  # Tests: CLI override with PROMPT_ON_COMMANDS
  # Validates: Command-line arguments prevent command-timing prompts
```

**Test 7.7.3: test_prompt_on_commands_multiple_commands_listed**

This test validates that a param can prompt before multiple different commands when listed in PROMPT_ON_COMMANDS. Each command in the list should trigger a prompt check (subject to repeat behaviour). This enables shared params that need confirmation before several sensitive operations. The test confirms multi-command PROMPT_ON_COMMANDS lists work correctly.

```gherkin
Scenario: Param with multiple commands in PROMPT_ON_COMMANDS prompts before each
  Given a param "confirm" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["delete", "reset", "purge"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_ALWAYS
  And stdin mocked with StringIO("yes\nyes\nyes\n")
  When application runs with command line "delete reset purge"
  Then before "delete", prompt appears, input "yes" captured
  And before "reset", prompt appears again, input "yes" captured
  And before "purge", prompt appears again, input "yes" captured
  And all three commands execute with confirm="yes"
  
  # Tests: Multiple commands in PROMPT_ON_COMMANDS
  # Validates: Param can prompt before several different commands
```

**Test 7.7.4: test_prompt_repeat_always_shows_previous_value**

This test validates PROMPT_REPEAT_ALWAYS behaviour. Every time a listed command executes, the prompt should appear and display the previous value as the default. This enables users to confirm or change the value on each execution. The test confirms REPEAT_ALWAYS prompts every time and preserves the previous value as the default.

```gherkin
Scenario: PROMPT_REPEAT_ALWAYS prompts before every command execution with previous value
  Given a param "action" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["step"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_ALWAYS
  And stdin mocked with StringIO("first\nsecond\nthird\n")
  When application runs with command line "step step step"
  Then iteration 1: prompt appears, input "first", action="first"
  And iteration 2: prompt shows [default: first], input "second", action="second"
  And iteration 3: prompt shows [default: second], input "third", action="third"
  And all three executions complete with different values
  
  # Tests: PROMPT_REPEAT_ALWAYS behaviour
  # Validates: Every execution prompts, previous value shown as default
```

**Test 7.7.5: test_prompt_repeat_if_blank_prompts_when_blank_only**

This test validates PROMPT_REPEAT_IF_BLANK behaviour. The first execution should prompt (value is blank), subsequent executions should skip prompting if the value is still set. This enables efficient re-use of values whilst allowing re-prompting if the value gets cleared. The test confirms REPEAT_IF_BLANK only prompts when necessary.

```gherkin
Scenario: PROMPT_REPEAT_IF_BLANK prompts only when value is blank
  Given a param "token" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["api_call"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_IF_BLANK
  And stdin mocked with StringIO("abc123\n")
  When application runs with command line "api_call api_call api_call"
  Then iteration 1: value blank, prompt appears, input "abc123" captured
  And iteration 2: value still "abc123", prompt skipped
  And iteration 3: value still "abc123", prompt skipped
  And all three executions use token="abc123"
  
  # Tests: PROMPT_REPEAT_IF_BLANK behaviour
  # Validates: Prompts only when value is blank, reuses set values
```

**Test 7.7.6: test_prompt_repeat_never_prompts_once_then_stops**

This test validates PROMPT_REPEAT_NEVER behaviour. Only the first execution of a listed command should prompt; all subsequent executions should skip prompting entirely. This enables one-time initialization values. The test confirms REPEAT_NEVER prompts exactly once and tracks prompt state correctly across multiple executions.

```gherkin
Scenario: PROMPT_REPEAT_NEVER prompts once on first execution then never repeats
  Given a param "config" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["process"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_NEVER
  And stdin mocked with StringIO("settings.json\n")
  When application runs with command line "process process process"
  Then iteration 1: prompt appears, input "settings.json" captured
  And param "config" added to _prompted_params tracking set
  And iteration 2: prompt skipped (already prompted), config="settings.json"
  And iteration 3: prompt skipped (already prompted), config="settings.json"
  And all three executions use same value
  
  # Tests: PROMPT_REPEAT_NEVER behaviour
  # Validates: Single prompt with persistent value across executions
```

**Test 7.7.7: test_prompt_on_commands_with_cycle_repeat_always**

This test validates PROMPT_ON_COMMANDS behaviour in cycles with REPEAT_ALWAYS. Each cycle iteration should trigger a prompt before the command executes. This enables per-iteration confirmation or value changes in loops. The test confirms REPEAT_ALWAYS works correctly in cycle contexts, prompting on every iteration.

```gherkin
Scenario: REPEAT_ALWAYS in cycle prompts on every iteration
  Given a param "item" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["process_item"]
  And PARAM_PROMPT_REPEAT=PROMPT_REPEAT_ALWAYS
  And a cycle command that runs "process_item" 3 times
  And stdin mocked with StringIO("item1\nitem2\nitem3\n")
  When cycle executes
  Then cycle iteration 1: prompt appears, input "item1"
  And cycle iteration 2: prompt appears, input "item2"
  And cycle iteration 3: prompt appears, input "item3"
  And each iteration processes different value
  
  # Tests: REPEAT_ALWAYS in cycles
  # Validates: Per-iteration prompting works correctly in loops
```

**Test 7.7.8: test_prompt_on_commands_command_queue_dependencies**

This test validates that prompts work correctly with command dependencies and sequencing. When commands have dependencies or specific execution orders, prompts should still appear at the right moment before each listed command executes. The test confirms prompt timing respects command orchestration logic and doesn't interfere with dependencies.

```gherkin
Scenario: Prompts respect command queue order and dependencies
  Given commands "prepare", "validate", "execute" with dependencies
  And param "mode" with PARAM_PROMPT and PROMPT_ON_COMMANDS ["validate", "execute"]
  And stdin mocked with StringIO("strict\n")
  When command queue processes with dependencies
  Then "prepare" executes first (no prompt, not in list)
  And before "validate", prompt appears, input "strict" captured
  And "validate" executes with mode="strict"
  And before "execute", prompt check occurs (REPEAT_NEVER, already prompted)
  And "execute" executes with mode="strict" (same value)
  
  # Tests: Prompts with command dependencies
  # Validates: Prompt timing respects command orchestration
```

[↑ Back to top](#table-of-contents)

---

**Step 8a: Add cycle-specific tests**

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

**Step 8b: Add extensibility tests**

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
- **Timing options:** Examples of `PROMPT_ON_START` vs `PROMPT_ON_COMMANDS`
- **Repeat behaviour:** Examples of each `PROMPT_REPEAT_*` option in cycles
- **Custom handlers:** Guide for implementing and registering custom prompt handlers
- **Multiple choice:** Dynamic population with `set_allowed_values()` examples
- **CLI override:** Explain how CLI args prevent prompting
- **Auto-population:** Document `PROMPT_ON_COMMANDS` auto-population from `COMMAND_REQUIRED_PARAMS`
- **Complete examples:** Working examples demonstrating common use cases

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
- **Future consideration:** May expand to support lists with multiple choice (enter choices by number separated by spaces or commas) - provisional only

**Rationale:** Integrates with existing param system, validation, and type handling. Leverages existing properties where possible (`PARAM_TYPE`, `PARAM_ALLOWED_VALUES`). Extensible design allows custom prompt handlers for advanced use cases (GUI prompts, API-based input, etc.) whilst providing sensible default behaviour.

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
- Timing control ✅ (Decided: `PARAM_PROMPT_TIMING` with `PROMPT_ON_START` / `PROMPT_ON_COMMANDS`)
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
