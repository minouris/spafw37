# Prompt: Update Plan Locally

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

**CRITICAL:** Do NOT update GitHub issue comments. This prompt only updates the local plan document.

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

You are updating the plan document (`features/{FEATURE_NAME}.md`) with answers, decisions, and analysis provided by the user. This is a LOCAL-ONLY operation - you must NOT post anything to GitHub issue comments.

**Note:** Plan documents follow structure rules defined in `.github/instructions/plan-structure.instructions.md` (automatically applied via `applyTo: features/**/*.md`).

## Parameters

- `{ISSUE_NUMBER}` - The GitHub issue number (used to locate the plan document)

## Usage

```bash
# Update local plan for issue #15 with user's answers
@2-update-plan-local 15
```

## Process

### Step 1: Identify What to Update

Listen to the user's input and identify:
- Which questions (Q1-QN) have answers to add
- Which Further Considerations (FC1-FCN) have answers to add
- Which items should change status (PENDING REVIEW → RESOLVED)
- Any cross-references to add between questions and considerations
- Any complexity assessments to update

### Step 2: Update the Plan Document

**File location:** `features/issue-{ISSUE_NUMBER}-{feature-name}-{version}.md`

For each item the user has answered:

1. **Add the answer text** in the appropriate section:

```markdown
**Q1: Architecture Approach** ([#issuecomment-XXXXXX](...))

[Original question text]

**Answer:** [User's answer/decision]

[↑ Back to top](#table-of-contents)
```

2. **Update status markers** where applicable:
   - Change section headers from "PENDING REVIEW" to "RESOLVED" only when answers are complete AND no TBD items remain
   - Keep status as "PENDING REVIEW" if answer contains "TBD", "requires further analysis", or similar language indicating incomplete decision
   - Update Table of Contents to reflect resolved status

3. **Add cross-references** between related items:

```markdown
**Q1: Architecture Approach**

[Question text]

**Answer:** See [Further Consideration 2: Architecture Approach Trade-offs](#2-architecture-approach-trade-offs---resolved)

[↑ Back to top](#table-of-contents)
```

Or:

```markdown
### 2. Architecture Approach Trade-offs - RESOLVED

[Question and answer]

**Resolves:** Q1 (Architecture Approach)
```

4. **Update complexity assessments** if the user provides updated complexity ratings:

```markdown
**Low complexity:**
- Text input with `input()` function ✅ (Decided: use Python's `input()`)
- CLI override behaviour ✅ (Decided: "if set, don't prompt")

**Medium complexity:**
- Type validation ✅ (Decided: use existing framework validation functions)

**High complexity:**
- Timing control ⚠️ (TBD: needs further analysis)

**Very high complexity (deferred):**
- Command-driven population ❌ (Not implementing in this version)
```

### Step 3: Maintain Consistency

Ensure the plan document remains consistent:
- All GitHub comment IDs remain unchanged
- Table of Contents reflects current status
- Cross-references are bidirectional where appropriate
- Status markers match the actual state (RESOLVED vs PENDING REVIEW)

### Step 4: Report Changes

Provide a brief summary of what was updated:

```
Updated plan document locally:
✅ Q1 - Added answer (param-level approach)
✅ Q7 - Added answer (use input() function)
✅ FC1 - Marked as RESOLVED
✅ FC2 - Marked as RESOLVED, added "Resolves Q1" cross-reference

Status: 2/8 questions resolved, 2/7 considerations resolved
```

## Important Notes

### DO:
- ✅ Update the local plan document file
- ✅ Add answers provided by the user
- ✅ Update status markers (PENDING REVIEW → RESOLVED)
- ✅ Add cross-references between questions and considerations
- ✅ Update complexity assessments
- ✅ Maintain consistency in formatting and structure

### DO NOT:
- ❌ Post comments to GitHub issue
- ❌ Update GitHub issue comments via API
- ❌ Call `gh api` to modify comments
- ❌ Use any GitHub API write operations
- ❌ Commit or push changes (unless user explicitly requests)

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English

All text must use UK English spelling: behaviour, colour, organise, etc.
