# Issue #37: Fix --no-logging Mode to Allow Errors to stderr

## Overview

The `--no-logging` flag is documented to "Disable both console and file logging (errors still to stderr)" but currently suppresses all output including errors. The `log()` function in `src/spafw37/logging.py` contains an early return that prevents any logging when both console and file handlers are disabled, which blocks the error handler from outputting errors to stderr.

This issue fixes the `log()` function to allow ERROR and CRITICAL level messages to reach the stderr handler even when both console and file logging are disabled. The fix preserves the documented behavior where `--no-logging` and `--silent` suppress normal output but still allow error messages to reach stderr, while `--suppress-errors` continues to suppress all output including errors.

The change is minimal and surgical, modifying only the early return condition in the `log()` function to check if the message is an error level before returning. This ensures the error handler remains functional while still preventing unnecessary processing for non-error messages when logging is disabled.

**Key architectural decisions:**

- **Minimal change:** Modify only the early return condition to preserve error output without restructuring the handler management logic
- **Level-based filtering:** Use the existing ERROR constant to determine which messages should bypass the early return
- **Handler independence:** The error handler operates independently and is never removed from the logger, ensuring errors always reach stderr
- **Backward compatibility:** No changes to the public API, parameter behavior, or handler configuration

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Fix log function early return condition](#1-fix-log-function-early-return-condition)
  - [2. Add tests for error output to stderr](#2-add-tests-for-error-output-to-stderr)
- [Further Considerations](#further-considerations)
  - [1. Should warnings also go to stderr?](#1-should-warnings-also-go-to-stderr)
  - [2. Impact on suppress-errors flag](#2-impact-on-suppress-errors-flag)
- [Success Criteria](#success-criteria)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps

### 1. Fix log function early return condition

**File:** `src/spafw37/logging.py`

Modify the early return condition in the `log()` function at line 244-246 to allow ERROR and CRITICAL level messages to proceed even when both console and file logging are disabled.

**Current code:**

```python
# If both are disabled, don't log at all
if not should_log_console and not should_log_file:
    return
```

**Updated code:**

```python
# If both are disabled and this is not an error, don't log at all
# Errors should always go to stderr via error handler
if not should_log_console and not should_log_file and _level < ERROR:
    return
```

**Rationale:**
- The error handler is configured to output ERROR and CRITICAL messages to stderr
- The error handler is never removed from the logger
- By checking `_level < ERROR`, we allow ERROR and CRITICAL messages to proceed to the handler logic
- Non-error messages (TRACE, DEBUG, INFO, WARNING) are still filtered out when logging is disabled

**Tests:**
- `test_no_logging_allows_errors_to_stderr()` - Verify errors appear on stderr with `--no-logging`
- `test_silent_allows_errors_to_stderr()` - Verify errors appear on stderr with `--silent`
- `test_suppress_errors_blocks_stderr()` - Verify `--suppress-errors` still blocks all output

[↑ Back to top](#table-of-contents)

### 2. Add tests for error output to stderr

**File:** `tests/test_logging.py`

Add test cases to verify that error messages reach stderr when console and file logging are disabled.

**Test implementations:**

- `test_no_logging_allows_errors_to_stderr()`:
  - Set `LOG_NO_LOGGING_PARAM` to True
  - Capture stderr output
  - Call `log_error()` with a test message
  - Verify the error message appears in stderr
  - Verify no output to stdout

- `test_silent_allows_errors_to_stderr()`:
  - Set `LOG_SILENT_PARAM` to True
  - Capture stderr output
  - Call `log_error()` with a test message
  - Verify the error message appears in stderr
  - Verify no output to stdout

- `test_suppress_errors_blocks_stderr()`:
  - Set `LOG_SUPPRESS_ERRORS_PARAM` to True
  - Capture stderr output
  - Call `log_error()` with a test message
  - Verify no output to stderr
  - Verify no output to stdout

- `test_no_logging_suppresses_non_errors()`:
  - Set `LOG_NO_LOGGING_PARAM` to True
  - Capture both stdout and stderr
  - Call `log_info()`, `log_warning()`, `log_debug()` with test messages
  - Verify no output to stdout or stderr
  - Ensures non-error messages are still suppressed

**Test pattern:**

```python
def test_no_logging_allows_errors_to_stderr(capfd):
    """Test that errors reach stderr when --no-logging is set.
    
    When no-logging mode is enabled, ERROR and CRITICAL messages should
    still be output to stderr via the error handler. This validates the
    documented behavior of --no-logging.
    """
    # Reset logging state
    logging._reset_logging()
    
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set no-logging mode
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    # Apply logging config
    logging.apply_logging_config()
    
    # Log an error
    logging.log_error(_message="Test error message")
    
    # Capture output
    captured = capfd.readouterr()
    
    # Verify error appears on stderr
    assert "Test error message" in captured.err
    assert "ERROR" in captured.err
    
    # Verify nothing on stdout
    assert "Test error message" not in captured.out
```

**Tests:** Manual verification - run test suite and verify all new tests pass.

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Should warnings also go to stderr?

**Question:** Should WARNING level messages also bypass the early return and go to stderr when logging is disabled?

**Answer:** No, only ERROR and CRITICAL messages should go to stderr.

**Rationale:**
- The documentation explicitly states "errors still to stderr" not "warnings and errors"
- Warnings are informational and can be safely suppressed in silent/no-logging modes
- The error handler is configured with level `ERROR`, not `WARNING`
- Changing this would require updating documentation and potentially user expectations

**Implementation:**
- Use `_level < ERROR` which allows ERROR (40) and CRITICAL (50) to proceed
- WARNING (30) is below ERROR and will be filtered by the early return

[↑ Back to top](#table-of-contents)

### 2. Impact on suppress-errors flag

**Question:** Does this change affect the behavior of `--suppress-errors`?

**Answer:** No, `--suppress-errors` continues to work as documented.

**Rationale:**
- The `--suppress-errors` flag sets the error handler level to `CRITICAL + 1` (line 194-198)
- This happens in `set_suppress_errors()` which is called by `apply_logging_config()`
- By setting the handler level above all standard levels, no messages reach stderr
- This is independent of the early return condition in `log()`

**Implementation:**
- No changes needed to suppress-errors functionality
- The error handler level setting takes precedence over the early return fix
- Test `test_suppress_errors_blocks_stderr()` verifies this behavior

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] Early return condition in `log()` function modified to allow ERROR and CRITICAL messages
- [ ] Test `test_no_logging_allows_errors_to_stderr()` added and passing
- [ ] Test `test_silent_allows_errors_to_stderr()` added and passing
- [ ] Test `test_suppress_errors_blocks_stderr()` added and passing
- [ ] Test `test_no_logging_suppresses_non_errors()` added and passing
- [ ] Manual verification: errors appear on stderr with `--no-logging` flag
- [ ] Manual verification: errors appear on stderr with `--silent` flag
- [ ] Manual verification: no errors appear with `--suppress-errors` flag
- [ ] Manual verification: non-error messages suppressed with `--no-logging` flag
- [ ] All existing tests still passing
- [ ] Overall test coverage remains above 80%
- [ ] Issue #37 closed with reference to implementation

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

### Bug Fixes

- **Logging:** Fixed `--no-logging` and `--silent` modes to allow ERROR and CRITICAL messages to stderr as documented. Previously, these modes suppressed all output including errors, contradicting the documented behavior.

[↑ Back to top](#table-of-contents)
