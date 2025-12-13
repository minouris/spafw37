## Switch Param Grouped Behaviour Flow

This section illustrates how switch param conflict handling changes with the new `PARAM_SWITCH_CHANGE_BEHAVIOR` property.

### Current Behaviour (Before Changes)

In the current implementation, both CLI and programmatic usage follow identical paths through `set_param()`, which calls `_validate_xor_conflicts()` to detect conflicts. When a conflict is detected (a switch param in the same group is already set), `_validate_xor_conflicts()` raises a `ValueError` immediately, with no mechanism to configure alternative behaviour.

**CLI usage:**
1. **User runs:** `app --mode-read --mode-write`
2. **CLI → _parse_command_line()**: Receives tokenized params
3. **_parse_command_line()**: Loops through params
4. **_parse_command_line() → param.set_param('mode_read', True)**: Sets first param
   - **set_param() → _validate_xor_conflicts()**: Checks for conflicts
   - **set_param() → config**: Sets `mode_read=True`
5. **_parse_command_line() → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _validate_xor_conflicts()**: Finds conflict
   - **_validate_xor_conflicts()**: Raises `ValueError`
   - **Error propagates**: set_param() → _parse_command_line() → CLI

**Programmatic usage:**
1. **Application → param.set_param('mode_read', True)**: Sets first param
2. **Application → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _validate_xor_conflicts()**: Finds conflict
   - **Raises `ValueError`**

**Result:** Always raises error. No way to configure different behaviour.

### New Behaviour (After Changes)

With `PARAM_SWITCH_CHANGE_BEHAVIOR` property, three behaviour options are available:

#### SWITCH_REJECT (default - backward compatible)

With `SWITCH_REJECT` behaviour, the system maintains backward compatibility by raising errors on conflicts, but the implementation path changes. CLI parsing uses a new `param.set_values()` function that enables batch mode, which forces `SWITCH_REJECT` regardless of configuration. The conflict detection logic moves to the renamed `_handle_switch_group_behavior()`.

**CLI usage:**
1. **User runs:** `app --mode-read --mode-write`
2. **CLI → _parse_command_line()**: Receives tokenized params
3. **_parse_command_line() → param.set_values()**: Calls with parsed list
4. **param.set_values()**: Enables batch mode (`_set_batch_mode(True)`)
5. **param.set_values() → param.set_param('mode_read', True)**: Sets first param
6. **param.set_values() → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (forced by batch mode)
   - **Raises `ValueError`**
7. **param.set_values()**: Disables batch mode in finally block

**Programmatic usage:**
1. **Application → param.set_param('mode_read', True)**: Sets first param
2. **Application → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_get_switch_change_behavior()**: Returns `SWITCH_REJECT` (from config)
   - **Raises `ValueError`**

**Result:** CLI forces SWITCH_REJECT via batch mode; programmatic uses configured behaviour (defaults to SWITCH_REJECT).

#### SWITCH_UNSET (new option)

With `SWITCH_UNSET` configured, programmatic usage exhibits automatic conflict resolution by calling `unset_param()` on conflicting switches. However, CLI usage ignores this configuration due to batch mode forcing `SWITCH_REJECT`.

**CLI usage:**
1. **User runs:** `app --mode-read --mode-write`
2. **[Same flow as SWITCH_REJECT - batch mode overrides to REJECT]**
3. **Result:** Error raised

**Programmatic usage:**
1. **Application → param.set_param('mode_read', True)**: Sets first param
2. **Application → param.set_param('mode_write', True)**: Sets second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_get_switch_change_behavior()**: Returns `SWITCH_UNSET` (batch mode disabled)
   - **_handle_switch_group_behavior()**: Calls `unset_param('mode_read')`
   - **set_param() → config**: Sets `mode_write=True`

**Result:** CLI raises error. Programmatic usage: `mode_read` removed, `mode_write` set to True.

**Key architectural changes:**

1. **CLI parser refactored**: `_parse_command_line()` calls new `param.set_values()` instead of looping
2. **Batch mode introduced**: `_batch_mode` flag forces `SWITCH_REJECT` during CLI parsing
3. **Behaviour abstraction**: `_get_switch_change_behavior()` respects config in programmatic usage but overrides when batch mode enabled
4. **Validation renamed**: `_validate_xor_conflicts()` → `_handle_switch_group_behavior()`
````

