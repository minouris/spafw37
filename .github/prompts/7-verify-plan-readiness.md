# Prompt 7: Verify Plan Readiness for Implementation

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY.**

Key reminder: NEVER guess about compliance or standards. Verify against actual instruction files.

## Your Task

You are verifying the plan document at `features/{FEATURE_NAME}.md` for issue #{ISSUE_NUMBER}. This is step 7 of 8: verifying the plan is complete and ready for implementation.

**This step performs a comprehensive review before implementation begins.**

## What This Step Does

This prompt verifies that:
1. All required sections are complete (no placeholders)
2. All code blocks follow project standards
3. Planning Checklist accurately reflects document state
4. Plan is ready for Step 8 (actual implementation)

**This is the final quality gate before writing production code.**

## Step 7.1: Verify Section Completeness

Check that all required sections have content (no `[PLACEHOLDER]` markers):

**Required sections:**
- [ ] Overview - Complete with architectural decisions
- [ ] Implementation Steps - All steps with detailed code blocks
- [ ] Further Considerations - All marked RESOLVED or addressed
- [ ] Success Criteria - Feature outcomes defined
- [ ] Planning Checklist - Completed with checkmarks
- [ ] Implementation Checklist - Complete TDD workflow
- [ ] CHANGES - Release notes populated

**Search for placeholders:**
```bash
grep -n "PLACEHOLDER" features/{FEATURE_NAME}.md
```

If any placeholders remain, note which sections need completion.

## Step 7.2: Verify Code Standards Compliance

Review all code blocks in the plan against mandatory standards.

**CRITICAL: Read these instruction files BEFORE verifying:**
- `.github/instructions/code-review-checklist.instructions.md` - Mandatory checklist
- `.github/instructions/python.instructions.md` - Python standards
- `.github/instructions/python37.instructions.md` - Python 3.7 compatibility
- `.github/instructions/python-tests.instructions.md` - Test standards
- `.github/instructions/plan-structure.instructions.md` - Plan structure rules

### Verification Checklist

For EVERY code block in the plan, verify:

**Import Rules:**
- [ ] NO inline imports inside functions
- [ ] ALL imports at module/file level (shown in "Module-level imports" section)
- [ ] NO `from module import *` (explicit imports only)

**Nesting Rules:**
- [ ] NO code nested more than 2 levels below function declaration
- [ ] NO nested blocks (if/for/while/with/try) exceeding 2 lines
- [ ] Helpers extracted where nesting violations would occur

**Naming Rules:**
- [ ] NO single-letter variables (use descriptive names)
- [ ] NO lazy names (`tmp`, `data`, `result`, `val`, `i`, `j`)
- [ ] ALL names are descriptive full words
- [ ] Constants in UPPER_SNAKE_CASE

**Python 3.7 Compatibility:**
- [ ] NO walrus operator (`:=`)
- [ ] NO positional-only parameters (`/` separator)
- [ ] NO f-string `=` specifier
- [ ] NO type hints (project policy)

**Plan Structure:**
- [ ] Block numbering follows X.Y.Z format
- [ ] Each function in separate code block
- [ ] Each function immediately followed by its tests
- [ ] Gherkin tests separate from Python implementation
- [ ] Module-level imports consolidated in Step 1

**Test Structure:**
- [ ] Test functions are module-level (NOT in classes)
- [ ] Test docstrings have 3+ sentences (What/Outcome/Why)
- [ ] One outcome per test function
- [ ] Test names describe behaviour being tested

**Documentation:**
- [ ] All public functions have comprehensive docstrings
- [ ] All private functions have minimum one-line docstrings
- [ ] UK English spelling (behaviour, colour, organise)

## Step 7.3: Verify Test Coverage

Check that all implementation has corresponding tests:

**For each function in implementation:**
- [ ] Has at least one test function
- [ ] Edge cases have dedicated tests
- [ ] Error cases have dedicated tests
- [ ] Regression tests for modified functions

**Count verification:**
```bash
# Count implementation functions (exclude imports, constants)
grep -E "^def " features/{FEATURE_NAME}.md | grep -v "test_" | wc -l

# Count test functions
grep -E "^def test_" features/{FEATURE_NAME}.md | wc -l
```

Test count should be ≥ implementation function count (typically 2-3 tests per function).

## Step 7.4: Update Planning Checklist

Based on your verification, update the Planning Checklist section in the plan document.

**Mark items as complete (✅) or incomplete (❌):**

```markdown
## Planning Checklist

This checklist tracks completion of this planning document.

**Plan Structure:**
- [x] Overview section complete with architectural decisions
- [x] All implementation steps identified and outlined
- [x] Further Considerations documented (all marked RESOLVED)
- [x] Success Criteria defined (feature outcomes)
- [x] Implementation Checklist created (TDD workflow)
- [x] CHANGES section populated for release
- [x] Table of Contents updated to reflect all sections

**Implementation Details:**
- [x] All implementation steps have detailed code blocks
- [x] All functions have corresponding test specifications
- [x] All code blocks follow X.Y.Z numbering scheme
- [x] All tests written in Gherkin + Python format
- [x] Module-level imports consolidated in Step 1
- [x] No nesting violations (max 2 levels)
- [x] No nested blocks exceeding 2 lines
- [x] All helper functions extracted and documented

**Documentation:**
- [x] All affected documentation files identified
- [x] Example files planned (if needed)
- [x] API reference updates planned (if needed)
- [x] User guide updates planned (if needed)

**Quality Verification:**
- [x] All code follows Python 3.7.0 compatibility requirements
- [x] All code follows UK English spelling conventions
- [x] No lazy naming (tmp, data, result, i, j, etc.)
- [x] All functions have proper docstrings
- [x] Regression tests planned for modified functions

**Ready for Implementation:**
- [x] Plan reviewed and approved
- [x] All Further Considerations resolved
- [x] Success Criteria agreed upon
- [x] Implementation Checklist ready to execute
```

