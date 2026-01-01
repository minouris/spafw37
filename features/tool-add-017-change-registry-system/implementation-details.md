# Implementation Details: Change Registry System Prompts

This document contains detailed step-by-step implementation instructions for creating the change registry lifecycle management prompts.

## Tracking Prompt: change-create.md

**Purpose:** Create and register new change in tracking system

**Called By:** Step 1 (1-create-plan-skeleton.md) at beginning

**Returns:** Change ID, Component, Ticket ID (if applicable), Opened date, Plan filename

**Detailed Actions:**

1. **Create Temporary Stem Plan File**
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

2. **Determine Work Context**
   - Ask user: "Are you defining brand new work from scratch, or starting work based on existing ticket(s)?"
   - If existing ticket(s): Ask for ticket number(s) or URLs
   - If new from scratch: Note "New work from scratch"
   - Update stem plan file "Work Context" section with answer
   - Store context for later use (affects description, links, related work)

3. **Read Existing Change IDs**
   - Use `read_file` to read CHANGES-ACTIVE.md (all Active Changes table sections)
   - Use `read_file` to read CHANGES-ARCHIVED.md (all Archived Changes table sections)
   - Extract all Change IDs from both files
   - Parse Change IDs to identify subjects and highest numbers per subject

4. **Determine Change Type**
   - If work context is from existing ticket(s): Infer category and type from ticket labels/content
   - Ask user to confirm change category: Feature, Tool, or Documentation
   - Map to subject code: `feat`, `tool`, `docs`
   - Update stem plan file metadata: Store subject
   - Ask user to confirm change type: Add, Enhancement, Refactor, or Fix
   - Map to verb code: `add`, `enh`, `ref`, `fix`
   - Update stem plan file metadata: Store verb

5. **Generate Change ID**
   - Find highest number for the selected subject (e.g., all `feat-*-NNN`)
   - Increment by 1
   - Format as 3-digit zero-padded number
   - Construct Change ID: `{subject}-{verb}-{NNN}`
   - Verify no collision exists
   - Update stem plan file metadata: Replace `[PENDING]` with actual Change ID

6. **Determine Component**
   - If `add` verb: Ask if this introduces new component or adds to existing
     - If new: Prompt for component details (defer to change-create-component logic)
     - If existing: List existing components for selection
   - If `enh`/`ref`/`fix` verb: List existing components for selection
   - Validate component exists in Component Identification section
   - Update stem plan file metadata: Replace `[PENDING]` with actual Component

7. **Get Change Description**
   - If work context from existing ticket: Use ticket title as default
   - Ask user for short description (confirm/edit if from ticket)
   - Update stem plan file title: Replace `[PENDING: Change Description]` with actual description

8. **Determine Milestone**
   - If subject is `feat` or `docs`: Assign to current/next product milestone
   - If subject is `tool`: Assign to "No Milestone"
   - Confirm with user
   - Store milestone for registry entry (not in plan metadata)

9. **Rename Plan File**
   - Construct proper filename: `{change-id}-{descriptive-slug}.md`
   - Use `run_in_terminal` with `mv` command to rename from temporary name
   - Continue working with renamed file

10. **Add to Active Registry**
   - **Fetch from GitHub issue #98** - Pull current content as source of truth
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
   - **Update workspace file** - Write modified content to CHANGES-ACTIVE.md
   - **Update GitHub issue #98** - Push modified content back to issue with comment: "Added {change-id}: {description}"

11. **Update Tracking Issue #98**

11. **Complete Plan Skeleton**
   - Add remaining skeleton sections to plan file (replacing `[PENDING: Overview to be added]`)
   - Proceed with normal Step 1 skeleton creation
   - If work context is from existing ticket(s): Include reference to original ticket(s) in overview

12. **Return to Caller**
   - Return Change ID, Component, Ticket ID, Opened date, Plan filename to Step 1
   - Step 1 uses this metadata to complete plan skeleton creation

## Tracking Prompt: change-complete.md

**Purpose:** Complete and archive change

**Called By:** Step 8 (8-implement-from-plan.md) at end

**Detailed Actions:**

1. **Locate Change Entry**
   - Extract Change ID from plan document metadata
   - **Fetch from GitHub issue #98** - Pull current content as source of truth
   - Parse Active Changes tables from issue content
   - Find change entry row by Change ID

2. **Extract Dates**
   - Search git log for first commit that added the change to CHANGES-ACTIVE.md
   - Use that date as "Opened" date (YYYY-MM-DD format)
   - Use current date as "Closed" date (YYYY-MM-DD format)

