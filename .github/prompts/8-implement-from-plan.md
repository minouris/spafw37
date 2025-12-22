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

**MANDATORY: Step 7 Verification Must Be Complete**

Before proceeding with implementation, Step 7 (Verify Plan Readiness) MUST have been executed and ALL criteria satisfied:

- [ ] Step 7 verification has been run on the plan document
- [ ] All Planning Checklist items marked with ✅ (no ❌ or [ ] remaining)
- [ ] Final readiness report shows "✅ Plan Ready for Implementation"
- [ ] Zero critical violations reported
- [ ] All minor issues resolved (if any were identified)

**If Step 7 has not been completed or any criteria are not satisfied, STOP and complete Step 7 first.**

**Additional Prerequisites:**
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

**When decisions are required:**
- **DO NOT decide for yourself** - Always consult the user
- If the plan doesn't specify an implementation detail, ask the user
- If multiple approaches are possible, present options and ask the user to choose
- If you encounter unexpected behaviour, ask the user before proceeding
- If a test appears wrong but you're not certain, ask the user before modifying it

**Examples requiring user consultation:**
- Plan says "validate input" but doesn't specify validation logic
- Multiple ways to implement a feature, all technically valid
- Test fails but you can't determine if test or implementation is wrong
- Error occurs that might require deviating from the plan
- Ambiguity in Gherkin scenario or code specification

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

### Step 1: Extract Implementation Checklist

1. **Extract checklist from plan document** to workspace **verbatim**:
   - Locate the "## Implementation Checklist" section in the plan
   - Copy it EXACTLY as written - no extra headings, no instructions, no modifications
   - This is a source file you'll work from, not an instruction document
   
2. Create `features/scratch/issue-{NUMBER}/implementation-checklist.md`

3. Paste the complete Implementation Checklist section verbatim

4. This file will be your step-by-step execution guide that you'll update as you work

### Step 2: Create Implementation Workspace

1. **Create workspace folder** for implementation artifacts:
   ```bash
   mkdir -p features/scratch/issue-{NUMBER}
   ```
   This folder will contain all temporary files created during implementation, isolated from the main plan document.

2. **Create implementation log** at `features/scratch/issue-{NUMBER}/implementation-log.md`:
   - Record any errors encountered during implementation
   - Document deviations from plan (if any)
   - Track unexpected issues and their resolutions
   - Note: This log is for tracking problems, NOT for changing the plan

3. **Optional: Create agent tracking** (if you have manage_todo_list or similar tools):
   - Break the Implementation Checklist into logical chunks (e.g., by step number)
   - Create tracking items for each major section (Step 1, Step 2, etc.)
   - Mark items as in-progress/completed as you work
   - This supplements, not replaces, the Implementation Checklist

### Step 3: Extract Plan Sections to Workspace

**CRITICAL: Extract ALL major sections upfront to avoid loading the full plan repeatedly.**

The plan document can be very large (1000+ lines). To reduce context load during implementation, split it into separate workspace files before you begin coding.

1. **Identify major sections** in the plan:
   - Each implementation step (Step 1, Step 2, Step 3, etc.)
   - These sections contain the Gherkin scenarios and code blocks you'll implement
   - Look for headers like "### Step N:" in the plan

2. **Extract each section verbatim**:
   - For each step, create `features/scratch/issue-{NUMBER}/step-{N}-{short-name}.md`
   - Copy the ENTIRE section from the plan exactly as written
   - Include all subsections, code blocks, Gherkin scenarios, and explanatory text
   - No modifications, no extra headings, no instructions - verbatim copy only
   - Example: `step-2-validation-helpers.md`, `step-3-inline-params.md`

3. **Why extract upfront:**
   - Avoids reading 1000+ line plan file every time you need a code block
   - Reduces context window usage significantly
   - Speeds up agent processing time
   - Makes it easier to focus on one step at a time
   - Simplifies recomposition later (just copy files back)

4. **Working with extracted files:**
   - Reference the extracted step file when implementing that step
   - Read only the section you're currently working on
   - Do NOT modify these extracted files - they're read-only references
   - All code changes go into actual source files (src/, tests/)

### Step 4: Follow Implementation Checklist as Script

**Work through the extracted Implementation Checklist from top to bottom, line by line.**

**The Implementation Checklist IS your TODO list.** Update items in the file as you work through them.

For EACH checklist item:

1. **Mark as IN PROGRESS** in `features/scratch/issue-{NUMBER}/implementation-checklist.md` when you begin working on it:
   - Add annotation: `- [ ] **IN PROGRESS** - [Item description]`
   - This helps track interruptions
