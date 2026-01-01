# Architectural Decisions: Change Registry System

This document consolidates all architectural decisions related to the change tracking and registry system for spafw37. It includes decisions from Issue #93 (Multi-file plan structure) and Issue #95 (Prompt refinements) that pertain to change identification, registry structure, and issue tracking.

## Table of Contents

1. [Change Identification](#change-identification)
2. [Change ID Format](#change-id-format)
3. [Component System](#component-system)
4. [Registry Structure](#registry-structure)
5. [Milestone Organization](#milestone-organization)
6. [Issue vs Deliverable Distinction](#issue-vs-deliverable-distinction)
7. [Tracking Independence](#tracking-independence)
8. [Workflow Integration](#workflow-integration)

---

## Change Identification

**Problem:** How do we uniquely identify changes across multiple files, developers, and time?

**Critical Constraint:** A ticket should only be created when the change has been at least somewhat described. We cannot start work without a ticket, but should not create empty tickets.

### Universal Requirement: Single Point of Truth

Regardless of project scale, change identifiers must have a single point of truth. This must be a ticket (GitHub issue) so it is freely accessible regardless of which branch a developer is on.

### Complexity: Request vs. Implementation Tickets

There is an important distinction between request tickets and implementation tickets:
- **Request tickets** (external): Describe problems or desired outcomes from user perspective (bug reports, feature requests)
- **Implementation tickets** (internal): Describe changes to the codebase (bugfixes, features, enhancements)

**Implications:**
- Multiple request tickets may be addressed by one implementation ticket
- One request ticket may require multiple implementation tickets
- Implementation tickets are what get planned and executed
- Changes (implementations) need an identity that may be independent of request ticket IDs

### AI Agent Requirement

For the AI agent to correctly create and track change planning, it must know:
1. What identification scheme is being used
2. What is being used to track change identifiers (registry file, issue list, directory scan, etc.)
3. How to create new identifiers without collisions
4. How to resolve what identifiers already exist

This means any scheme must be:
- **Well-defined:** Documented in prompts/instructions
- **Discoverable:** AI can query what identifiers exist
- **Programmatic:** AI can generate valid new identifiers
- **Collision-resistant:** AI can detect/avoid duplicates

---

## Change ID Format

### Decision

**Format:** `{subject}-{verb}-{NNN}`

Where:
- `{subject}` = Category of change (`feat`, `tool`, `docs`)
- `{verb}` = Type of modification (`add`, `enh`, `ref`, `fix`)
- `{NNN}` = Three-digit sequential number per subject (001-999)

**Examples:**
- `feat-add-001` - First feature addition
- `tool-fix-013` - Thirteenth tool bugfix
- `docs-enh-002` - Second documentation enhancement
- `feat-ref-018` - Eighteenth feature refactor

### Rationale

**Subject-First Ordering:**
- Enables better grouping and filtering by category
- All features together, all tools together, all docs together
- Easier to track what area of the project is being modified

**Three-Digit Padding:**
- Accommodates up to 999 changes per subject
- Ensures alphabetical sort matches numerical order
- More concise than four digits for project scale

**Sequential per Subject:**
- Each subject has its own sequence
- Reduces collision risk
- Clear separation between feat-add-001 and tool-add-001

### Evolution from Previous Format

**Old Format:** `{verb}-{subject}-{NNNN}`
- Example: `add-feature-0001`
- Verb-first made filtering by subject harder
- Four digits unnecessarily long

**Migration:** All 32 historical changes renumbered with new format on 2026-01-01.

---

## Component System

### Decision

Components provide hierarchical categorization of changes within each subject area.

**Naming Convention:** 3-5 letters per hyphenated group for clarity

**Structure:** `{subject}-{domain}-{aspect}`

**Examples:**
- `feat-param-registration` - Parameter registration feature area
- `feat-param-validation` - Parameter validation feature area
- `feat-cycle-api` - Cycles API feature area
- `tool-workflow` - Planning workflow tools
- `tool-cicd` - CI/CD infrastructure tools
- `docs-user` - User-facing documentation

### Current Components

**Features (13):**
- `feat-cmd-registration` - Command Registration
- `feat-conf-unset` - Config Unset
- `feat-cycle-api` - Cycles API
- `feat-cycle-loops` - Cycle Loops
- `feat-data-tools` - Data Tools
- `feat-help-display` - Help Display
- `feat-log-errors` - Error Logging
- `feat-log-output` - Logging Output
- `feat-param-defaults` - Parameter Defaults
- `feat-param-groups` - Parameter Groups
- `feat-param-prompts` - User Prompts
- `feat-param-registration` - Parameter Registration
- `feat-param-validation` - Parameter Validation

**Tools (3):**
- `tool-cicd` - CI/CD
- `tool-instructions` - Instructions
- `tool-workflow` - Planning Workflow

**Documentation (1):**
- `docs-user` - User Guides

### Component Creation Rule

New components are created when an `add-*` change introduces a new area that could be subject to future enhancements, fixes, or refactoring. Subsequent changes (enh-*, fix-*, ref-*) reference existing components. Multiple `add-*` changes may reference the same component if adding to an existing area.

### GitHub Label Synchronization

Each component has a corresponding GitHub label:
- **Color:** Gray (#ededed) for all component labels
- **Label name:** Matches component identifier exactly
- **Purpose:** Enables filtering issues by component area

### Rationale for 3-5 Letter Groups

**Old Rule:** Strict 4-letter abbreviations (e.g., `parm`, `logr`, `cmnd`, `cycl`)

**Problem:** Forced cryptic abbreviations that reduced readability

**New Rule:** Allow 3-5 letters per hyphenated group

**Benefits:**
- Significantly improved clarity (`param` vs `parm`, `log` vs `logr`, `cmd` vs `cmnd`)
- Still concise enough for practical use
- Natural abbreviations more intuitive

---

## Registry Structure

### Decision

The change registry consists of two markdown files in the `features/` directory:

**Active Changes:** `features/CHANGES-ACTIVE.md`
- Contains all open/in-progress changes
- Component identification registry
- Frequently mutated data first (Active Changes before Component Identification)
- Empty sections hidden

**Archived Changes:** `features/CHANGES-ARCHIVED.md`
- Contains all closed/completed changes
- Historical reference and audit trail
- Changes moved here when closed
- Organized by milestone

### Tracking Issues

**Issue #98:** Active Changes Registry
- Contains the actual active changes table
- Updated whenever changes are added/removed/status changes
- This is the registry data itself, not a work tracking issue

**Issue #99:** Archived Changes Registry
- Contains the actual archived changes table
- Updated when changes are closed/completed
- This is the registry data itself, not a work tracking issue

**Issue #100:** Change Registry System (Implementation)
- Work tracking issue for implementing the registry system
- References #98 and #99 as deliverables

### Table Formats

**Active Changes Table:**

| Change ID | Component | Ticket ID | Description | Status |
|-----------|----------|-----------|-------------|--------|

**Column Definitions:**
- **Change ID**: Stable identifier in format `{subject}-{verb}-{NNN}`
- **Component**: Reference to component from identification registry
- **Ticket ID**: GitHub issue number (blank until ticket created)
- **Description**: Short description of the change
- **Status**: Current state (Draft, Planning, Ready, In Progress, Review, Complete, Rejected)

**Archived Changes Table:**

| Change ID | Component | Ticket ID | Description | Opened | Closed | Status |
|-----------|----------|-----------|-------------|--------|--------|--------|

**Additional Columns:**
- **Opened**: Date the change was created (YYYY-MM-DD format)
- **Closed**: Date the change was closed (YYYY-MM-DD format)
- **Status**: Final state (typically "Complete" or "Rejected")

### Data-First Organization

**Principle:** Most frequently mutated data appears first

**Active Changes Registry:**
1. Active Changes tables (updated frequently)
2. Component Identification tables (updated rarely)
3. Column Definitions (reference material)
4. About This Registry (documentation)

**Archived Changes Registry:**
1. Archived Changes tables (append-only)
2. Column Definitions (reference material)
3. About This Registry (documentation)

**Rationale:** Optimize for common access patterns, reduce scrolling to frequently accessed data

---

## Milestone Organization

### Decision

Changes are organized by milestone with special handling for infrastructure work.

**Ordering:**
1. **Current milestone** (e.g., v1.1.0) - highest priority, appears first
2. **No Milestone** - infrastructure/tooling work not tied to product releases
3. **Other milestones** - chronologically ordered (newer first in active, older first in archived)

### No Milestone Section

**Purpose:** Infrastructure and tooling work that is not tied to product releases

**Typical Contents:**
- Tool changes (workflow improvements, CI/CD fixes, instructions updates)
- Project setup and configuration changes
- Development environment improvements

**Rationale:**
- Infrastructure work has different release cadence than product features
- Clear separation of concerns
- Better release planning visibility

### Milestone Assignment Rules

**Features:** Assigned to product milestone (e.g., v1.1.0, v1.2.0)
- User-facing functionality
- API changes
- New capabilities

**Tools:** Assigned to "No Milestone"
- Workflow improvements
- CI/CD changes
- Development tools
- Instructions and documentation for developers

**Documentation:** May be assigned to either
- User guides → product milestone
- Developer guides → "No Milestone"

### Category Organization

Within each milestone section, changes are organized by category:
- **Features**
- **Tools**
- **Documentation**

Empty categories are hidden to reduce clutter.

---

## Issue vs Deliverable Distinction

### Decision

Issues #98 and #99 ARE the deliverables (the registry files themselves), not tracking issues for something else.

**Issue #98:** Active Changes Registry
- **Nature:** Deliverable
- **Content:** The actual active changes table and component identification
- **Purpose:** Source of truth for active work
- **Updates:** Whenever changes are added, removed, or status changes

**Issue #99:** Archived Changes Registry
- **Nature:** Deliverable
- **Content:** The actual archived changes table
- **Purpose:** Historical audit trail
- **Updates:** When changes are moved from active to archived

**Issue #100:** Change Registry System
- **Nature:** Work tracking issue
- **Content:** Implementation plan, design decisions, work status
- **Purpose:** Track the work of creating/refining the registry system
- **References:** #98 and #99 as deliverables

### Rationale

**Branch Independence:**
- Issues are accessible from any branch without switching
- No merge conflicts
- Always available regardless of branch state

**Collaborative:**
- Multiple developers can access simultaneously
- Centralized source of truth
- Persistent across branch lifecycle

**AI Discoverable:**
- AI can query GitHub API for registry issues
- Programmatic access to change data
- Enables automated collision detection

### Workspace File Synchronization

**Principle:** GitHub issues are the source of truth for registry content to avoid merge conflicts across branches

**Process:**
1. **Fetch from GitHub issue** - Pull current content from issue #98 or #99
2. **Parse and modify** - Extract table data, make changes in memory
3. **Update workspace file** - Write modified content to CHANGES-ACTIVE.md or CHANGES-ARCHIVED.md
4. **Update GitHub issue** - Push modified content back to issue

**Rationale:**
- Avoids merge conflicts when multiple branches modify tracker files
- Issues provide branch-independent source of truth
- Always working with latest data regardless of local branch state
- Single source prevents divergence between branches

**Use Cases:**
- **Issues:** Quick reference, branch-independent access, external visibility, merge conflict avoidance
- **Workspace files:** Development work, editing, version control, local reference

---

## Tracking Independence

### Decision

Changes can be tracked with or without GitHub issues, and change IDs remain stable regardless of ticket system changes.

### Change Lifecycle Without Ticket

1. **Draft Phase:** Change ID assigned, no ticket yet
   - Change appears in Active Changes with blank Ticket ID
   - Planning and design work can begin
   - No premature ticket creation

2. **Ticket Creation:** When change is sufficiently described
   - GitHub issue created with plan content
   - Ticket ID column updated in registry
   - Change ID remains unchanged

3. **Implementation:** Work proceeds with linked ticket
   - Status updates tracked in registry
   - Ticket provides discussion thread
   - Change ID provides stable reference

4. **Completion:** Change closed and archived
   - Moved from CHANGES-ACTIVE.md to CHANGES-ARCHIVED.md
   - Ticket closed
   - Change ID preserved in archive

### Benefits

**Stable References:**
- Change IDs never change once assigned
- Can reference changes before tickets exist
- Decouples change identity from ticketing system

**Workflow Flexibility:**
- Supports architecture-first workflow (plan then ticket)
- Supports ticket-first workflow (ticket then plan)
- No forced workflow on team

**System Independence:**
- Could migrate from GitHub Issues to another system
- Change IDs remain valid
- Historical references preserved

### Rationale

**Core Principle:** Change IDs are the primary identifier, tickets are secondary

This enables:
- Planning without premature ticketing
- Stable cross-references in documentation
- Freedom to change ticketing systems
- Clearer separation between change identity and ticket tracking

---

## Workflow Integration

### Decision

The change registry integrates with the planning workflow (Steps 1-8) through dedicated tracking prompts that are called by workflow prompts, maintaining separation of concerns.

**Integration Architecture:**
- Workflow prompts (Step 1, Step 8) remain focused on their core purpose
- Tracking operations delegated to specialized tracking prompts
- Workflow prompts invoke tracking prompts at appropriate points

**Integration Points:**
- **Step 1 (1-create-plan-skeleton.md):** Calls `change-create.md` at beginning
- **Step 8 (8-implement-from-plan.md):** Calls `change-complete.md` at end

### Step 1: Change Creation

**Workflow Integration:** Step 1 calls `change-create.md` prompt at beginning, before plan skeleton creation

**Invocation:** Step 1 executes: "Execute change-create prompt to register this change"

**Purpose:** Separate tracking logic from plan creation logic

**change-create.md Operations:**
- Create temporary stem plan file with progressive data capture
- Determine work context (new vs existing ticket)
- Generate unique Change ID
- Collect component, milestone, description
- Add entry to CHANGES-ACTIVE.md (fetch from #98, modify, update workspace and #98)
- Rename plan file with Change ID prefix
- Return Change ID and metadata to Step 1 for skeleton creation

**Rationale:** Tracking operations isolated in reusable prompt, Step 1 focuses on plan structure

### Step 8: Change Completion

**Workflow Integration:** Step 8 calls `change-complete.md` prompt at end, after all implementation verified

**Invocation:** Step 8 executes: "Execute change-complete prompt to archive this change"

**Purpose:** Separate archival logic from implementation logic

**change-complete.md Operations:**
- Extract Change ID from plan document
- Fetch current data from issues #98 and #99
- Move change from CHANGES-ACTIVE.md to CHANGES-ARCHIVED.md
- Set Status to "Complete" with dates
- Update workspace files and issues #98 and #99
- Note implementation issue can be closed

**Rationale:** Archival operations isolated in reusable prompt, Step 8 focuses on implementation

### Lifecycle Flow Through Workflow

**Complete Change Lifecycle:**

1. **Step 1:** Calls `change-create.md` → Change ID created, registered in CHANGES-ACTIVE.md (Status: Draft) → Step 1 creates plan skeleton
2. **Step 2:** Planning work → Manual call to `change-update-status.md` to set Status: "Planning"
3. **Step 2 (complete):** Manual call to `change-update-status.md` to set Status: "Ready"
4. **Between Step 2 and 8:** Create GitHub issue → Manual update of Ticket ID in registry
5. **Step 8:** Begin implementation → Manual call to `change-update-status.md` to set Status: "In Progress"
6. **Step 8 (end):** Calls `change-complete.md` → Move to CHANGES-ARCHIVED.md (Status: Complete), update both tracking issues

**Status Transitions:**
- Draft → Planning (manual: `change-update-status.md`)
- Planning → Ready (manual: `change-update-status.md`)
- Ready → In Progress (manual: `change-update-status.md`)
- In Progress → Complete (automatic: `change-complete.md` called by Step 8)

**Alternative Paths:**
- Any status → Rejected (manual: `change-reject.md`)

### Tracking Prompts

**Called by Workflow:**
- `change-create.md` - Create and register new change (called by Step 1)
- `change-complete.md` - Complete and archive change (called by Step 8)

**Manual Operations:**
- `change-update-status.md` - Update change status between workflow steps
- `change-create-component.md` - Add new component to identification registry
- `change-reject.md` - Reject change and move to archive

### Integration with Prompt Files

**Files to Create:**
- `.github/prompts/change-create.md` - Change creation and registration
- `.github/prompts/change-complete.md` - Change completion and archival
- `.github/prompts/change-update-status.md` - Status transitions
- `.github/prompts/change-create-component.md` - Component creation
- `.github/prompts/change-reject.md` - Change rejection

**Files to Modify:**
- `.github/prompts/1-create-plan-skeleton.md` - Add call to `change-create.md` at beginning
- `.github/prompts/8-implement-from-plan.md` - Add call to `change-complete.md` at end
- `.github/instructions/planning-workflow.instructions.md` - Document change registry lifecycle in workflow overview

**Prompt Requirements:**
- Clear invocation instructions for workflow prompts
- Defined interface (what data is passed/returned)
- Error handling (duplicate IDs, missing components, etc.)
- GitHub issue synchronization to avoid merge conflicts

**Rationale:**
- Separation of concerns (workflow vs tracking)
- Reusable tracking operations
- Easier to maintain and test
- Clearer prompt responsibilities

---

## Related Documents

- [tool-add-017-change-registry-system.md](tool-add-017-change-registry-system.md) - Main plan document
- [features/CHANGES-ACTIVE.md](../CHANGES-ACTIVE.md) - Active changes registry
- [features/CHANGES-ARCHIVED.md](../CHANGES-ARCHIVED.md) - Archived changes registry
- Issue #98 - Active Changes Registry deliverable
- Issue #99 - Archived Changes Registry deliverable
- Issue #100 - Change Registry System implementation

## Source Documents

Architectural decisions extracted from:
- `features/issue-95-prompt-refinement/issue-93-multifile-structure/architecture.md` (Q1: Change Identification and Registry)
- `features/issue-95-prompt-refinement/issue-93-multifile-structure/change-identification-decision.md` (Industry practices and requirements analysis)
- Discussion and implementation work on 2026-01-01 for change registry system design
