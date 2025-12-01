# Prompt 3: Generate Test Specifications

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

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 3 of 6: generating Gherkin test specifications for all implementation steps.

## Critical Rules - NO GUESSING POLICY

**NEVER guess or make assumptions about ANYTHING.**

**You are not helping by pretending to have information you don't have.**

If you are not certain about test expectations or behaviour, you must explicitly state that you don't know and ask for clarification.

### Mandatory Source Citation for External Knowledge

When writing tests involving external tools or libraries:

1. **Check if you have webpage fetching capability** - If you don't have `fetch_webpage`, `curl`, or similar tools, state this immediately
2. **If you can fetch: Retrieve official documentation BEFORE writing tests**
3. **Cite the specific URL** you fetched or checked
4. **Quote the relevant section** from the documentation
5. **If you cannot find or access documentation**, state: "I cannot find documentation to verify this" instead of guessing

**Examples requiring documentation fetch:**
- pytest fixture behaviour
- Mock/patch usage patterns
- Assertion methods and expected behaviour
- Test framework capabilities

All test scenarios must be based on:
- Actual implementation plans from Step 2
- Verified existing behaviour from codebase analysis
- Explicit requirements from the issue
- Official documentation for test tools/libraries

If test behaviour is unclear:
1. Review the implementation plan
2. Check existing tests for similar functionality
3. For pytest/testing patterns: Fetch official documentation
4. Ask the user for clarification

Do NOT:
- Make up test expectations
- Assume behaviour without verification
- Write tests without understanding what they should verify
- Pretend to know pytest features without checking documentation
- Assume mock/patch behaviour without verification

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

## Gherkin Test Specification Format

**From planning.instructions.md:**

For EACH test, document using this format:

```markdown
**Test X.Y.Z: test_function_name**

```gherkin
Scenario: Description of what this test validates
  Given [preconditions - what state exists before test]
  And [additional preconditions if needed]
  When [action being tested]
  Then [expected outcome]
  And [additional expected outcomes if needed]
  
  # Tests: [What specific functionality this test exercises]
  # Validates: [Why this test confirms correct behaviour]
```
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

**From planning.instructions.md:**

Tests use X.Y.Z format:
- **X** = Implementation step number
- **Y** = Code block number being tested (must be even number: Y+1)
- **Z** = Test number (1, 2, 3, etc.)

**Example:**
- Code 3.4 = `set_values()` function
- Test 3.4.1 = First test for `set_values()`
- Test 3.4.2 = Second test for `set_values()`
- Test 3.4.3 = Third test for `set_values()`

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
3. ✅ Include test coverage rationale
4. ✅ Use correct hierarchical numbering
5. ✅ Follow all Python testing standards

After completing all steps, confirm:
- Total number of new tests specified
- Number of existing tests requiring updates
- Coverage assessment (are all behaviours tested?)

Ask user to review test specifications before proceeding to Step 4 (implementation code).