2. **Locate code blocks** in the plan (using line ranges you noted)
3. **Execute the checklist item**:
   - If it's a test: Write the test (from Gherkin + code block)
   - If it's implementation: Write the implementation code
   - If it's verification: Run tests and verify
4. **When copying code from plan to source files**:
   - **For all code**: Remove block comment annotations (e.g., `# Block 2.1.1: Add to tests/test_command.py`)
   - **For test functions**: Merge the Gherkin scenario from the plan into the test docstring
   - Copy the rest of the code exactly as written
   - These are the ONLY planned modifications when copying code
5. **Check off the item** in the checklist file when finished:
   - Change `- [ ] **IN PROGRESS**` to `- [x]` 
   - Only check off when the item is completely finished
6. **Update agent tracking** (if using manage_todo_list or similar tools)
7. **If errors occur**:
   - Add entry to implementation log with timestamp
   - Document the error, what caused it, and how you resolved it
   - **ONLY change tests if categorically wrong** (see Critical Rules below)
8. **Move to next item**

### Step 5: Critical Rules for Test Implementation

**Tests are the specification. They define correct behaviour.**

1. **Gherkin scenarios are authoritative**:
   - Test implementation MUST match its Gherkin scenario
   - If test fails, implementation is wrong (not the test)
   - Gherkin defines the contract that implementation must satisfy

2. **DO NOT modify tests to make them pass** unless:
   - The test has a clear coding error (syntax, typo in test code itself)
   - The test contradicts its own Gherkin scenario
   - You can **categorically establish** the test is wrong (not just "inconvenient")

3. **When a test fails**:
   - First assumption: Implementation is wrong
   - Check: Does implementation match plan specification?
   - Check: Does test match Gherkin scenario?
   - Only if both are mismatched should you question the test

4. **If you believe a test is wrong**:
   - Document in implementation log with full justification
   - Show contradiction between test and Gherkin
   - Get user confirmation before modifying test
   - STOP implementation until resolved

### Step 6: TDD Workflow Per Checklist Item

**For each implementation item in checklist:**

1. **Red Phase - Write failing test**:
   - Copy Gherkin from plan into test docstring
   - Implement test body per code block in plan
   - Run test: `pytest tests/test_{module}.py::test_name -v`
   - **Verify test FAILS** (if it passes, something is wrong)

2. **Green Phase - Implement code**:
   - Write implementation per code block in plan
   - Follow exact specifications and coding standards
   - Run test: `pytest tests/test_{module}.py::test_name -v`
   - **Verify test PASSES**

3. **Refactor Phase** (if needed):
   - Improve code clarity without changing behaviour
   - Keep within plan specifications
   - Re-run test to ensure still passes

4. **Integration - Run full suite**:
   - `pytest tests/test_{module}.py -v` (all tests in file)
   - Verify no regressions in existing tests
   - If regressions occur, log them and fix implementation

### Step 7: Handle Implementation Errors

**When errors occur during implementation:**

1. **Add to implementation log**:
   ```markdown
   ## Error: [Timestamp]
   **Checklist Item:** [Item description]
   **Error:** [Full error message]
   **Cause:** [Why it happened]
   **Resolution:** [How you fixed it]
   **Deviation from Plan:** [Any changes needed, or "None"]
   ```

2. **Common error categories**:
   - **Test failure**: Implementation doesn't match specification
     - Resolution: Fix implementation to match plan
   - **Import error**: Missing imports or incorrect module paths
     - Resolution: Add missing imports (module-level only)
   - **Regression**: Existing tests now fail
     - Resolution: Fix implementation to maintain backwards compatibility
   - **Test appears wrong**: Test contradicts Gherkin or plan
     - Resolution: Document in log, STOP, ask user for guidance
   - **Ambiguous specification**: Plan doesn't provide enough detail
     - Resolution: Document in log, STOP, ask user for clarification
   - **Multiple valid approaches**: More than one way to implement
     - Resolution: Document options in log, STOP, ask user to choose

3. **When to STOP and ask user**:
   - Any time you're unsure about the correct approach
   - When implementation detail is missing from plan
   - When test and implementation both seem correct but test fails
   - When error requires deviating from plan
   - When you need to make a design decision

4. **DO NOT silently change plan or tests** - log everything and consult user

### Step 8: Integration Testing

1. Run complete test suite: `pytest tests/ -v`
2. Check test coverage: `pytest --cov=spafw37 --cov-report=term-missing`
3. Verify minimum 80% coverage maintained (target 90%)
4. Test any examples if applicable

### Step 9: Documentation Updates

1. Update documentation files as specified in plan Step 5
2. Add "**Added in vX.Y.Z**" notes for new features
3. Update README.md if specified
4. Verify documentation examples are correct

