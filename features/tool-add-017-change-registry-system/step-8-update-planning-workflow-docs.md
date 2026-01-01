# Step 8: Update planning-workflow.instructions.md

**File:** [.github/instructions/planning-workflow.instructions.md](../../../.github/instructions/planning-workflow.instructions.md)

**Purpose:** Document change registry tracking prompts and invocation patterns

## Table of Contents

1. [Location](#location)
2. [Content Requirements](#content-requirements)
   - [Section 1: Automatic Tracking](#section-1-automatic-tracking-called-by-workflow)
   - [Section 2: Manual Tracking Operations](#section-2-manual-tracking-operations)
   - [Section 3: Update Complete Example Workflow](#section-3-update-complete-example-workflow)

---

## Location

Add new section **"Change Registry Tracking"** before the existing **"Complete Example Workflow"** section.

## Content Requirements

### Section 1: Automatic Tracking (Called by Workflow)

#### Introduction
Explain that these prompts are called automatically by the workflow and users don't need to invoke them explicitly.

#### change-create.md (Called by Step 1)

**What it does:**
- Creates temporary stem plan file with progressive data capture
- Determines work context (new vs existing ticket)
- Generates unique Change ID based on change type
- Collects component, milestone, and description from user
- Adds entry to CHANGES-ACTIVE.md (Status: "Draft")
- Renames plan file with Change ID prefix
- Returns metadata to Step 1 for skeleton completion

**Note:** Change ID is assigned automatically at the start of Step 1, before any planning begins.

#### change-complete.md (Called by Step 8)

**What it does:**
- Extracts Change ID from plan document
- Moves change from CHANGES-ACTIVE.md to CHANGES-ARCHIVED.md
- Sets Status to "Complete" with opened/closed dates
- Updates tracking issues #98 and #99
- Notes that implementation issue can be closed

**Note:** Change is archived automatically after Step 8 completes successfully.

### Section 2: Manual Tracking Operations

#### Introduction
Explain that these prompts are invoked manually between workflow steps for status updates, component creation, and change rejection.

#### change-update-status.md

**What it does:**
- Updates Status field for a change in CHANGES-ACTIVE.md
- Validates status transitions
- Updates tracking issue #98
- Logs status change in plan document

**When to use:**
- Moving from Draft to Planning (after initial skeleton created)
- Moving from Planning to Ready (after planning approved)
- Moving from Ready to In Progress (when starting implementation)
- Moving from In Progress to Review (when ready for review)

**User invocation patterns:**
- "Update status for change {change-id}"
- "Set status of {change-id} to Planning"
- "Move {change-id} to In Progress"

#### change-create-component.md

**What it does:**
- Validates component ID format and uniqueness
- Adds new component to Component Identification section in CHANGES-ACTIVE.md
- Creates synchronized GitHub label (grey #ededed)
- Updates tracking issue #98

**When to use:**
- When implementing a feature that introduces a new functional area not covered by existing components

**User invocation patterns:**
- "Create component {component-id}"
- "Add new component for {feature-area}"

#### change-reject.md

**What it does:**
- Confirms rejection with user
- Moves change from CHANGES-ACTIVE.md to CHANGES-ARCHIVED.md with strikethrough formatting
- Sets Status to "Rejected"
- Updates tracking issues #98 and #99
- Notes that implementation issue can be closed with rejection reason

**When to use:**
- When a planned change is no longer needed
- When a change is superseded by different approach
- When a change is deemed not feasible

**User invocation patterns:**
- "Reject change {change-id}"
- "Mark {change-id} as rejected"

### Section 3: Update Complete Example Workflow

Update the existing "Complete Example Workflow" section to show change registry integration:

```
1. "Create plan for issue #61"
   → (Step 1 automatically calls change-create.md)
   → Change ID assigned (e.g., feat-add-042)
   → Plan file created: feat-add-042-parameter-validation.md
   → Entry added to CHANGES-ACTIVE.md with Status: "Draft"

2a. "Update status for feat-add-042 to Planning"
    → Manual status update via change-update-status.md
    
2b. "Do the analysis and planning step"
    → Creates questions, posts to GitHub, adds Planning Checklist items for each question
    
2c. User answers questions in chat
    "Update the plan with: [answers]"
    → Marks question items [x] in Planning Checklist
    
2d. "Update status for feat-add-042 to Ready"
    → Manual status update when planning complete

3. "Generate test specs"
   → Marks Step 3 complete in Planning Checklist

4. "Generate implementation code"
   → Marks Step 4 complete in Planning Checklist

5. "Generate documentation changes"
   → Marks Step 5 complete in Planning Checklist

6. "Generate CHANGES section"
   → Marks Step 6 complete in Planning Checklist

7. "Verify the plan is ready for implementation"
   → Final verification, updates Planning Checklist with any issues

8. "Update status for feat-add-042 to In Progress"
   → Manual status update before implementation begins

9. "Implement the feature from the plan"
   → Writes actual code
   → (Step 8 automatically calls change-complete.md at end)
   → Change moved to CHANGES-ARCHIVED.md with Status: "Complete"
   → Note: "Implementation issue #61 can now be closed"
```
