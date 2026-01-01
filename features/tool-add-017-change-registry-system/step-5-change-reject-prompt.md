# Step 5: Implement change-reject.md Prompt

**File:** [.github/prompts/change-reject.md](../../../.github/prompts/change-reject.md)

**Purpose:** Mark change as rejected and move to archive

## Table of Contents

1. [Get Change Information](#1-get-change-information)
2. [Confirm Rejection](#2-confirm-rejection)
3. [Extract Dates](#3-extract-dates)
4. [Prepare Archived Entry](#4-prepare-archived-entry)
5. [Add to Archived Registry](#5-add-to-archived-registry)
6. [Remove from Active Registry](#6-remove-from-active-registry)
7. [Update Tracking Issue #98](#7-update-tracking-issue-98)
8. [Update Tracking Issue #99](#8-update-tracking-issue-99)
9. [Note Implementation Issue](#9-note-implementation-issue)

---

## Detailed Implementation Actions

### 1. Get Change Information

**Tools:** `run_in_terminal` (gh issue)

- Ask user for Change ID
- Ask user for rejection reason (optional)
- **Fetch from GitHub issue #98** - Use `gh issue view 98 --json body -q .body` to pull current content as source of truth
- Parse Active Changes tables from issue content
- Find change entry by Change ID

### 2. Confirm Rejection

**Interaction:** User confirmation

- Display change details to user
- Ask for confirmation: "Are you sure you want to reject {change-id}?"
- If not confirmed, abort

### 3. Extract Dates

**Tools:** `run_in_terminal` (git log)

- Search git log for first commit that added the change to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)
- Use that date as "Opened" date (YYYY-MM-DD format)
- Use current date as "Closed" date (YYYY-MM-DD format)

### 4. Prepare Archived Entry

**Logic:** Data transformation with formatting

- Copy change data from [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md) entry
- Apply strikethrough formatting to: Change ID, Component, Ticket ID, Description
- Do NOT apply strikethrough to Status
- Add Opened date column
- Add Closed date column
- Set Status to "Rejected" (plain text, no strikethrough)

### 5. Add to Archived Registry

**Tools:** `run_in_terminal` (gh issue), `replace_string_in_file`

- **Fetch from GitHub issue #99** - Use `gh issue view 99 --json body -q .body` to pull current archived content as source of truth
- Parse Archived Changes tables from issue content
- Determine correct section (milestone + category)
- Insert row in correct table section
- If section doesn't exist, create it with proper heading structure
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ARCHIVED.md](../../CHANGES-ARCHIVED.md)

### 6. Remove from Active Registry

**Tools:** `replace_string_in_file`

- Remove entire row from Active Changes data (already fetched in step 1)
- If removing last entry in a category section, remove the category section heading
- If removing last entry in a milestone section, remove the milestone section heading
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)

### 7. Update Tracking Issue #98

**Tools:** `run_in_terminal` (gh issue)

- **Push modified Active Changes** - Use `gh issue edit 98 --body` to update GitHub issue #98
- Post comment with `gh issue comment 98 --body`: "Rejected {change-id}: {description} - {reason}"

### 8. Update Tracking Issue #99

**Tools:** `run_in_terminal` (gh issue)

- **Push modified Archived Changes** - Use `gh issue edit 99 --body` to update GitHub issue #99
- Post comment with `gh issue comment 99 --body`: "Archived (Rejected) {change-id}: {description}"

### 9. Note Implementation Issue

**Output:** User message

- If Ticket ID exists in change entry, log message: "Implementation issue {ticket-id} can now be closed with reason: Rejected - {reason}"
- Do NOT close the issue (user operation)