**If any items are incomplete, mark with ❌ and explain what needs fixing.**

## Step 7.5: Generate Readiness Report

Create a comprehensive readiness report for the user.

### If Plan is READY:

```markdown
## ✅ Plan Ready for Implementation

This plan meets all requirements and is ready for Step 8 (implementation).

**Verification Summary:**
- ✅ All sections complete (no placeholders)
- ✅ {N} code blocks verified against standards
- ✅ {M} implementation functions with {K} tests ({K/M} ratio)
- ✅ All code follows Python 3.7 compatibility
- ✅ All code follows nesting rules (max 2 levels)
- ✅ All code follows naming standards
- ✅ All tests follow proper structure
- ✅ Planning Checklist complete

**Next Step:**
Ready to proceed with Step 8: "Implement issue #{NUMBER} from the plan"
```

### If Plan is NOT READY:

```markdown
## ⚠️ Plan Not Ready for Implementation

This plan has issues that must be resolved before implementation.

**Issues Found:**

### Section Completeness
- ❌ {Section name} still contains placeholder
- ❌ {Section name} missing required content

### Code Standards Violations
- ❌ {Location}: Inline import inside function (violates import rules)
- ❌ {Location}: 3-level nesting detected (max 2 levels allowed)
- ❌ {Location}: Nested block exceeds 2 lines (extract helper)
- ❌ {Location}: Lazy variable name `{name}` (use descriptive name)
- ❌ {Location}: Using Python 3.8+ feature `{feature}` (Python 3.7 required)

### Test Coverage Gaps
- ❌ Function `{name}` has no tests
- ❌ Edge case for `{scenario}` not tested
- ❌ Error case for `{scenario}` not tested

### Planning Checklist
- ❌ {N} items marked incomplete (see Planning Checklist)

**Required Actions:**
1. Fix all code standards violations listed above
2. Add missing test coverage
3. Complete all placeholder sections
4. Update Planning Checklist
5. Re-run Step 7 to verify fixes

**Do NOT proceed to Step 8 until all issues are resolved.**
```

## Critical Verification Patterns

### Detecting Nesting Violations

Look for code blocks with excessive indentation:

```python
# ❌ VIOLATION - 3 levels of nesting
def function():
    if condition:           # Level 1
        for item in items:  # Level 2
            if check:       # Level 3 - TOO DEEP
                process()

# ✅ CORRECT - Extract helper
def function():
    if condition:           # Level 1
        _process_items(items)  # Level 2 (helper call)

def _process_items(items):
    for item in items:      # Level 1 (in helper)
        if check:           # Level 2
            process()
```

### Detecting Inline Imports

Search for import statements inside functions:

```python
# ❌ VIOLATION
def test_something():
    from spafw37 import param  # WRONG - inline import
    
# ✅ CORRECT
# Module-level imports shown at start of file
from spafw37 import param

def test_something():
    param.add_param({})  # Uses already-imported module
```

### Detecting Lazy Naming

Look for prohibited variable names:

```python
# ❌ VIOLATIONS
tmp = get_value()
data = process()
i = 0
result = calculate()

# ✅ CORRECT
parameter_value = get_value()
processed_commands = process()
command_index = 0
validation_outcome = calculate()
```

## Output Requirements

After completing verification, provide:

1. **Readiness verdict:** READY or NOT READY
2. **Statistics:** 
   - Number of code blocks verified
   - Number of functions vs tests
   - Number of violations found (if any)
3. **Updated Planning Checklist** in the plan document
4. **Detailed report** as specified above
5. **Next steps** - Either proceed to Step 8 or list required fixes

## When Plan is NOT Ready

**DO NOT proceed to Step 8 if issues are found.**

Instead:
1. Clearly list ALL violations and gaps
2. Provide specific locations (line numbers or block IDs)
3. Show examples of corrections needed
4. Update Planning Checklist with ❌ for incomplete items
5. Instruct user to fix issues and re-run Step 7

## When Plan is READY

**Confirm readiness and notify user:**

```
✅ Plan verification complete. All standards met.

This plan is ready for Step 8 implementation.

Statistics:
- 42 code blocks verified
- 9 implementation functions with 24 tests (2.7 tests per function)
- 0 standards violations
- 0 placeholders remaining
- Planning Checklist: 28/28 items complete

Next step: "Implement issue #{NUMBER} from the plan"
```

## UK English Requirements

All comments and output must use UK English spelling: behaviour, organise, colour, centre, etc.
