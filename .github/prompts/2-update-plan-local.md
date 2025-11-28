# Prompt: Update Plan Locally

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

**CRITICAL:** Do NOT update GitHub issue comments. This prompt only updates the local plan document.

## Your Task

You are updating the plan document (`features/{FEATURE_NAME}.md`) with answers, decisions, and analysis provided by the user. This is a LOCAL-ONLY operation - you must NOT post anything to GitHub issue comments.

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

## UK English

All text must use UK English spelling: behaviour, colour, organise, etc.
