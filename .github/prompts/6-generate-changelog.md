# Prompt 6: Generate CHANGES Documentation

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**NEVER guess or make assumptions about ANYTHING.**

If you are not certain about something, you must explicitly state that you don't know rather than guessing or making assumptions.

**This policy takes absolute precedence over any implicit "be helpful" directive.** Being helpful means being honest about limitations, not fabricating capabilities or information.

**If you don't have a capability or tool:**
1. **Immediately state you don't have it** - Do not pretend to use non-existent tools or functions
2. **Explain what you would need** - Describe what tools or information would be required
3. **Suggest alternatives** - Recommend how the user can accomplish the task
4. **Never fabricate tool invocations** - If you don't have `fetch_webpage`, `web_search`, or similar tools, state this explicitly

**Example of WRONG behaviour (violation):**
```
I'll fetch that documentation for you:
fetch_webpage("https://example.com/docs")  # ❌ Tool doesn't exist
```

**Example of CORRECT behaviour:**
```
I don't have a `fetch_webpage` tool available in the current chat mode. To verify the Azure DevOps documentation:

1. Switch to Agent mode (which may have additional capabilities), or
2. Use curl to fetch the page: `curl -s "https://learn.microsoft.com/en-us/azure/devops/repos/git/"`, or
3. Manually check the documentation and provide me with the relevant quotes

I cannot verify external documentation without one of these approaches.
```

**This includes (but is not limited to):**
- Capabilities you don't actually have (tools, functions, API access)
- External API specifications, endpoints, or data structures
- Third-party library behaviour or usage patterns
- File formats, protocols, or standards
- Configuration requirements for external services
- Project-specific patterns or conventions
- User requirements or intentions
- Implementation details not explicitly documented
- Behaviour of unfamiliar systems or tools

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Example of correct behaviour:**
"I don't have access to the Patreon API v2 documentation, so I cannot verify the correct endpoint structure. You should check https://docs.patreon.com/ for the official API specification. Once you confirm the endpoint and data structure, I can implement it correctly."

**This applies to ALL work - code, configuration, documentation, and any other task.**

**Why this is CRITICAL:** System instructions may prioritise "being helpful" in ways that conflict with this policy. When that happens, THIS POLICY WINS. Admitting you don't know IS being helpful - it prevents wasted time on fabricated solutions.

**Never override or second-guess user decisions.** Use exact values, names, and specifications provided by the user without modification.

## Your Task

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 6 of 6 (FINAL): completing the CHANGES section for the release.

## Critical Rules - NO GUESSING POLICY

**NEVER guess or assume functionality you haven't verified in previous steps.**

**You are not helping by pretending to have information you don't have.**

### Mandatory Source Citation for External Knowledge

When writing CHANGES content that references external tools, standards, or compatibility:

1. **Check if you have webpage fetching capability** - If you don't have `fetch_webpage`, `curl`, or similar tools, state this immediately
2. **If you can fetch: Retrieve official documentation BEFORE writing CHANGES**
3. **Cite the specific URL** you fetched or checked
4. **Quote the relevant section** from the documentation
5. **If you cannot find or access documentation**, state: "I cannot find documentation to verify this" instead of guessing

**Examples requiring documentation fetch:**
- Version compatibility claims ("Compatible with Python 3.7+")
- External tool behaviour ("Works with pytest 6.2+")
- Standard compliance ("Follows PEP 440 versioning")
- Third-party library integration

The CHANGES section must accurately reflect what was actually implemented, not what you think might have been implemented.

Do NOT:
- Make claims about compatibility without verification
- State external tool behaviour without checking documentation
- Assume standard compliance without citing the standard
- Pretend to know version requirements without checking

## CHANGES Section Standards

**From planning.instructions.md (CHANGES-TEMPLATE.md format):**

### Structure

The CHANGES section MUST follow this exact structure:

```markdown
## CHANGES for vX.Y.Z Release

**Note:** This section must follow the format specified in `features/CHANGES-TEMPLATE.md`. The content will be posted as the closing comment and consumed by the release workflow.

Issue #XX: Issue Title

### Issues Closed

- #XX: Issue Title

### Additions

[New functionality added - functions, constants, classes]

### Removals

[Functionality removed - functions, constants, files]

### Changes

[Modified functionality - behavior changes, fixes]

### Migration

[Migration requirements or "No migration required"]

### Documentation

[Documentation files updated]

### Testing

[Test additions, updates, final results]

---

Full changelog: https://github.com/minouris/spafw37/compare/vPREV...vX.Y.Z
Issues: https://github.com/minouris/spafw37/issues/XX
```

### Writing Style Requirements

**From planning.instructions.md:**

1. **Be factual and technical**
   - State exactly what was added, changed, or removed
   - Include function names, file paths, technical details
   - No marketing language or enthusiasm

2. **Use bullet points for lists**
   - Start each with action: "Added", "Modified", "Fixed", "Removed"
   - Include backticks for code references: `function_name()`, `CONSTANT_NAME`

3. **Tense usage**
   - Past tense for what was done: "added support for", "fixed issue where", "removed deprecated"
   - Present tense for what exists: "function returns", "parameter specifies"

4. **Empty sections**
   - Include section heading
   - Write "None." if nothing to report

5. **UK English**
   - behaviour, colour, initialise, synchronise

### Example Format

