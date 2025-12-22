# Prompt 2: Analyse Issue and Create Implementation Plan

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY (applies to ALL work).**

Key reminder: NEVER guess or assume anything. For external systems, fetch and cite official documentation. For codebase patterns, read source files and tests.

## Your Task

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 2 of 6: analysing the issue and creating the implementation breakdown.

**Important:** If called multiple times on the same document, UPDATE existing sections rather than overwriting them. Preserve any work already completed, and only add or refine content as needed.

### Posting Questions to GitHub Issue

**When you have questions that require user clarification:**

1. **Post INDIVIDUAL comments** for each question (allows threaded responses)
2. **Capture each comment URL** from the command output
3. **Extract comment IDs** from URLs (the number after `#issuecomment-`)
4. **Document questions in the plan file** with their respective comment IDs

**Step-by-step process:**

```bash
# For each question, post a separate comment for threaded responses

# Question 1
cat > /tmp/question.md << 'EOF'
**Q1: [Category]**
[Question text with details and options]
EOF
gh issue comment {ISSUE_NUMBER} --body-file /tmp/question.md
# Capture URL: https://github.com/owner/repo/issues/N#issuecomment-XXXXXX

# Question 2
cat > /tmp/question.md << 'EOF'
**Q2: [Category]**
[Question text with details and options]
EOF
gh issue comment {ISSUE_NUMBER} --body-file /tmp/question.md
# Capture URL: https://github.com/owner/repo/issues/N#issuecomment-YYYYYY

# Repeat for all questions...
```

**In the plan document, format each question as:**
```markdown
**Q1: [Category]** ([#issuecomment-XXXXXX](https://github.com/owner/repo/issues/N#issuecomment-XXXXXX))
[Question text]

[↑ Back to top](#table-of-contents)

---
```

**This ensures:**
- Each question has its own comment thread on GitHub
- Users can reply directly to specific questions
- Answers are organized and easy to track
- Design decisions are documented with direct links

## Writing Style Requirements

**From planning.instructions.md:**

1. **Be technical and dispassionate**
   - Use precise technical language
   - Avoid marketing language or hype
   - State facts without embellishment
   - No exclamation marks or enthusiastic language

2. **Be specific and concrete**
   - Include exact file paths
   - Include exact function names
   - Include code examples where helpful
   - Specify error messages and conditions

3. **Use UK English:** colour, organise, behaviour, centre, licence, defence

## Step 2.1: Fill Overview Section

Replace the PLACEHOLDER in the Overview section with:

**Structure:**
- 2-4 paragraphs explaining:
  - What problem this issue solves or what functionality it adds
  - How it fits into the existing architecture
  - What the end result will be for users

**Key architectural decisions:**
- List 3-5 key decisions in this format:
  - **[Decision category]:** [Brief explanation of architectural choice]

**Example:**

```markdown
## Overview

Currently, `_set_defaults()` is called in `cli.py` after `_pre_parse_params()` is called, meaning that any param values set by `_pre_parse_params()` will be overridden if those params have default values. This is a bug that prevents pre-parse params from functioning correctly when they have default values defined.

Setting defaults is not a responsibility that should belong to `cli.py`. The CLI module should orchestrate argument parsing, not manage parameter lifecycle concerns like default value initialization. Parameter default management belongs in `param.py` alongside other parameter configuration logic.

The fix will move default-setting responsibility from `cli.py` to `param.py`, ensuring defaults are set at the correct point in the parameter lifecycle—immediately when parameters are registered via `add_param()`. This prevents defaults from overriding values set during pre-parsing and establishes a clearer separation of concerns.

**Key architectural decisions:**

- **Responsibility placement:** Default-setting moves from CLI parsing phase to parameter registration phase in `param.py`
- **Timing:** Defaults set immediately when `add_param()` is called, before any CLI parsing occurs
- **Backward compatibility:** Maintains existing behavior for non-pre-parse params while fixing pre-parse param issue
- **XOR handling:** Preserves existing XOR validation disabling during default-setting to avoid false conflicts
```

## Step 2.2: Add Program Flow Analysis (If Applicable)

**When to include:** For issues that change how code flows through the system (refactorings, architectural changes, new execution paths).

**Position:** After Table of Contents entry, before Implementation Steps section.

**Structure:**

1. **Section heading:** Use descriptive title focused on primary feature/behaviour being changed
2. **Current Behaviour (Before Changes)** subsection:
   - One paragraph summary
   - Separate breakdowns for each usage scenario (if flows differ)
   - Result summary
3. **New Behaviour (After Changes)** subsection:
   - One subsection per behaviour mode/option
   - Each includes: summary paragraph, scenario breakdowns, result
4. **Key architectural changes** summary

**Flow breakdown format:**
- Numbered steps showing complete call chain
- Include function names and module boundaries (e.g., "CLI → _parse_command_line()")
- Show data flowing through system (e.g., "Receives tokenized params `[...]`")
- Indent sub-steps with bullet points
- Highlight decision points and branching
- Show error propagation
- **Only include multiple scenarios if flows actually differ**

## Step 2.3: Create Implementation Steps Outline

**Note:** When implementation code is added in Step 4, it must follow the structure rules in `.github/instructions/plan-structure.instructions.md` (X.Y.Z block numbering, function + tests interweaved).

Replace PLACEHOLDER in Implementation Steps with numbered step outlines:

**Each step should have:**
- Clear title describing what it accomplishes
- File(s) being modified
- Brief description
- Placeholder for detailed implementation (Step 4 will fill this)

**Example outline:**

