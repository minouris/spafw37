# Change Registry System

**Change ID:** tool-add-017  
**Component:** tool-workflow  
**Ticket ID:** [#100](https://github.com/minouris/spafw37/issues/100)  
**Status:** In Progress  
**Opened:** 2026-01-01

## Table of Contents

1. [Overview](#overview)
2. [Deliverables](#deliverables)
3. [Key Design Decisions](#key-design-decisions)
4. [Prompt Integration Requirements](#prompt-integration-requirements)
5. [Implementation Status](#implementation-status)
6. [Success Criteria](#success-criteria)
7. [Related Changes](#related-changes)
8. [Notes](#notes)

---

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

The change registry integrates with the planning workflow through:

- **5 tracking prompts** for lifecycle management (create, complete, update-status, create-component, reject)
- **Workflow modifications** to Step 1 and Step 8 prompts (automatic change creation and completion)
- **Documentation updates** to planning-workflow.instructions.md for user invocation patterns

Detailed implementation steps are in separate Step files:
- [step-1-change-create-prompt.md](step-1-change-create-prompt.md)
- [step-2-change-complete-prompt.md](step-2-change-complete-prompt.md)
- [step-3-change-update-status-prompt.md](step-3-change-update-status-prompt.md)
- [step-4-change-create-component-prompt.md](step-4-change-create-component-prompt.md)
- [step-5-change-reject-prompt.md](step-5-change-reject-prompt.md)
- [step-6-modify-create-skeleton.md](step-6-modify-create-skeleton.md)
- [step-7-modify-implement-from-plan.md](step-7-modify-implement-from-plan.md)
- [step-8-update-planning-workflow-docs.md](step-8-update-planning-workflow-docs.md)

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
- 🔄 Implementation step files (8 files created for detailed prompt implementation)

### Not Started
- ⏳ Implement change-create.md prompt (see [step-1-change-create-prompt.md](step-1-change-create-prompt.md))
- ⏳ Implement change-complete.md prompt (see [step-2-change-complete-prompt.md](step-2-change-complete-prompt.md))
- ⏳ Implement change-update-status.md prompt (see [step-3-change-update-status-prompt.md](step-3-change-update-status-prompt.md))
- ⏳ Implement change-create-component.md prompt (see [step-4-change-create-component-prompt.md](step-4-change-create-component-prompt.md))
- ⏳ Implement change-reject.md prompt (see [step-5-change-reject-prompt.md](step-5-change-reject-prompt.md))
- ⏳ Modify 1-create-plan-skeleton.md (see [step-6-modify-create-skeleton.md](step-6-modify-create-skeleton.md))
- ⏳ Modify 8-implement-from-plan.md (see [step-7-modify-implement-from-plan.md](step-7-modify-implement-from-plan.md))
- ⏳ Update planning-workflow.instructions.md (see [step-8-update-planning-workflow-docs.md](step-8-update-planning-workflow-docs.md))
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
