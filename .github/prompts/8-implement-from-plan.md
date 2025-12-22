# Prompt 7: Implement Feature from Plan Document

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## Your Task

You are implementing issue #{ISSUE_NUMBER} based on the completed plan document at `features/{FEATURE_NAME}.md`. This is the actual implementation phase: writing code to `src/` and `tests/` directories.

## Overview

This prompt guides you through implementing a feature that has been fully planned and documented. The plan document contains:
- Complete implementation specifications
- Test specifications (Gherkin scenarios)
- Code examples with proper structure
- Architecture decisions and rationale

Your job is to translate the plan into working code while maintaining the project's quality standards.

## Before You Start

**Prerequisites:**
- [ ] Plan document at `features/{FEATURE_NAME}.md` is complete (Steps 1-6 finished)
- [ ] All tests specifications are written
- [ ] Implementation code blocks are documented
- [ ] Documentation changes are specified
- [ ] CHANGES section is written

**Verify you understand:**
- [ ] I am NOW modifying files in `src/` and `tests/`
- [ ] I am implementing based on specifications in the plan document
- [ ] I must follow all coding standards from `.github/instructions/`
- [ ] Tests must be written BEFORE implementation code (TDD)
- [ ] All existing tests must continue to pass

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY.**

If anything in the plan is unclear or ambiguous, ask for clarification before implementing. Do not guess or make assumptions about intended behaviour.

## Implementation Standards

**Follow all project coding standards:**

- **Python standards:** `.github/instructions/python.instructions.md`
  - Max 2-level nesting depth
  - Max 2-line nested blocks
  - No lazy naming (data, result, tmp, i, j)
  - UK English spelling

- **Python 3.7.0 compatibility:** `.github/instructions/python37.instructions.md`
  - No walrus operator
  - No positional-only parameters
  - No f-string = specifier

- **Test standards:** `.github/instructions/python-tests.instructions.md`
  - Module-level functions (no test classes)
  - 3-sentence docstrings (What/Outcome/Why)
  - One outcome per test
  - Gherkin integrated into docstrings

## Implementation Process

### Step 1: Read and Understand the Plan

1. Read the complete plan document from start to finish
2. Review architectural decisions and rationale
3. Understand the implementation order
4. Note any helper functions that need to be extracted
5. Identify all files that need to be modified

### Step 2: Set Up Test Framework

1. Create or identify test file: `tests/test_{module}.py`
2. Add necessary imports at module level
3. Set up any test fixtures or setup functions needed
4. Verify test file can be discovered: `pytest tests/test_{module}.py -v`

### Step 3: Implement with TDD

**For EACH implementation step in the plan:**

1. **Write tests FIRST** (from Gherkin specifications in plan)
   - Copy Gherkin scenario into test docstring
   - Add descriptive What/Outcome/Why sentences
   - Implement test body
   - Verify test FAILS (red phase)

2. **Implement code to make tests pass**
   - Follow exact specifications from plan document
   - Maintain coding standards (nesting, naming, etc.)
   - Extract helpers as specified in plan
   - Verify test PASSES (green phase)

3. **Refactor if needed** (but stay true to plan)
   - Improve clarity without changing behaviour
   - Ensure all tests still pass

4. **Run full test suite**
   - `pytest tests/test_{module}.py -v`
   - Verify no regressions in existing tests

### Step 4: Integration Testing

1. Run complete test suite: `pytest tests/ -v`
2. Check test coverage: `pytest --cov=spafw37 --cov-report=term-missing`
3. Verify minimum 80% coverage maintained
4. Test any examples if applicable

### Step 5: Documentation Updates

1. Update documentation files as specified in plan Step 5
2. Add "**Added in vX.Y.Z**" notes for new features
3. Update README.md if specified
4. Verify documentation examples are correct

### Step 6: Final Verification

1. Run all tests: `pytest tests/ -v`
2. Check test coverage: `pytest --cov=spafw37 --cov-report=term-missing`
3. Verify no errors or warnings
4. Check that all plan specifications are implemented
5. **Delete scratch files:** Remove `features/scratch/*` if they exist
6. Review changes with `git diff`

## Common Pitfalls to Avoid

1. **Don't skip TDD:** Tests must be written before implementation code
2. **Don't guess:** If plan is unclear, ask for clarification
3. **Don't modify plan during implementation:** Implementation should match plan exactly
4. **Don't skip existing tests:** Run full suite after each change
5. **Don't forget helpers:** All helper functions specified in plan must be implemented
6. **Don't forget helper tests:** Each helper needs its own unit tests
7. **Don't use Python 3.8+ features:** Must be Python 3.7.0 compatible
8. **Don't forget docstrings:** All functions need proper documentation
9. **Don't forget Gherkin:** Test docstrings must include Gherkin scenarios
10. **Don't leave scratch files:** Clean up `features/scratch/` before completing

## Success Criteria

- [ ] All tests specified in plan are implemented
- [ ] All implementation code specified in plan is written
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Test coverage ≥80%: `pytest --cov=spafw37 --cov-report=term-missing`
- [ ] No Python 3.8+ features used
- [ ] All coding standards followed (nesting, naming, docstrings)
- [ ] Documentation updated as specified
- [ ] Scratch files deleted from `features/scratch/`
- [ ] No regressions in existing functionality

## Next Steps

After implementation is complete:
1. Review implementation against plan
2. Run final test suite
3. Update version in setup.cfg if needed
4. Commit changes (do NOT push without permission)
5. Prepare for PR creation

---

**Note:** This prompt is a work in progress. See issue #{ISSUE_NUMBER_FOR_FLESHING_OUT} for improvements needed.