3. **Prepare Archived Entry**
   - Copy change data from CHANGES-ACTIVE.md entry
   - Add Opened date column
   - Add Closed date column
   - Set Status to "Complete"
   - Preserve all other columns (Change ID, Component, Ticket ID, Description)

4. **Add to Archived Registry**
   - **Fetch from GitHub issue #99** - Pull current archived content as source of truth
   - Parse Archived Changes tables from issue content
   - Determine correct section (milestone + category)
   - Insert row in correct table section (maintain chronological order within section)
   - If section doesn't exist, create it with proper heading structure
   - **Update workspace file** - Write modified content to CHANGES-ARCHIVED.md

5. **Remove from Active Registry**
   - Remove entire row from Active Changes data (already fetched in step 1)
   - If removing last entry in a category section, remove the category section heading
   - If removing last entry in a milestone section, remove the milestone section heading
   - **Update workspace file** - Write modified content to CHANGES-ACTIVE.md

6. **Update Tracking Issue #98**
   - **Push modified Active Changes** to GitHub issue #98
   - Post comment: "Completed {change-id}: {description}"

7. **Update Tracking Issue #99**
   - **Push modified Archived Changes** to GitHub issue #99
   - Post comment: "Archived {change-id}: {description} (Closed: {closed-date})"

8. **Note Implementation Issue Closure**
   - If Ticket ID exists in change entry, log message: "Implementation issue {ticket-id} can now be closed"
   - Do NOT close the issue (user operation)

9. **Return to Caller**
   - Confirm completion to Step 8
   - Step 8 proceeds with final workflow steps

## Manual Prompt: change-update-status.md

**Purpose:** Manual status transitions outside Step 1-8 workflow

**Detailed Actions:**

1. **Get Change Information**
   - Ask user for Change ID
   - **Fetch from GitHub issue #98** - Pull current content as source of truth
   - Parse Active Changes tables from issue content
   - Find change entry by Change ID
   - Display current status to user

2. **Validate Status Transition**
   - Ask user for new status
   - Valid statuses: Draft, Planning, Ready, In Progress, Review, Complete, Rejected
   - Valid transitions:
     - Draft → Planning, Rejected
     - Planning → Ready, Rejected
     - Ready → In Progress, Rejected
     - In Progress → Review, Rejected
     - Review → In Progress, Complete, Rejected
   - If invalid transition, explain valid options and ask again

3. **Update Active Registry**
   - Modify Status column in Active Changes data (already fetched in step 1)
   - Preserve all other columns
   - **Update workspace file** - Write modified content to CHANGES-ACTIVE.md

4. **Update Tracking Issue #98**
   - **Push modified Active Changes** to GitHub issue #98
   - Post comment: "Status changed: {change-id} {old-status} → {new-status}"

5. **Log Status Change**
   - Add comment to plan document (if exists) with status change and timestamp

## Manual Prompt: change-create-component.md

**Purpose:** Add new component when introducing new feature area

**Detailed Actions:**

1. **Get Component Information**
   - Ask user for component ID (validate format: subject-domain-aspect, 3-5 letters per group)
   - Ask user for component name (short, descriptive)
   - Ask user for component description (one sentence)
   - Ask user for category (Features/Tools/Documentation)
   - Ask user for first milestone (current or specific version)

2. **Validate Component ID**
   - Check Component ID format matches pattern: `{subject}-{domain}-{aspect}`
   - Verify each part is 3-5 letters
   - Subject must be `feat`, `tool`, or `docs`
   - **Fetch from GitHub issue #98** - Pull current content as source of truth
   - Parse Component Identification tables from issue content
   - Check for component ID collisions

3. **Add to Component Identification**
   - Determine correct category table in Component Identification section
   - Create table row:
     - Component: Component ID
     - Name: Component name
     - Description: Component description
     - First Milestone: First milestone
     - Status: "Active"
   - Insert row in alphabetical order within category
   - **Update workspace file** - Write modified content to CHANGES-ACTIVE.md

4. **Create GitHub Label**
   - Use GitHub API to create label
   - Label name: Component ID
   - Label colour: #ededed (grey)
   - Label description: Component name

5. **Update Tracking Issue #98**
   - **Push modified Component Identification** to GitHub issue #98
   - Post comment: "Added component: {component-id} ({component-name})"

## Manual Prompt: change-reject.md

