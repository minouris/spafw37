# Step 1: Implement change-create.md Prompt

**File:** [.github/prompts/change-create.md](../../../.github/prompts/change-create.md)

**Purpose:** Create and register new change in tracking system

**Called By:** Step 1 ([1-create-plan-skeleton.md](../../../.github/prompts/1-create-plan-skeleton.md)) at beginning

**Returns:** Change ID, Component, Ticket ID (if applicable), Opened date, Plan filename

## Table of Contents

1. [Create Temporary Stem Plan File](#1-create-temporary-stem-plan-file)
2. [Determine Work Context](#2-determine-work-context)
3. [Read Existing Change IDs](#3-read-existing-change-ids)
4. [Determine Change Type](#4-determine-change-type)
5. [Generate Change ID](#5-generate-change-id)
6. [Determine Component](#6-determine-component)
7. [Get Change Description](#7-get-change-description)
8. [Determine Milestone](#8-determine-milestone)
9. [Rename Plan File](#9-rename-plan-file)
10. [Add to Active Registry](#10-add-to-active-registry)
11. [Complete Plan Skeleton](#11-complete-plan-skeleton)
12. [Return to Caller](#12-return-to-caller)

---

## Detailed Implementation Actions

### 1. Create Temporary Stem Plan File

**Tools:** `create_file`

- Generate timestamp-based temporary filename: `_temp-plan-{timestamp}.md`
- Create stem plan file in `features/` directory with basic structure:
  ```markdown
  # [PENDING: Change Description]
  
  **Change ID:** [PENDING]
  **Component:** [PENDING]
  **Ticket ID:** [PENDING]
  **Status:** Draft
  **Opened:** {current-date}
  
  ## Overview
  
  [PENDING: Overview to be added]
  
  ## Work Context
  
  [PENDING: Work context to be determined]
  ```
- This ensures data is not lost if conversation is interrupted

### 2. Determine Work Context

**Interaction:** User prompt

- Ask user: "Are you defining brand new work from scratch, or starting work based on existing ticket(s)?"
- If existing ticket(s): Ask for ticket number(s) or URLs
- If new from scratch: Note "New work from scratch"
- Update stem plan file "Work Context" section with answer
- Store context for later use (affects description, links, related work)

### 3. Read Existing Change IDs

**Tools:** `read_file`, `grep_search`

- Use `read_file` to read [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md) (all Active Changes table sections)
- Use `read_file` to read [CHANGES-ARCHIVED.md](../../CHANGES-ARCHIVED.md) (all Archived Changes table sections)
- Extract all Change IDs from both files
- Parse Change IDs to identify subjects and highest numbers per subject

### 4. Determine Change Type

**Interaction:** User prompt

- If work context is from existing ticket(s): Infer category and type from ticket labels/content
- Ask user to confirm change category: Feature, Tool, or Documentation
- Map to subject code: `feat`, `tool`, `docs`
- Update stem plan file metadata: Store subject
- Ask user to confirm change type: Add, Enhancement, Refactor, or Fix
- Map to verb code: `add`, `enh`, `ref`, `fix`
- Update stem plan file metadata: Store verb

### 5. Generate Change ID

**Logic:** ID generation

- Find highest number for the selected subject (e.g., all `feat-*-NNN`)
- Increment by 1
- Format as 3-digit zero-padded number
- Construct Change ID: `{subject}-{verb}-{NNN}`
- Verify no collision exists
- Update stem plan file metadata: Replace `[PENDING]` with actual Change ID

### 6. Determine Component

**Interaction:** User prompt, `read_file`

- If `add` verb: Ask if this introduces new component or adds to existing
  - If new: Prompt for component details (defer to change-create-component logic)
  - If existing: List existing components for selection
- If `enh`/`ref`/`fix` verb: List existing components for selection
- Validate component exists in Component Identification section
- Update stem plan file metadata: Replace `[PENDING]` with actual Component

### 7. Get Change Description

**Interaction:** User prompt

- If work context from existing ticket: Use ticket title as default
- Ask user for short description (confirm/edit if from ticket)
- Update stem plan file title: Replace `[PENDING: Change Description]` with actual description

### 8. Determine Milestone

**Logic:** Milestone assignment

- If subject is `feat` or `docs`: Assign to current/next product milestone
- If subject is `tool`: Assign to "No Milestone"
- Confirm with user
- Store milestone for registry entry (not in plan metadata)

### 9. Rename Plan File

**Tools:** `run_in_terminal`

- Construct proper filename: `{change-id}-{descriptive-slug}.md`
- Use `run_in_terminal` with `mv` command to rename from temporary name
- Continue working with renamed file

### 10. Add to Active Registry

**Tools:** `run_in_terminal` (gh issue), `replace_string_in_file`

- **Fetch from GitHub issue #98** - Use `gh issue view 98 --json body -q .body` to pull current content as source of truth
- Parse Active Changes tables from issue content
- Determine correct section (milestone + category)
- Create table row:
  - Change ID: Generated ID
  - Component: Selected component
  - Ticket ID: From existing ticket if provided, otherwise empty (update plan metadata if populated)
  - Description: Short description from user
  - Status: "Draft"
- Insert row in correct table section
- If section doesn't exist, create it with proper heading structure
- **Update workspace file** - Use `replace_string_in_file` to write modified content to [CHANGES-ACTIVE.md](../../CHANGES-ACTIVE.md)
- **Update GitHub issue #98** - Use `gh issue edit 98 --body` to push modified content back to issue
- Use `gh issue comment 98 --body` to add comment: "Added {change-id}: {description}"

### 11. Complete Plan Skeleton

**Logic:** Continue to normal Step 1

- Add remaining skeleton sections to plan file (replacing `[PENDING: Overview to be added]`)
- Proceed with normal Step 1 skeleton creation
- If work context is from existing ticket(s): Include reference to original ticket(s) in overview

### 12. Return to Caller

**Returns:** Metadata object

- Return Change ID, Component, Ticket ID, Opened date, Plan filename to Step 1
- Step 1 uses this metadata to complete plan skeleton creation