```markdown
## Implementation Steps

### 1. Add failing test to demonstrate bug

**Files:** `tests/test_cli.py`, `tests/test_param.py`

Add a test that demonstrates the current bug: pre-parse params with default values get overridden by `_set_defaults()` after pre-parsing completes. This test should FAIL initially, proving the bug exists.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 2. Move _set_defaults logic to param.py

**File:** `src/spafw37/param.py`

Create a new internal function `_set_param_default()` in `param.py` that sets the default value for a single parameter.

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

[Continue for all implementation steps...]
```

## Step 2.4: Create Further Considerations Section

Replace PLACEHOLDER in Further Considerations with initial design questions.

**Post EACH consideration as an INDIVIDUAL GitHub comment** (allows threaded responses):

```bash
# Consideration 1
cat > /tmp/consideration.md << 'EOF'
**Further Consideration: [Consideration name]**

**Question:** [What design decision needs to be made?]

**Analysis:** [Your analysis or "TO BE DETERMINED - requires investigation"]

**Trade-offs:** [What factors need evaluation]

**Impact:** [How it affects the implementation]
EOF
gh issue comment {ISSUE_NUMBER} --body-file /tmp/consideration.md
# Capture URL: https://github.com/owner/repo/issues/N#issuecomment-XXXXXX

# Consideration 2
cat > /tmp/consideration.md << 'EOF'
**Further Consideration: [Next consideration name]**
...
EOF
gh issue comment {ISSUE_NUMBER} --body-file /tmp/consideration.md
# Capture URL: https://github.com/owner/repo/issues/N#issuecomment-YYYYYY

# Repeat for EACH consideration...
```

**Format EACH consideration in plan document with its own comment ID:**

```markdown
### 1. [Consideration name] - PENDING REVIEW

([#issuecomment-XXXXXX](https://github.com/owner/repo/issues/N#issuecomment-XXXXXX))

**Question:** [What design decision needs to be made?]

**Answer:** [Your analysis or "TO BE DETERMINED - requires investigation"]

**Rationale:** [Why this approach, or what factors need evaluation]

**Implementation:** [How it affects the implementation, or "Depends on resolution"]

[↑ Back to top](#table-of-contents)

---

### 2. [Next consideration name] - PENDING REVIEW

([#issuecomment-YYYYYY](https://github.com/owner/repo/issues/N#issuecomment-YYYYYY))

**Question:** [Next design decision]

...

[↑ Back to top](#table-of-contents)

---
```

**Mark all considerations as "PENDING REVIEW" - never mark as "RESOLVED" without explicit user confirmation.**

**This ensures:**
- EVERY consideration has its own discussion thread on GitHub
- Each design analysis can be discussed and refined independently
- All decisions are documented with direct links to specific comment threads
- Users can provide feedback on individual considerations without mixing topics

## Step 2.5: Define Success Criteria

Replace PLACEHOLDER in Success Criteria section with specific, verifiable criteria for the **feature outcomes**, not plan completion.

**Purpose:** Define what "done" means for the feature from a user/system perspective.

**Focus on:**
- **Functional outcomes** - Does the feature behave correctly?
- **Performance outcomes** - Does it meet performance requirements?
- **Integration outcomes** - Does it work with existing systems?
- **User experience outcomes** - Does it meet usability requirements?

**NOT about:**
- Plan document completion (that's Planning Checklist)
- Implementation workflow (that's Implementation Checklist)
- Code quality rules (those are universal standards)

**Structure:**

```markdown
## Success Criteria

This issue is considered successfully implemented when:

**Functional Requirements:**
- [ ] Feature X produces correct output Y for input Z
- [ ] Edge case A handled correctly (specific behaviour expected)
- [ ] Integration with existing feature B works as designed
- [ ] Error case C produces appropriate error message D

**Performance Requirements:**
- [ ] Operation completes in <N seconds for typical input
- [ ] Memory usage remains under X MB for Y items
- [ ] No performance regression for existing features

**Compatibility Requirements:**
- [ ] Works with Python 3.7.0+
- [ ] Backward compatible with existing API usage
- [ ] Existing tests continue to pass

**User Experience Requirements:**
- [ ] Error messages are clear and actionable
- [ ] Configuration options are intuitive
- [ ] Documentation explains how to use feature
- [ ] Examples demonstrate common use cases
```

**Guidelines:**
1. **Be specific** - "Error message includes function name" not "errors handled properly"
2. **Be measurable** - "< 100ms" not "fast", "80% coverage" not "well tested"
3. **Be outcome-focused** - "User can X" not "Code implements Y"
4. **Include acceptance tests** - Each criterion should be verifiable

**Example - Bug Fix:**
```markdown
**Functional Requirements:**
- [ ] Pre-parse params with default values retain their pre-parsed values
- [ ] Pre-parse params without default values work as before
- [ ] Non-pre-parse params with defaults work as before
- [ ] XOR validation not triggered during default-setting phase
```

**Example - New Feature:**
```markdown
**Functional Requirements:**
- [ ] User can specify prompt text for a parameter
- [ ] Prompt appears before CLI parsing when configured
- [ ] User input validation executes before storing value
- [ ] Invalid input prompts user to re-enter
- [ ] Prompt skipped if value provided via CLI argument
```

## Output Requirements

Update the plan document with:
1. ✅ Complete Overview section with architectural decisions
2. ✅ Program Flow Analysis (if applicable)
3. ✅ Implementation Steps outline with all steps identified
4. ✅ Further Considerations with initial questions (all marked PENDING REVIEW)
5. ✅ Success Criteria defining feature outcomes (not plan completion)
6. ✅ Updated Table of Contents to include all new sections (three levels: major sections, subsections, individual questions)

Confirm completion and ask user to review considerations and success criteria before proceeding to Step 3 (test generation).
