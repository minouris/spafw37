# Prompt 3: Generate Test Specifications

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY (applies to ALL work).**

Key reminder: NEVER guess or assume anything. If uncertain about test expectations, behaviour, or external tool usage, explicitly state what you don't know and ask for clarification.

## Your Task

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 3 of 6: generating Gherkin test specifications for all implementation steps.

## Python Testing Standards

**From python-tests.instructions.md - ALL tests MUST follow these rules:**

### Test Structure Requirements

1. **Use module-level functions, NOT test classes**
   ```python
   # CORRECT
   def test_feature_behaviour():
       pass
   
   # WRONG
   class TestFeature:
       def test_behaviour(self):
           pass
   ```

2. **Include comprehensive docstrings (minimum 3 sentences)**
   - Sentence 1: What the test does (tests X behaviour)
   - Sentence 2: What the expected outcome is
   - Sentence 3: Why this validates correct behaviour

3. **Test exactly one behaviour per test function**

4. **Use `setup_function()` explicitly at start of each test**
   ```python
   def test_example():
       """Test description here."""
       setup_function()  # REQUIRED at start
       # Test code here
   ```

5. **Follow Python naming standards (from python.instructions.md)**
   - Use descriptive names, no lazy placeholders like `data`, `result`, `tmp`
   - Functions: `lowercase_with_underscores()`
   - Variables: `lowercase_with_underscores`
   - Constants: `UPPER_CASE_WITH_UNDERSCORES`

## Test Specification Format

**CRITICAL: In plan documents, Gherkin comes FIRST in separate blocks, then Python tests.**

**From python-tests.instructions.md § Including Gherkin Scenarios in Tests:**

In plan documents (`features/**/*.md`), Gherkin scenarios are written separately in their own code blocks BEFORE the Python test implementation. The Python test contains only the descriptive docstring (What/Outcome/Why). When generating final implementation files, the Gherkin will be integrated into the test docstrings.

**Why:** This separation aids in test generation and keeps specifications clear for review.

For EACH test, document using this format:

```markdown
### Test X.Y.Z: Brief description of what's being tested

\`\`\`gherkin
Scenario: Description of what this test validates
  Given [preconditions - what state exists before test]
  And [additional preconditions if needed]
  When [action being tested]
  Then [expected outcome]
  And [additional expected outcomes if needed]
  
  # Tests: [What specific functionality this test exercises]
  # Validates: [Why this test confirms correct behaviour]
\`\`\`

### Code X.Y.Z: Test for function_name()

\`\`\`python
def test_function_name():
    """Test that [what is being tested].
    
    This test verifies that [expected outcome].
    This behaviour is expected because [why this validates correct behaviour].
    """
    setup_function()
    # Test implementation here
\`\`\`
```

**For tests that need updating (obsolete or changed expectations):**

```markdown
**Test X.Y.Z: test_existing_function (requires update)**

**Old test logic (to be removed):**
```gherkin
Scenario: Description of old expectation (OLD)
  Given [old preconditions]
  When [old action]
  Then [old expectation]
  
  # Tests: Old behavior
```

**New test logic (replacement):**
```gherkin
Scenario: Description of new expectation (NEW)
  Given [new preconditions]
  When [new action]
  Then [new expectation]
  
  # Tests: New behavior
  # Validates: Why this is the correct new behavior
```

**Why this change is necessary:**
[Explain the rationale for changing the test]
```

## Your Task for Each Implementation Step

For EACH implementation step in the plan:

### 1. Add Test Specifications Section

After the implementation description and before the next step, add:

```markdown
**Tests:** [Brief overview of what needs testing]

**Test X.2.1: test_name_describing_behaviour**

```gherkin
Scenario: Clear description
  Given [setup]
  When [action]
  Then [outcome]
  
  # Tests: What is tested
  # Validates: Why this confirms correctness
```

[Repeat for all tests needed for this step]

**Tests:** Manual review to verify [what needs verification]

[↑ Back to top](#table-of-contents)
```

### 2. Identify Obsolete or Changed Tests

If any existing tests become obsolete or need updating:

1. Create a subsection: "Existing Tests Requiring Updates"
2. For each test, document OLD and NEW expectations using Gherkin
3. Explain why the change is necessary

### 3. Test Coverage Checklist

For each step, ensure tests cover:
- ✅ Happy path (successful operation)
- ✅ Error cases (expected failures)
- ✅ Edge cases (boundary conditions)
- ✅ Integration (interaction with other components)
- ✅ Backward compatibility (if applicable)

## Hierarchical Test Numbering

**All plan documents in `features/` directory must follow the structure rules defined in:**
**`.github/instructions/plan-structure.instructions.md`**

Key points:
- Tests use X.Y.Z format (X=step, Y=member, Z=block)
- Each function (Code X.Y.Z) followed immediately by its tests (Test X.Y.(Z+1), Test X.Y.(Z+2), etc.)
- Each test section contains both Gherkin specification and Python implementation
- Test headings describe what's being tested (not "Gherkin for...")

**See the instruction file for complete details and examples.**

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English Requirements

Use UK spelling: behaviour, colour, initialise, synchronise, optimise

## Output Requirements

For EACH implementation step in the document:
1. ✅ Add complete test specifications using Gherkin format
2. ✅ Document any existing tests requiring updates (OLD/NEW format)

## Step Completion Gate

Before proceeding to the next step, verify:

- [ ] Every implementation step has Gherkin test specifications
- [ ] Every function has at least one test scenario
- [ ] Edge cases and error conditions have dedicated tests
- [ ] Test specifications follow Gherkin format (Given/When/Then)
- [ ] Planning Checklist item for Step 3 marked complete `[x]`
- [ ] Table of Contents updated

**Do NOT proceed to Step 4 until ALL items above are checked.**

Ask the user: "Step 3 complete. All test specifications added. Ready to proceed to Step 4 (implementation code)?"
3. ✅ Include test coverage rationale
4. ✅ Use correct hierarchical numbering
5. ✅ Follow all Python testing standards

After completing all steps, confirm:
- Total number of new tests specified
- Number of existing tests requiring updates
- Coverage assessment (are all behaviours tested?)

## CRITICAL: Pre-Submission Verification

**Before completing your response, verify ALL test specifications against the mandatory checklist:**

**See `.github/instructions/code-review-checklist.instructions.md` for the complete checklist.**

Specifically verify:
1. ✅ **Each test follows: Code → Test → Test pattern** (not Step Xa/Xb)
2. ✅ **Test structure uses module-level functions** (not classes)
3. ✅ **Each test has 3-sentence minimum docstring** (What, Outcome, Why)
4. ✅ **One behaviour per test function**
5. ✅ **Descriptive naming** (no `data`, `result`, `tmp`)
6. ✅ **Gherkin + Python pairs** for each test

**If any violations found, fix them before submitting your response.**

## Step 3.1: Update Planning Checklist

Mark the Planning Checklist item for this step as complete:
1. Find "Step 3: Generate tests" in the Planning Checklist
2. Change `- [ ]` to `- [x]`

Ask user to review test specifications before proceeding to Step 4 (implementation code).
