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
- [Further Considerations](#further-considerations)
  - [1. Design Pattern Research](#1-design-pattern-research---resolved)
  - [2. Architecture Approach Trade-offs](#2-architecture-approach-trade-offs---resolved)
  - [3. Implementation Complexity Assessment](#3-implementation-complexity-assessment---pending-review)
  - [4. User Experience Considerations](#4-user-experience-considerations---resolved)
  - [5. Alternative Solutions](#5-alternative-solutions---pending-review)
  - [6. Backward Compatibility and Breaking Changes](#6-backward-compatibility-and-breaking-changes---pending-review)
  - [7. Testing Strategy](#7-testing-strategy---pending-review)
- [Fixing Regressions](#fixing-regressions)
- [Implementation Plan Changes](#implementation-plan-changes)
- [Documentation Updates](#documentation-updates)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

---

## Overview

Add params that solicit user input before a Command.

- Will display a text prompt, and allow the user to enter (or select) a value.
- Types - text, bool, number or multiple choice (select from list)
  - Select from list - populate data programatically. Specify command to populate list? Would be first instance of a param specifying a command, rather than vice versa...
- Prompt can be either at the start of a flow, or immediately before the command is executed
  - Flag on Command? Will probably need to be, to not need special handling in cycles
- Not included in validation, as not a command line param
- Option to set on command line up front?
  - What behaviour if on a Cycle Command - pop up to confirm value if set, silently pass if value is set, or make optional?

Should be params with special features, or another structure entirely?

**Critical analysis:**

This feature has several unresolved design questions that make implementation premature. These questions have been documented below and should be posted as a comment on GitHub issue #15 for tracking.

**Key architectural decisions (pending user input):**

- **Architecture approach:** Whether to extend existing param system or create separate structure
- **Timing control:** Param-driven vs command-driven prompt execution
- **CLI integration:** Behaviour when values provided via command line
- **Cycle integration:** Handling of prompts within cycle iterations
- **Validation strategy:** How user input validation integrates with existing param validation

## Success Criteria

[PENDING REVIEW - To be completed in Step 5]

## Implementation Plan

### Program Flow Analysis

**Not applicable** - Cannot analyse program flow without design decisions from user.

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

**Answer:** Will use flags for timing control - requires further analysis. Timing control and cycle integration (Q5) are conceptually linked. Will consider param-level and/or command-level flags.

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

**Answer:** Will use flags for cycle control - linked with timing control (Q3). Cycle integration and timing control are conceptually linked. Requires further analysis to determine optimal flag structure.

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

**Answer:** See [Further Consideration 1: Design Pattern Research](#1-design-pattern-research---resolved) - Use Python's built-in `input()` function with appropriate type conversion and validation.

[↑ Back to top](#table-of-contents)

---

**Q8: Silent/Batch Mode** ([#issuecomment-3587791532](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791532))

How should prompts interact with existing framework flags?
- Should prompts be suppressed with `--silent`?
- How to disable prompts for automated scripts/batch mode?
- Should there be a `--no-prompts` flag?

**Answer:** Suppress prompts when `--silent` flag used. Consider adding `--no-prompts` flag. In batch/silent mode: use default if available, use `None` if no default and not required, exit with error if required and no default/value.

[↑ Back to top](#table-of-contents)

---

**Next Steps:**

Once design decisions are provided, implementation planning can proceed to define:
1. Specific implementation steps
2. Test specifications
3. Code changes with file paths and function signatures
4. Documentation updates

## Further Considerations

### 1. Design Pattern Research - RESOLVED

([#issuecomment-3587791560](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791560))

**Question:** How do other CLI frameworks handle interactive user input?

**Answer:** Simplest approach - display a prompt for the user using `print()` statements, and capture input using `input()`.

**Rationale:** Python's built-in `input()` function is simple, requires no dependencies, works on all platforms, and is what most Python CLI tools use. No need to complicate with external libraries.

**Implementation:** Use `input()` for capturing user responses with appropriate type conversion and validation.

**Resolves:** Q7 (User Input Mechanism)

[↑ Back to top](#table-of-contents)

---

### 2. Architecture Approach Trade-offs - RESOLVED

([#issuecomment-3587791581](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791581))

**Question:** What are the pros and cons of each architecture approach?

**Answer:** Option A - Param-level approach.

**Implementation details:**
- Add `PARAM_PROMPT` property to param definitions (e.g., `{PARAM_PROMPT: "What is the air-speed velocity of an unladen swallow?"}`)
- Use existing `PARAM_TYPE` to determine input handling:
  - `TEXT` - accepts any text input
  - `NUMBER` - validates numeric input
  - `TOGGLE` - accepts boolean values
- Multiple choice automatically enabled when `PARAM_ALLOWED_VALUES` is present:
  - Display numbered list of allowed values
  - User can enter either the text value or the corresponding number
  - List displayed automatically with assigned numbers
- **Future consideration:** May expand to support lists with multiple choice (enter choices by number separated by spaces or commas) - provisional only

**Rationale:** Integrates with existing param system, validation, and type handling. Leverages existing properties where possible (`PARAM_TYPE`, `PARAM_ALLOWED_VALUES`).

**Breaking changes:** Low (new optional properties only).

**Resolves:** Q1 (Architecture Approach)

[↑ Back to top](#table-of-contents)

---

### 3. Implementation Complexity Assessment - PENDING REVIEW

([#issuecomment-3587791599](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791599))

**Question:** What is the relative complexity of different aspects of this feature?

**Answer:**

**Low complexity:**
- Text input with `input()` function ✅ (Decided: use Python's `input()`)
- Basic type conversion (only relevant for `get_param()` retrieval and multi-choice number resolution)
- CLI override behaviour ✅ (Decided: "if set, don't prompt")

**Medium complexity:**
- Type validation ✅ (Decided: use existing framework validation functions)
- Default handling ✅ (Decided: bash convention `[default: value]`, blank selects default)
- Retry logic ✅ (Decided: re-prompt on error, max retry limit with required/optional behaviour)
- Boolean/number parsing ✅ (Decided: use existing `INPUT_FILTER`, toggles use y/n with natural defaults)
- Multiple choice with static lists ✅ (Decided: use `PARAM_ALLOWED_VALUES`)

**High complexity:**
- Multiple choice with dynamic population ✅ (Decided: new public API `set_allowed_values()` method)
- Cycle integration ⚠️ (TBD: needs further analysis, linked with timing control)
- Timing control ⚠️ (TBD: needs further analysis, linked with cycle behaviour)

**Very high complexity (deferred):**
- Command-driven population ❌ (Not implementing as special feature in this version, achievable via `set_allowed_values()`)

**Status:** Most decisions made. Remaining work: analyse timing control and cycle integration flags (Q3 & Q5).

**Rationale:** Helps prioritise features and identify implementation risks. Most features can leverage existing framework infrastructure, reducing complexity.

**Implementation:** Phased approach - core features first (text, validation, defaults, retries), then advanced features (timing control, cycle integration) after further analysis.

**Resolves:** Q2, Q4, Q6, Q7, Q8 (partially resolves Q3 & Q5 - pending further analysis)

[↑ Back to top](#table-of-contents)

---

### 4. User Experience Considerations - RESOLVED

([#issuecomment-3587791616](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791616))

**Question:** How should prompts interact with existing framework features?

**Answer:** Several UX questions resolved:
- **Silent mode:** ✅ Prompts suppressed with `--silent` flag
- **Batch mode:** ✅ Consider adding `--no-prompts` flag for automated scripts
- **Testing:** Mock user input using stdin redirection or test fixtures
- **Help text:** Add "Will prompt if not provided" to param description
- **Error messages:** Provide clear guidance when prompts fail or are unavailable
- **Silent/batch behaviour:** Use default if available, `None` if no default and not required, exit with error if required and no default/value

**Rationale:** Prompts must work seamlessly with existing framework features and not break automated workflows. Ensures framework remains scriptable.

**Implementation:** Depends on Q8 answer (RESOLVED) and overall architecture choice (RESOLVED).

**Resolves:** Q8 (Silent/Batch Mode)

[↑ Back to top](#table-of-contents)

---

### 5. Alternative Solutions - PENDING REVIEW

([#issuecomment-3587791636](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791636))

**Question:** Should this be built into the framework at all?

**Answer:** Users can currently achieve interactive prompts by:
- Using Python's `input()` directly in command actions
- Using external prompt libraries (Click, Inquirer, PyInquirer)
- Creating helper functions in their application code

**Rationale:** Adding this to the framework increases complexity and maintenance burden. The feature may have limited use cases, as most CLI tools prefer non-interactive behaviour for scriptability.

**Implementation:** Consider whether framework integration provides sufficient value over existing alternatives. May be better as documentation/examples rather than built-in feature.

[↑ Back to top](#table-of-contents)

---

### 6. Backward Compatibility and Breaking Changes - PENDING REVIEW

([#issuecomment-3587791658](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791658))

**Question:** What breaking changes might this introduce?

**Answer:** Risk depends on architecture chosen:
- **Low risk:** Command-level feature (new `COMMAND_PROMPTS` constant and processing)
- **Medium risk:** New param properties (existing params unaffected, but param processing logic changes)
- **High risk:** Changes to param validation or command execution flow (could affect existing behaviour)

**Rationale:** Need to ensure existing applications continue to work without modification.

**Implementation:** Must not change behaviour of existing params or commands. All prompt functionality must be opt-in.

[↑ Back to top](#table-of-contents)

---

### 7. Testing Strategy - PENDING REVIEW

([#issuecomment-3587791692](https://github.com/minouris/spafw37/issues/15#issuecomment-3587791692))

**Question:** How will interactive prompts be tested?

**Answer:** Testing interactive input requires:
- Mocking `stdin` for automated tests
- Test fixtures for different input scenarios (valid input, invalid input, EOF, keyboard interrupt)
- Integration tests for prompt timing and cycle behaviour
- Tests for silent mode and batch mode behaviour

**Rationale:** Interactive code is difficult to test and prone to edge cases.

**Implementation:** Need robust test infrastructure before implementation begins. May require test helper functions for stdin mocking.

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