**Purpose:** Mark change as rejected and move to archive

**Detailed Actions:**

1. **Get Change Information**
   - Ask user for Change ID
   - Ask user for rejection reason (optional)
   - **Fetch from GitHub issue #98** - Pull current content as source of truth
   - Parse Active Changes tables from issue content
   - Find change entry by Change ID

2. **Confirm Rejection**
   - Display change details to user
   - Ask for confirmation: "Are you sure you want to reject {change-id}?"
   - If not confirmed, abort

3. **Extract Dates**
   - Search git log for first commit that added the change to CHANGES-ACTIVE.md
   - Use that date as "Opened" date (YYYY-MM-DD format)
   - Use current date as "Closed" date (YYYY-MM-DD format)

4. **Prepare Archived Entry**
   - Copy change data from CHANGES-ACTIVE.md entry
   - Apply strikethrough formatting to: Change ID, Component, Ticket ID, Description
   - Do NOT apply strikethrough to Status
   - Add Opened date column
   - Add Closed date column
   - Set Status to "Rejected" (plain text, no strikethrough)

5. **Add to Archived Registry**
   - **Fetch from GitHub issue #99** - Pull current archived content as source of truth
   - Parse Archived Changes tables from issue content
   - Determine correct section (milestone + category)
   - Insert row in correct table section
   - If section doesn't exist, create it with proper heading structure
   - **Update workspace file** - Write modified content to CHANGES-ARCHIVED.md

6. **Remove from Active Registry**
   - Remove entire row from Active Changes data (already fetched in step 1)
   - If removing last entry in a category section, remove the category section heading
   - If removing last entry in a milestone section, remove the milestone section heading
   - **Update workspace file** - Write modified content to CHANGES-ACTIVE.md

7. **Update Tracking Issue #98**
   - **Push modified Active Changes** to GitHub issue #98
   - Post comment: "Rejected {change-id}: {description} - {reason}"

8. **Update Tracking Issue #99**
   - **Push modified Archived Changes** to GitHub issue #99
   - Post comment: "Archived (Rejected) {change-id}: {description}"

9. **Note Implementation Issue**
   - If Ticket ID exists in change entry, log message: "Implementation issue {ticket-id} can now be closed with reason: Rejected - {reason}"
   - Do NOT close the issue (user operation)

## Workflow Prompt Modifications

### 1-create-plan-skeleton.md Modification

**Integration Point:** At beginning of prompt

**Action:** Add invocation of `change-create.md`

**Pseudo-code:**
```
1. Invoke change-create.md prompt
2. Receive: Change ID, Component, Ticket ID, Opened date, Plan filename
3. Plan file already created and renamed by change-create.md
4. Use returned metadata to populate plan skeleton sections
5. Continue with normal Step 1 skeleton creation
```

### 8-implement-from-plan.md Modification

**Integration Point:** At end of prompt, after all implementation verified

**Action:** Add invocation of `change-complete.md`

**Pseudo-code:**
```
1. Verify all implementation complete (tests pass, docs updated, etc.)
2. Invoke change-complete.md prompt
3. Change automatically archived
4. Receive confirmation
5. Display completion message to user
6. Note implementation issue can be closed (if applicable)
```

## Documentation Updates

### planning-workflow.instructions.md

**File:** `.github/instructions/planning-workflow.instructions.md`

**Location:** Add new section before "Complete Example Workflow"

**Section to Add:** "Change Registry Tracking"

**Content Requirements:**

1. **Automatic Tracking (Called by Workflow)** subsection:
   - Explain these prompts are called automatically
   - Document `change-create.md` (called by Step 1)
     - What it does
     - Note about automatic Change ID assignment
   - Document `change-complete.md` (called by Step 8)
     - What it does
     - Note about automatic archival

2. **Manual Tracking Operations** subsection:
   - Explain these are invoked manually between steps
   - Document `change-update-status.md`
     - What it does
     - User instruction patterns: "Update status for change {change-id}" or "Set status of {change-id} to Planning"
     - When to use
   - Document `change-create-component.md`
     - What it does
     - User instruction patterns: "Create component {component-id}" or "Add new component for {feature-area}"
     - When to use
   - Document `change-reject.md`
     - What it does
     - User instruction patterns: "Reject change {change-id}" or "Mark {change-id} as rejected"
     - When to use

3. **Update Complete Example Workflow:**
   - After Step 1: Show automatic change creation
   - Between steps: Show manual status updates
   - After Step 8: Show automatic change completion
