# Prompt 1: Create Plan Document Skeleton and Branch

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY (applies to ALL work).**

Key reminder: NEVER guess or assume anything about the issue, repository structure, or implementation requirements. If uncertain, explicitly state what you don't know.

## Your Task

You are creating an issue plan document for issue #{ISSUE_NUMBER}. This is step 1 of 6: creating the document skeleton and git branch.

## Step 2: Create Skeletal Plan Document

Create a new planning document in the `features/` directory:

**File path:** `features/<feature_name>.md`

**Note:** This plan document will follow structure rules defined in `.github/instructions/plan-structure.instructions.md` when implementation code is added in Step 4.

**Content structure:**

```markdown
# Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

**GitHub Issue:** https://github.com/minouris/spafw37/issues/{ISSUE_NUMBER}

## Overview

{ISSUE_BODY}

**Key architectural decisions:**

- **[Decision category]:** [PLACEHOLDER - Will be filled in Step 2]

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
- [Further Considerations](#further-considerations)
- [Success Criteria](#success-criteria)
- [CHANGES for v{VERSION} Release](#changes-for-vversion-release)

## Implementation Steps

[PLACEHOLDER - Will be filled in Steps 3-4]

[↑ Back to top](#table-of-contents)

## Further Considerations

[PLACEHOLDER - Will be filled in Step 2]

[↑ Back to top](#table-of-contents)

## Success Criteria

[PLACEHOLDER - Will be filled in Step 5]

[↑ Back to top](#table-of-contents)

## CHANGES for v{VERSION} Release

[PLACEHOLDER - Will be filled in Step 6]

[↑ Back to top](#table-of-contents)
---
```

## Critical Rules

**From general.instructions.md - NO GUESSING POLICY:**

**NEVER guess or make assumptions about ANYTHING.**

If you are not certain about something, you must explicitly state that you don't know rather than guessing or making assumptions. This policy takes absolute precedence.

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Use UK English spelling:** colour, organise, behaviour, centre, licence, defence

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## Output Format

After completing both steps, inform the user:
- The branch name created
- The plan document location
- Confirm skeleton is ready for Step 2 (analysis)
