# Step 6: Modify 1-create-plan-skeleton.md

**File:** [.github/prompts/1-create-plan-skeleton.md](../../../.github/prompts/1-create-plan-skeleton.md)

**Purpose:** Add change creation to Step 1 workflow

## Table of Contents

1. [Integration Point](#integration-point)
2. [Modification Details](#modification-details)

---

## Integration Point

At the **beginning** of the prompt, before creating plan skeleton structure.

## Modification Details

### Add Change Creation Invocation

**Pseudo-code:**
```
1. Invoke change-create.md prompt
2. Receive: Change ID, Component, Ticket ID, Opened date, Plan filename
3. Plan file already created and renamed by change-create.md
4. Use returned metadata to populate plan skeleton sections
5. Continue with normal Step 1 skeleton creation
```

### Implementation Approach

**Tools:** Internal prompt invocation

1. **Invoke change-create.md**
   - Execute the change-create.md prompt logic
   - This creates temporary stem plan file, determines work context, generates Change ID, determines component/milestone, renames plan file, and adds to active registry

2. **Receive Metadata**
   - Change ID (e.g., `feat-add-042`)
   - Component (e.g., `feat-param-registration`)
   - Ticket ID (if provided by user, otherwise empty)
   - Opened date (YYYY-MM-DD)
   - Plan filename (e.g., `feat-add-042-parameter-validation.md`)

3. **Continue with Skeleton Creation**
   - Plan file already exists with basic metadata populated
   - Add remaining sections per normal Step 1 process:
     - Deliverables
     - Key Design Decisions
     - Implementation Status (mark as Planning)
     - Success Criteria
     - Related Changes
     - Notes

4. **Status Update**
   - Change status automatically set to "Draft" by change-create.md
   - When Step 1 completes, status can be updated to "Planning" using change-update-status.md
