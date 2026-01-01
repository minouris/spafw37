# Step 7: Modify 8-implement-from-plan.md

**File:** [.github/prompts/8-implement-from-plan.md](../../../.github/prompts/8-implement-from-plan.md)

**Purpose:** Add change completion to Step 8 workflow

## Table of Contents

1. [Integration Point](#integration-point)
2. [Modification Details](#modification-details)

---

## Integration Point

At the **end** of the prompt, after all implementation verified and tests pass.

## Modification Details

### Add Change Completion Invocation

**Pseudo-code:**
```
1. Verify all implementation complete (tests pass, docs updated, etc.)
2. Invoke change-complete.md prompt
3. Change automatically archived
4. Receive confirmation
5. Display completion message to user
6. Note implementation issue can be closed (if applicable)
```

### Implementation Approach

**Tools:** Internal prompt invocation

1. **Verify Implementation Complete**
   - All tests passing
   - Documentation updated
   - Code review completed (if applicable)
   - All checklist items marked complete

2. **Invoke change-complete.md**
   - Execute the change-complete.md prompt logic
   - This extracts Change ID from plan, fetches current registry data from issues #98 and #99, moves change from active to archived, updates status to "Complete", updates workspace files and tracking issues

3. **Receive Confirmation**
   - Confirmation that change has been archived
   - Closed date
   - Location in archived registry (milestone + category)

4. **Display Completion Message**
   - Inform user: "Change {change-id} completed and archived"
   - If Ticket ID exists: "Implementation issue {ticket-id} can now be closed"

5. **Proceed with Step 8 Final Steps**
   - User can close implementation issue
   - User can merge branch
   - User can proceed to next work item
