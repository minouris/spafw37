# Step 2: Implement change-complete.md Prompt

**File:** [.github/prompts/change-complete.md](../../../.github/prompts/change-complete.md)

**Purpose:** Complete and archive change

**Called By:** Step 8 ([8-implement-from-plan.md](../../../.github/prompts/8-implement-from-plan.md)) at end

## Table of Contents

1. [Locate Change Entry](#1-locate-change-entry)
2. [Extract Dates](#2-extract-dates)
3. [Prepare Archived Entry](#3-prepare-archived-entry)
4. [Add to Archived Registry](#4-add-to-archived-registry)
5. [Remove from Active Registry](#5-remove-from-active-registry)
6. [Update Tracking Issue #98](#6-update-tracking-issue-98)
7. [Update Tracking Issue #99](#7-update-tracking-issue-99)
8. [Note Implementation Issue Closure](#8-note-implementation-issue-closure)
9. [Return to Caller](#9-return-to-caller)

---

## Detailed Implementation Actions

### 1. Locate Change Entry

**Tools:** `run_in_terminal` (gh issue), `read_file`

- Extract Change ID from plan document metadata
- **Fetch from GitHub issue #98** - Use `gh issue view 98 --json body -q .body` to pull current content as source of truth
- Parse Active Changes tables from issue content
- Find change entry row by Change ID

### 2. Extract Dates

**Tools:** `run_in_terminal` (git log)

- Search git log for first commit that added the change to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)
- Use that date as "Opened" date (YYYY-MM-DD format)
- Use current date as "Closed" date (YYYY-MM-DD format)

### 3. Prepare Archived Entry

**Logic:** Data transformation

- Copy change data from [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md) entry
- Add Opened date column
- Add Closed date column
- Set Status to "Complete"
- Preserve all other columns (Change ID, Component, Ticket ID, Description)

### 4. Add to Archived Registry

**Tools:** `run_in_terminal` (gh issue), `replace_string_in_file`

- **Fetch from GitHub issue #99** - Use `gh issue view 99 --json body -q .body` to pull current archived content as source of truth
- Parse Archived Changes tables from issue content
- Determine correct section (milestone + category)
- Insert row in correct table section (maintain chronological order within section)
- If section doesn't exist, create it with proper heading structure
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ARCHIVED.md](../../CHANGES-ARCHIVED.md)

### 5. Remove from Active Registry

**Tools:** `replace_string_in_file`

- Remove entire row from Active Changes data (already fetched in step 1)
- If removing last entry in a category section, remove the category section heading
- If removing last entry in a milestone section, remove the milestone section heading
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)

### 6. Update Tracking Issue #98

**Tools:** `run_in_terminal` (gh issue)

- **Push modified Active Changes** - Use `gh issue edit 98 --body` to update GitHub issue #98
- Post comment with `gh issue comment 98 --body`: "Completed {change-id}: {description}"

### 7. Update Tracking Issue #99

**Tools:** `run_in_terminal` (gh issue)

- **Push modified Archived Changes** - Use `gh issue edit 99 --body` to update GitHub issue #99
- Post comment with `gh issue comment 99 --body`: "Archived {change-id}: {description} (Closed: {closed-date})"

### 8. Note Implementation Issue Closure

**Output:** User message

- If Ticket ID exists in change entry, log message: "Implementation issue {ticket-id} can now be closed"
- Do NOT close the issue (user operation)

### 9. Return to Caller

**Returns:** Confirmation

- Confirm completion to Step 8
- Step 8 proceeds with final workflow steps
