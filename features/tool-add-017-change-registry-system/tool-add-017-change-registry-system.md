# Change Registry System

**Change ID:** tool-add-017  
**Component:** tool-workflow  
**Ticket ID:** [#100](https://github.com/minouris/spafw37/issues/100)  
**Status:** In Progress  
**Opened:** 2026-01-01

## Overview

This change implements a comprehensive change tracking and registry system for the spafw37 project, independent of the GitHub issue tracking system. The system provides stable change identification, component categorization, and historical tracking across all change types (features, tools, documentation).

## Deliverables

### Primary Deliverables

1. **CHANGES-ACTIVE.md** (Issue [#98](https://github.com/minouris/spafw37/issues/98))
   - Active changes registry with component identification
   - Organized by milestone and category
   - Frequently mutated data first (Active Changes before Component Identification)
   - Empty sections hidden

2. **CHANGES-ARCHIVED.md** (Issue [#99](https://github.com/minouris/spafw37/issues/99))
   - Historical archive of completed and rejected changes
   - Organized by milestone (most recent first, then "No Milestone", then older)
   - Complete audit trail with dates and status

### Supporting Deliverables

3. **Change ID System**
   - Format: `{subject}-{verb}-{NNN}`
   - Subjects: `feat`, `tool`, `docs`
   - Verbs: `add`, `enh`, `ref`, `fix`
   - Sequential numbering per subject (3-digit zero-padded)

4. **Component System**
   - 14 components across Features (13), Tools (3), Documentation (1)
   - Naming: 3-5 letters per hyphenated group
   - Hierarchical organization (e.g., `feat-param-registration`, `tool-workflow`)
   - Synchronized GitHub labels (grey #ededed)

5. **Milestone Organization**
   - Current/most recent milestone first
   - "No Milestone" section for infrastructure/tooling
   - Older milestones in reverse chronological order

## Key Design Decisions

### Change ID Format
- **Decision:** Use `{subject}-{verb}-{NNN}` format instead of `{verb}-{subject}-{NNNN}`
- **Rationale:** Subject-first enables better grouping and filtering by type
- **Impact:** All 32 historical changes renumbered with new format

### Component Naming
- **Decision:** Allow 3-5 letters per hyphenated group instead of strict 4-letter limit
- **Rationale:** Clarity over brevity (e.g., `param` instead of `parm`)
- **Impact:** Significantly improved readability

### Milestone Handling
- **Decision:** Tools/infrastructure in "No Milestone", features/docs in versioned milestones
- **Rationale:** Infrastructure work not tied to product releases
- **Impact:** Clear separation of concerns, better release planning

### Data-First Organization
- **Decision:** Most frequently mutated data first (Active Changes before Component Identification)
- **Rationale:** Optimize for common access patterns
- **Impact:** Better usability, reduced scrolling

## Prompt Integration Requirements

### Tracking Prompts Called by Workflow

#### change-create.md

**Purpose:** Create and register new change in tracking system

**Called By:** Step 1 (1-create-plan-skeleton.md) at beginning

**High-Level Operations:**
- Create temporary stem plan file with progressive data capture
- Determine work context (new vs existing ticket)
- Generate unique Change ID
- Collect component, milestone, description
- Add entry to CHANGES-ACTIVE.md (fetch from #98, modify, update)
- Rename plan file with Change ID prefix
- Return Change ID and metadata to caller

**User Invocation:** Called automatically by Step 1

#### change-complete.md

**Purpose:** Complete and archive change

**Called By:** Step 8 (8-implement-from-plan.md) at end

**High-Level Operations:**
- Extract Change ID from plan document
- Fetch current data from issues #98 and #99
- Move change from active to archived registry
- Set Status to "Complete" with dates
- Update workspace files and tracking issues
- Note implementation issue can be closed

**User Invocation:** Called automatically by Step 8

### Manual Lifecycle Management Prompts

#### change-update-status.md

**Purpose:** Manual status transitions between workflow steps

**High-Level Operations:**
- Fetch from #98, validate transition, update status
- Update workspace file and tracking issue

**User Invocation:** "Update status for change {change-id}"

#### change-create-component.md

**Purpose:** Add new component to identification registry

**High-Level Operations:**
- Validate component ID and uniqueness
- Add to Component Identification section
- Create GitHub label
- Update workspace file and tracking issue

**User Invocation:** "Create component {component-id}"

#### change-reject.md

**Purpose:** Reject change and move to archive

**High-Level Operations:**
- Fetch from #98 and #99
- Move change to archived with Status: "Rejected"
- Apply strikethrough formatting
- Update workspace files and tracking issues

**User Invocation:** "Reject change {change-id}"

### Workflow Prompt Modifications

#### 1-create-plan-skeleton.md

**Modification:** Add invocation of `change-create.md` at beginning

**Integration Point:** Before creating plan skeleton structure

**Operations:**
- Execute `change-create.md` prompt
- Receive Change ID and metadata
- Use Change ID for plan file (already renamed by change-create)
- Proceed with skeleton creation using returned metadata

#### 8-implement-from-plan.md

**Modification:** Add invocation of `change-complete.md` at end

**Integration Point:** After all implementation verified and tests pass

**Operations:**
- Execute `change-complete.md` prompt
- Change archived automatically
- Confirm completion to user
- Note implementation issue can be closed

#### planning-workflow.instructions.md

**Modification:** Document change registry tracking prompts and invocation patterns

**Purpose:** Enable users to invoke tracking prompts using plain English

## Implementation Status

### Completed
- ✅ Change ID format defined and applied to all 32 archived changes
- ✅ Component identification system with 14 components
- ✅ GitHub labels created/updated (15 renamed, 1 deleted)
- ✅ CHANGES-ACTIVE.md structure (Active Changes, Component Identification, instructions)
- ✅ CHANGES-ARCHIVED.md structure (v1.1.0 and No Milestone sections)
- ✅ Milestone-based organization (current first, then No Milestone, then older)
- ✅ Data-first layout (frequently mutated data at top)
- ✅ Empty sections hidden in Active Changes
- ✅ Populated with 5 active changes (1 feature, 4 tools)
- ✅ Architecture.md with workflow integration decisions

### In Progress
- 🔄 This plan document (prompt requirements documentation)

### Not Started
- ⏳ Create change-update-status.md prompt
- ⏳ Create change-create-component.md prompt
- ⏳ Create change-reject.md prompt
- ⏳ Update 1-create-plan-skeleton.md with change creation logic
- ⏳ Update 8-implement-from-plan.md with change archival logic
- ⏳ Update planning-workflow.instructions.md with registry lifecycle
- ⏳ Integration testing with real workflow

## Success Criteria

1. **Tracking Independence**
   - Changes can be tracked with or without GitHub issues
   - Change IDs remain stable regardless of ticket system changes

2. **Component Organization**
   - All components clearly defined with descriptions
   - GitHub labels synchronized with component names
   - Easy to identify what area a change affects

3. **Historical Visibility**
   - Complete audit trail of all changes
   - Easy to find similar past work
   - Clear understanding of project evolution

4. **Milestone Clarity**
   - Clear separation of infrastructure vs. product work
   - Easy to see what's in current release
   - Historical releases well-organized

5. **Usability**
   - Frequently accessed data appears first
   - Empty sections don't clutter the view
   - Easy to add/update/close changes

## Related Changes

- **tool-ref-005** (Issue #93): Multi-file plan structure - foundational architectural work
- **tool-enh-012** (Issue #96): Multi-file structure refinements - child of #93
- **tool-enh-015** (Issue #95): Prompt refinements - broader planning workflow improvements

## Notes

- Issues #98 and #99 ARE the deliverables (the files themselves), not tracking issues for something else
- This change demonstrates the system tracking itself (meta-level tracking)
- Change ID tool-add-017 assigned before work issue created, demonstrating independence from ticketing