### Step 10: Recompose Plan Sections

**After all implementation is complete, merge workspace files back into the plan document:**

1. **Implementation Checklist recomposition:**
   - Open updated checklist from `features/scratch/issue-{NUMBER}/implementation-checklist.md`
   - Locate "## Implementation Checklist" section in plan `features/{FEATURE_NAME}.md`
   - Replace it ENTIRELY with your updated version (all items should be `[x]`)

2. **Any other extracted sections:**
   - If you extracted other plan sections to workspace (Step 3), check if they were modified
   - Most extracted sections should be unchanged (they're reference copies)
   - If any section was updated during implementation (rare), merge those changes back
   - Usually only the Implementation Checklist will have changed

3. **Verify the recomposition:**
   - Check that all sections are accounted for
   - Ensure formatting is consistent with the rest of the plan
   - Confirm Implementation Checklist shows completion status
   - Verify no temporary workspace annotations remain

4. **This preserves the record** of implementation progress in the plan document

### Step 11: Cleanup and Final Checks

1. **Complete Implementation Checklist review**:
   - Verify all items in the recomposed checklist (now back in plan document) are checked off
   - Ensure nothing was skipped

2. **Run complete test suite**: `pytest tests/ -v`
3. **Check test coverage**: `pytest --cov=spafw37 --cov-report=term-missing`
4. **Verify minimum 80% coverage** maintained (target 90%)

5. **Review implementation log**:
   - Check `features/scratch/issue-{NUMBER}/implementation-log.md`
   - Verify all errors were resolved
   - Confirm all deviations are documented
   - Ensure no silent changes to tests

6. **Delete workspace folder**: 
   - Remove entire `features/scratch/issue-{NUMBER}/` folder
   - Checklist has been recomposed into plan, log has been reviewed
   - No need to keep temporary workspace files

7. **Review changes**: `git diff`
   - Verify all changes match plan specifications
   - Check no unintended modifications were made
   - Ensure all coding standards are met
   - Confirm Implementation Checklist in plan shows completion status

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
10. **Don't leave workspace folder:** Clean up `features/scratch/issue-{NUMBER}/` before completing
11. **Don't change tests to pass:** Only modify tests if categorically wrong
12. **Don't work out of order:** Follow Implementation Checklist top-to-bottom
13. **Don't search plan repeatedly:** Extract ALL step sections upfront (Step 3), work from extracted files
14. **Don't hide errors:** Log all issues in implementation log
15. **Don't make decisions alone:** Consult user when choices or clarifications are needed

## Success Criteria

- [ ] Workspace folder created at `features/scratch/issue-{NUMBER}/`
- [ ] Implementation Checklist extracted verbatim to workspace (this is your TODO list)
- [ ] All major step sections extracted verbatim to workspace (reduces context load)
- [ ] Implementation log created for error tracking
- [ ] All Implementation Checklist items checked off in workspace file
- [ ] All tests specified in plan are implemented
- [ ] All tests match their Gherkin scenarios exactly
- [ ] All implementation code specified in plan is written
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Test coverage ≥80%: `pytest --cov=spafw37 --cov-report=term-missing`
- [ ] No Python 3.8+ features used
- [ ] All coding standards followed (nesting, naming, docstrings)
- [ ] Documentation updated as specified
- [ ] Implementation log reviewed (all errors resolved)
- [ ] All workspace sections recomposed back into plan document with completion status
- [ ] Workspace folder deleted from `features/scratch/issue-{NUMBER}/`
- [ ] No regressions in existing functionality
- [ ] No tests modified except when categorically wrong (documented in log)

## Next Steps

After implementation is complete:
1. Review implementation against plan
2. Verify all Success Criteria above are met
3. Review `git diff` for unintended changes
4. Update version in setup.cfg if needed
5. Commit changes (do NOT push without permission)
6. Prepare for PR creation

---

**Implementation Notes:**

- All files extracted from the plan to the workspace must be verbatim copies (no modifications during extraction)
- Extract ALL major step sections upfront before starting implementation (Step 3)
- When copying code from plan blocks to source files:
  - Remove block comment annotations (e.g., `# Block X.Y.Z:`)
  - For tests: Merge Gherkin scenario into test function docstring
  - Copy everything else exactly
- Extracting sections upfront reduces context load and speeds up implementation
- The Implementation Checklist is your TODO list - follow it line by line and check off items as you complete them
- Agents with tracking tools (like manage_todo_list) may use them as supplementary progress tracking
- The implementation log captures reality - log all deviations and errors
- Tests define correct behaviour - don't change them to make implementation easier
- Gherkin scenarios are contracts - implementation must satisfy them
- Workspace files are source documents for reference, not instruction files