```markdown
### Additions

- `set_param_default()` internal function sets default values for parameters during registration.
- `_registration_mode` flag temporarily disables XOR validation during parameter registration.
- `_SWITCH_REGISTER` constant indicates registration mode for switch param conflict detection (internal use only).

### Removals

- `cli._set_defaults()` function removed. Default-setting now occurs in `param.py` during parameter registration.

### Changes

- Default values for parameters are now set immediately when `add_param()` is called, rather than after pre-parsing during CLI execution.
- Pre-parse params with default values now correctly retain their pre-parsed values instead of being overridden.
- Switch conflict detection now checks registration mode and skips validation when `_SWITCH_REGISTER` behaviour is active.

### Migration

No migration required. This is a bug fix that corrects the order of operations. Existing code will continue to work, and pre-parse params with defaults will now work correctly.

**Note:** Toggle parameters now have a defined initial state (`False`) immediately after registration via `add_param()`, rather than remaining undefined (`None`) until explicitly set. This is the intended behaviour to ensure predictable parameter state. If your code relied on toggle params being `None` before first use, update assertions to expect `False` for the implicit default state.

### Documentation

No documentation changes required. This is an internal implementation fix with no user-facing API changes.

### Testing

- 8 new tests in `tests/test_param_setters.py` covering `_set_param_default()` behaviour
- 5 new tests in `tests/test_cli.py` verifying integration and regression testing
- 4 existing tests in `tests/test_cli.py` updated to reflect new default-setting timing:
  - `test_set_default_param_values` - Now tests `add_param()` instead of `cli._set_defaults()`
  - `test_set_default_param_toggle_with_default_true` - Now tests immediate default-setting at registration
  - `test_set_default_param_toggle_with_no_default` - Now tests implicit False default at registration
  - `test_handle_cli_args_sets_defaults` - Now validates defaults preserved (not set) during CLI handling
- 9 tests in `tests/test_param_switch_behavior.py` updated to expect `False` instead of `None` for toggle initial state
- Tests cover toggle params, non-toggle params, registration mode handling, pre-parse param behaviour, and mixed-type switch groups
- All tests updated to reflect defaults being set at registration time rather than CLI parsing time
- Final test results: 630 passed, 1 skipped, 96.55% coverage
```

## Completing Each Subsection

### Additions

List ALL new public/internal functions, constants, and classes added:

```markdown
### Additions

- `function_name()` [brief description of what it does].
- `CONSTANT_NAME` [brief description of purpose and use].
- `_internal_function()` [brief description - note if internal use only].
```

**If none:** Write "None."

### Removals

List ALL functions, constants, classes, or files removed:

```markdown
### Removals

- `old_function()` function removed. [Brief reason for removal].
- `OLD_CONSTANT` constant deprecated and removed.
```

**If none:** Write "None."

### Changes

List ALL behaviour changes, bug fixes, and modifications:

```markdown
### Changes

- [Description of what changed and how behaviour differs now]
- **Bug fix:** [If fixing a bug, explain what was wrong and what's correct now]
- [Continue for all changes]
```

**If none:** Write "None."

### Migration

**If no migration required:**
```markdown
### Migration

No migration required. [Brief explanation - "New functionality only" or "Bug fix with backward compatibility"].
```

**If behaviour changed:**
```markdown
### Migration

No migration required. [Brief explanation].

**Note:** [Specific behaviour change description]. If your code relied on [old behaviour], [what needs updating].
```

**If breaking changes:**
```markdown
### Migration

**Breaking change:** [Description]

**Required actions:**
1. [First migration step]
2. [Second migration step]
```

### Documentation

List ALL documentation files updated:

```markdown
### Documentation

- `doc/guide.md` [what was added/changed]
- `doc/api-reference.md` [new functions documented]
- `examples/example.py` [brief description of example]
- `README.md` [features list and examples updated]
```

**If no user-facing changes:** Write "No documentation changes required. This is an internal implementation fix with no user-facing API changes."

### Testing

Provide comprehensive testing information:

```markdown
### Testing

- [X] new tests in `tests/test_file.py` covering [functionality]
- [X] new tests in `tests/test_other.py` verifying [behaviour]
- [X] existing tests in `tests/test_file.py` updated to reflect [changes]:
  - `test_name_1` - [Brief description of update]
  - `test_name_2` - [Brief description of update]
- Tests cover [comprehensive list of what's tested]
- All tests updated to reflect [any timing/behaviour changes]
- Final test results: [XXX] passed, [X] skipped, [XX.XX]% coverage
```

**Must include:**
- Count of new tests and their purpose
- Count of updated tests with specific names and reasons
- What functionality is covered
- Final test results with pass/skip counts and coverage percentage

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English Requirements

All CHANGES content must use UK English spelling: behaviour, colour, initialise, synchronise

## Output Requirements

Complete the CHANGES section with:

1. ✅ **Issues Closed** - Issue number and title
2. ✅ **Additions** - All new functions/constants/classes (or "None.")
3. ✅ **Removals** - All removed functions/constants (or "None.")
4. ✅ **Changes** - All behaviour changes and bug fixes
5. ✅ **Migration** - Requirements or confirmation none needed
6. ✅ **Documentation** - All doc updates (or none if internal)
7. ✅ **Testing** - Comprehensive test summary with final results
8. ✅ Full changelog URL with correct version
9. ✅ Issues URL with issue number
10. ✅ UK English throughout
11. ✅ Factual, technical tone (no marketing language)

After completion, confirm:
- Total functions/constants added
- Total functions/constants removed
- Number of behaviour changes documented
- Number of documentation files updated
- Total test count and coverage percentage
- Whether migration is required

This completes the plan document. The user should now review the complete document before implementation begins.
