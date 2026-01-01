# Step 3: Implement change-update-status.md Prompt

**File:** [.github/prompts/change-update-status.md](../../../.github/prompts/change-update-status.md)

**Purpose:** Manual status transitions outside Step 1-8 workflow

## Table of Contents

1. [Get Change Information](#1-get-change-information)
2. [Validate Status Transition](#2-validate-status-transition)
3. [Update Active Registry](#3-update-active-registry)
4. [Update Tracking Issue #98](#4-update-tracking-issue-98)
5. [Log Status Change](#5-log-status-change)

---

## Detailed Implementation Actions

### 1. Get Change Information

**Tools:** `run_in_terminal` (gh issue)

- Ask user for Change ID
- **Fetch from GitHub issue #98** - Use `gh issue view 98 --json body -q .body` to pull current content as source of truth
- Parse Active Changes tables from issue content
- Find change entry by Change ID
- Display current status to user

### 2. Validate Status Transition

**Interaction:** User prompt with validation

- Ask user for new status
- Valid statuses: Draft, Planning, Ready, In Progress, Review, Complete, Rejected
- Valid transitions:
  - Draft → Planning, Rejected
  - Planning → Ready, Rejected
  - Ready → In Progress, Rejected
  - In Progress → Review, Rejected
  - Review → In Progress, Complete, Rejected
- If invalid transition, explain valid options and ask again

### 3. Update Active Registry

**Tools:** `replace_string_in_file`

- Modify Status column in Active Changes data (already fetched in step 1)
- Preserve all other columns
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)

### 4. Update Tracking Issue #98

**Tools:** `run_in_terminal` (gh issue)

- **Push modified Active Changes** - Use `gh issue edit 98 --body` to update GitHub issue #98
- Post comment with `gh issue comment 98 --body`: "Status changed: {change-id} {old-status} → {new-status}"

### 5. Log Status Change

**Tools:** `replace_string_in_file` (if plan document exists)

- Add comment to plan document (if exists) with status change and timestamp