[↑ Back to top](#table-of-contents)

### Fixing Regressions Section

**When to include:** After core implementation (Steps 1-N) is complete and testing reveals issues requiring fixes. Omit if all tests pass after core implementation.

**Position in document:** After Further Considerations, before Success Criteria.

**Purpose:** Document fixes for bugs or incorrect behavior discovered during post-implementation testing, separate from the planned implementation steps.

**Structure:**

Each regression fix should be documented as a numbered step continuing from the last implementation step (N+1, N+2, etc.). Use ✅ COMPLETE marker when implemented. Each step should include numbered code blocks matching the hierarchical numbering system, and for test updates, use OLD/NEW Gherkin scenarios to document expected behavior changes.

See template at `.github/instructions/templates/ISSUE-PLAN.md` for complete examples.

[↑ Back to top](#table-of-contents)

### Implementation Plan Changes Section

**When to include:** When the plan evolves during implementation. Omit if implementation follows the original plan exactly.

**Position in document:** After Success Criteria, before CHANGES section.

**Purpose:** Provide transparency about how the implementation process evolved, what was discovered during testing, and why additional steps were needed.

**Structure:**

1. **Post-Implementation Analysis:** List test failures or issues discovered, categorize by type
2. **Additional Implementation Steps:** List additional steps added (N+1, N+2) with brief descriptions
3. **Additional Considerations:** List considerations documented post-implementation with resolution status
4. **Timeline:** Chronological summary including core implementation, additional steps, final results

See template at `.github/instructions/templates/ISSUE-PLAN.md` for complete example.

[↑ Back to top](#table-of-contents)

### Status Tracking in Steps

**When to use:** Mark steps as complete when implemented to provide clear progress tracking.

**Format:** Add ✅ COMPLETE marker to step title and include brief status line.

**Example:**

```markdown
### 7. Fix _has_switch_conflict() for mixed-type switch groups ✅ COMPLETE

**Status:** COMPLETE - All 4 logging tests now pass
```

[↑ Back to top](#table-of-contents)

### Enhanced CHANGES Section Documentation

**Migration notes for behavior changes:**

When implementation includes behavior changes that might affect existing code, add explicit warnings with concrete examples of what changed and what users need to update.

**Detailed testing documentation:**

The Testing subsection should include:
- Count and location of new tests
- Count and list of updated tests with specific descriptions
- Comprehensive coverage list (what aspects are tested)
- Final test results (passed count, skipped count, coverage percentage)

**Bug fix documentation:**

When regression fixes include actual bug fixes (not just behavior changes), document them explicitly in the Changes section with technical details about what was wrong and what's now correct.

See template at `.github/instructions/templates/ISSUE-PLAN.md` for complete examples.

[↑ Back to top](#table-of-contents)

### Documentation Update Section

**When to include:** For all issues that add or change user-facing functionality.

**Position in document:** After all implementation steps, before "Further Considerations".

**Purpose:** Specify exactly what documentation files need updates and what content to add.

**Structure:**

1. **Main section heading:** Use "X. Update documentation" where X is the step number
2. **Brief intro paragraph:** Summarize what documentation updates are needed and version
3. **Horizontal rule:** `---` to separate intro from subsections
4. **Subsections (X.1, X.2, etc.):** One per documentation file to update
   - Use `####` heading level (e.g., `#### 6.1. Update parameters.md`)
   - **File:** field specifying the file path
   - Description of what to add/change
   - **Location:** (optional) where in the file to add content
   - **Content to add:** or **Updates required:** with full markdown content blocks
   - **Tests:** Concise format "Manual review to verify [aspect]"
5. **Back to top link** at end of main section

**Documentation subsection format:**

Each subsection should include:
- **File:** path to documentation file
- Description paragraph explaining the update
- **Location:** (optional) where to place new content
- **Content to add:** for single additions with full markdown wrapped in ````markdown syntax, or
- **Updates required:** for multiple specific changes (numbered list) with markdown snippets
- **Tests:** Manual review description

**Test format for documentation:**

Documentation tests use a concise, single-line format:
```markdown
**Tests:** Manual review to verify documentation clarity and accuracy
**Tests:** Manual review to verify documentation completeness and accuracy
**Tests:** Manual review to verify README clarity and consistency
```

Do NOT use Gherkin format for documentation tests. Documentation tests are manual reviews focused on quality aspects (clarity, accuracy, completeness, consistency).

**Example structure:**

````markdown
### 6. Update documentation

Update user-facing documentation to describe the new functionality. 
Add version notes to indicate this was added in v1.1.0.

---

#### 6.1. Update parameters.md

**File:** `doc/parameters.md`

Add new section "Feature Name" after "Related Section" section. 
This section documents the new functionality, provides code examples, 
and includes version note.

**Location:** After "Related Section" section

**Content to add:**

````markdown