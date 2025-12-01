# Prompt 2: Analyse Issue and Create Implementation Plan

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

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 2 of 6: analysing the issue and creating the implementation breakdown.

**Important:** If called multiple times on the same document, UPDATE existing sections rather than overwriting them. Preserve any work already completed, and only add or refine content as needed.

## Critical Rules - NO GUESSING POLICY

**NEVER guess or make assumptions about ANYTHING.**

**You are not helping by pretending to have information you don't have.**

If you are not certain about something, you must explicitly state that you don't know rather than guessing or making assumptions.

### Mandatory Source Citation for External Knowledge

When answering questions about external systems, tools, APIs, or documentation:

1. **Check if you have webpage fetching capability** - If you don't have `fetch_webpage`, `curl`, or similar tools, state this immediately
2. **If you can fetch: Retrieve official documentation BEFORE answering**
3. **Cite the specific URL** you fetched or checked
4. **Quote the relevant section** from the documentation
5. **If you cannot find or access documentation**, state: "I cannot find documentation to verify this" instead of guessing

**Examples requiring documentation fetch:**
- How external libraries work (pytest, argparse, etc.)
- Standard library module behaviour not visible in code
- File format specifications
- Third-party tool configuration
- API specifications, endpoints, or data structures

**This includes (but is not limited to):**
- External API specifications, endpoints, or data structures
- Third-party library behaviour or usage patterns
- File formats, protocols, or standards
- Configuration requirements for external services
- Project-specific patterns or conventions
- User requirements or intentions
- Implementation details not explicitly documented

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **For external systems: Fetch official documentation or state you cannot access it**
4. **Suggest where the user can find the information**
5. **Ask the user to verify or provide the correct information**

For codebase-specific information:
1. Read the relevant source files
2. Search the codebase for patterns
3. Check test files for expected behaviour
4. If still uncertain, state what you don't know and ask the user

Do NOT:
- Pretend to know how external libraries work without checking documentation
- Assume standard library behaviour without verification
- Answer questions about external systems without citing sources

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

## Output Requirements

Update the plan document with:
1. ✅ Complete Overview section with architectural decisions
2. ✅ Program Flow Analysis (if applicable)
3. ✅ Implementation Steps outline with all steps identified
4. ✅ Further Considerations with initial questions (all marked PENDING REVIEW)
5. ✅ Updated Table of Contents to include all new sections (three levels: major sections, subsections, individual questions)

Confirm completion and ask user to review considerations before proceeding to Step 3 (test generation).
