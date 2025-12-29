# Architectural Decisions: Multi-File Plan Structure

This document tracks architectural decisions and design discussions for Issue #93.

## Table of Contents

1. [Glossary](#glossary)
2. [Step 1: Create Plan Skeleton](#step-1-create-plan-skeleton)
   - [Current Behaviour](#current-behaviour)
   - [Required Changes](#required-changes)
   - [Questions Requiring User Input](#questions-requiring-user-input)
     - [Q1: Change Identification and Registry](#q1-change-identification-and-registry)
     - [Q2: Ticket/Folder Timing](#q2-ticketfolder-timing-two-valid-workflows)
     - [Q3: Feature Type Variations](#q3-feature-type-variations)
     - [Q4: Stub File Content](#q4-stub-file-content)
     - [Q5: Main File Population](#q5-main-file-population)
   - [Open Discussion Topics](#open-discussion-topics)

---

## Glossary

| Term | Variable Form | Definition |
|------|---------------|------------|
| **Architecture-first workflow** | N/A | Development workflow where plan documents are created before tickets, typically for planned features or architectural changes. |
| **Bug fix** | `{bugfix}` | A change that corrects incorrect behaviour in existing code. |
| **Change** | `{change}` | A unit of work that modifies the codebase. Encompasses features, enhancements, and bug fixes. Domain-independent term that remains distinct from ticket-tracking terminology (issue, ticket). |
| **Change type** | `{change-type}` | The category of change being made. Can expand to: `feature`, `bugfix`, `enhancement`, `refactor`, or other project-defined types. Used in change ID format. |
| **Enhancement** | `{enhancement}` | A change that improves or extends existing functionality without adding entirely new capabilities. |
| **Feature** | `{feature}` | A change that adds new functionality or capabilities to the codebase. |
| **Issue** | `{issue}` | A GitHub issue that tracks a change. May be created before or after the plan document, depending on workflow. |
| **Issue name** | `{issue-name}` | The descriptive name portion of an issue (e.g., "multifile-structure"). |
| **Issue number** | `{issue-number}` | The numeric identifier assigned by GitHub to an issue (e.g., 93). |
| **Ticket-first workflow** | N/A | Development workflow where tickets are created first (by third parties or during other work), then plan documents are created in response. |
| **Plan** | `{plan}` | A structured set of documents describing what will be changed, why, and how. Located in `features/` directory. |
| **Ticket** | `{ticket}` | Generic term for a tracked unit of work in ticket-tracking systems. In this project, tickets are implemented as GitHub issues. |
| **Workflow** | N/A | The sequence of steps followed when planning and implementing a change. |

---

## Step 1: Create Plan Skeleton

### Current Behaviour

Creates a single monolithic plan file with placeholder sections:
- Overview
- Table of Contents
- Further Considerations
- Success Criteria
- Implementation Steps
- Documentation Changes
- Changes

### Required Changes

Step 1 needs to create a multi-file structure:

```
features/
  issue-{N}-{name}/
    issue-{N}-{name}.md              # Main file
    overview.md                       # Detailed background (stub)
    architectural-decisions.md        # Step 2 output (stub)
    success-criteria.md              # Step 3 output (stub)
    changes.md                        # Step 6 output (stub)
    planning-checklist.md            # Step 7 tracking (stub)
    implementation-steps/            # Directory (empty initially)
    implementation-checklist.md      # Step 4 tracker (stub)
    implementation-log.md            # Step 8 log (stub)
```

### Questions Requiring User Input

#### Q1: Change Identification and Registry

**Problem:** How do we uniquely identify changes across multiple files, developers, and time?

**Critical Constraint:** A ticket should only be created when the change has been at least somewhat described. We cannot start work without a ticket, but should not create empty tickets.

**Universal Requirement: Single Point of Truth**

Regardless of project scale, change identifiers must have a single point of truth. This must be a ticket (GitHub issue) so it is freely accessible regardless of which branch a developer is on.

**Tracker Ticket Format:**

The most basic form is a GitHub issue containing a table:

| Change ID | Ticket ID | Description | Milestone | Opened | Closed | Status |
|-----------|-----------|-------------|-----------|--------|--------|--------|
| bugfix-0001 | #47 | Fix config timing | v1.2.0 | 2025-12-15 | | Pending |
| feature-0001 | #45 | Add cycles API | v1.1.0 | 2025-12-01 | | In Progress |
| refactor-0001 | #93 | Multi-file plan structure | v1.2.0 | 2025-12-29 | | Planning |

- **Change ID**: Human-readable identifier (alphabetically sortable)
- **Ticket ID**: GitHub issue number for implementation ticket (when created)
- **Description**: Short description of the change
- **Milestone**: Target release version
- **Opened**: Date the ticket was created (YYYY-MM-DD format)
- **Closed**: Date the ticket was closed (empty if still open)
- **Status**: Current status (Planning, In Progress, Complete, etc.)
- **Sorted**: Alphabetically by Change ID

**Scalability:** Larger projects may break this down into sub-tickets:
- Version-specific trackers (e.g., "Changes for v2.0.0")
- Epic-specific trackers (e.g., "Changes for Cycles Feature")
- Scope depends on project size and formality requirements

**Rationale:**
- Branch-independent: Accessible from any branch without switching
- Always available: No merge conflicts or branch sync issues
- Collaborative: Multiple developers can access simultaneously
- Persistent: Survives branch deletion
- Discoverable: AI can query GitHub API for tracker ticket(s)

**Implication:** Changes must have implementation tickets. The identifier is the ticket number. The scheme question becomes: how do we structure/format these implementation tickets?

**Complexity: Request vs. Implementation Tickets**

The distinction between request tickets (external) and implementation tickets (internal) reveals that changes need an identity independent of request ticket IDs:
- Multiple request tickets may be addressed by one implementation
- One request ticket may require multiple implementations
- Implementation tickets describe the actual change to the codebase

**Scalability Consideration:** This naming scheme must work for both small teams and large organisations. Overly formal processes necessary for large organisations add overhead that is cumbersome for smaller teams when not required.

**AI Agent Requirement:** For the AI agent to correctly create and track change planning, it must know:
1. How to query GitHub for existing implementation tickets
2. How to create new implementation tickets
3. How to distinguish implementation tickets from request tickets
4. What format/structure implementation tickets should have

**Configuration Storage:** The project-wide decision about implementation ticket format should be stored in the project configuration file (tracked in [minouris/prompt-driven-development#31](https://github.com/minouris/prompt-driven-development/issues/31)).

**Scope for Issue #93:** 
- Design ONE implementation ticket format for this project (spafw37)
- Define how AI queries GitHub for existing implementation tickets
- Define how AI creates new implementation tickets
- Implement support for that format in Step 1 prompt

**Out of Scope:** General framework design for multiple schemes tracked in [minouris/prompt-driven-development#71](https://github.com/minouris/prompt-driven-development/issues/71)

**Decision for spafw37:**

As a small, single-developer project, we adopt a simple sequential scheme:

**Change ID Format:** `{change-type}-{NNNN}`

Where:
- `{change-type}` = Type of change (`feature`, `bugfix`, `enhancement`, `refactor`, etc.)
- `{NNNN}` = Left-padded four-digit sequential number (0001, 0002, 0003, ...)

**Examples:**
- `feature-0001` - First feature
- `bugfix-0001` - First bugfix
- `enhancement-0001` - First enhancement
- `refactor-0001` - First refactor

**Rationale:**
- **No collision risk:** Single developer means no concurrent ID assignment
- **Simple:** Easy to understand and remember
- **Sortable:** Alphabetical sort groups by type, then by sequence
- **Scalable:** Can accommodate up to 9,999 changes per type
- **Discoverable:** AI can query existing IDs from tracker ticket table
- **Type-scoped sequences:** Each change type has its own sequence, avoiding confusion between feature-0001 and bugfix-0001

**Implementation Ticket Identification:**
- Implementation tickets are distinguished by having a Change ID in the tracker ticket
- AI queries tracker ticket to discover existing Change IDs
- AI generates next sequential number for the given change type
- Tracker ticket maintained as GitHub issue with table format (shown above)

**User Decision:** [RESOLVED]

**Full Analysis:** See [change-identification-decision.md](change-identification-decision.md) for industry research, architectural requirements, and alternative approaches considered.

---

#### Q2: Ticket/Folder Timing (Two Valid Workflows)

**Problem:** When do we create the ticket versus the plan folder?

**Note:** This question depends on Q1 (naming format decision).

**Critical Constraint:** A ticket should only be created when the change has been at least somewhat described. We cannot start work without a ticket, but should not create empty tickets.

**Two Valid Workflows:**

##### Workflow A: External Tickets
- **Context:** Tickets created by users, external parties, or other stakeholders
- **Process:** External party creates ticket → developer reviews and refines → create plan folder → implement change
- **Description timing:** At point of creation (may be refined by developer)
- **Examples:**
  - **Bug reports**: User reports a problem
  - **Feature requests**: User requests new functionality
  - **Enhancement requests**: User suggests improvements to existing features
  - **Support issues**: User encounters problems that may require code changes
- **Important distinction: Request vs. Implementation**
  - **Request tickets** (external): Describe problems or desired outcomes from user perspective
  - **Implementation tickets** (internal): Describe changes to the codebase
  - Examples:
    - "Bug report" ticket → "Bugfix" ticket
    - "Feature request" ticket → "Feature" ticket
    - "Enhancement request" ticket → "Enhancement" ticket
  - Multiple request tickets may be addressed by a single implementation ticket
  - One request ticket may require multiple implementation tickets
- **Use cases:** User-reported bugs, community feature requests, external enhancement suggestions

##### Workflow B: Internal Tickets (Architecture-First)
- **Context:** Features or enhancements as part of internal architecture effort
- **Process:** Architecture/design work → iterate on description → create ticket with description → create plan folder → continue detailed planning
- **Description timing:** During architecture process (before ticket creation)
- **Key insight:** Description happens during design iterations, then ticket is created once sufficiently described
- **Use cases:** Major features, architectural changes, planned enhancements

**Implication for Workflow B:** 
If description/design happens before ticket creation, where do those artifacts live? Options:
- In a temporary location (e.g., local files, scratch area)
- In architecture.md-style discussion documents
- Directly in ticket draft (unpublished)

**User Decision:** [PENDING - need to decide on artifact location for pre-ticket architecture work]

---

#### Q3: Feature Type Variations

**Problem:** Not all features need all files.

**Examples:**
- **Tracker issues** (#95): No implementation-steps/, no success-criteria.md
- **Documentation-only**: No implementation-steps/
- **Bug fixes**: May not need architectural-decisions.md

**Options:**
- **A)** Always create full structure, delete unused files later
- **B)** Accept a "feature type" parameter and create appropriate subset
- **C)** Create minimal structure, let later steps add files as needed

**User Decision:** [PENDING]

**Rationale:** [To be documented after decision]

---

#### Q4: Stub File Content

**Problem:** What should stub files contain?

**Options:**
- **A)** Just a heading (e.g., "# Overview")
- **B)** Heading + template structure with placeholders
- **C)** Heading + instructions for what to populate in that step

**User Decision:** [PENDING]

**Rationale:** [To be documented after decision]

---

#### Q5: Change Identification and Registry

**Problem:** How do we uniquely identify changes across multiple files, developers, and time?

**Critical Constraint:** Cannot start work on a change without a ticket (need ticket ID), but should not create empty tickets in the ticketing system.

**Implication:** This constraint affects identifier options - GitHub issue numbers provide collision-resistant IDs since issues must exist before work begins. The question becomes: what format when issue exists?

**Options under consideration:**
- `issue-{N}-{descriptive-name}` (current approach)
- `{N}-{descriptive-name}` (shorter)
- `issue-{N}` only (minimal, description in metadata)

**User Decision:** [PENDING - need to decide on format]

**Full Analysis:** See [change-identification-decision.md](change-identification-decision.md) for industry research, architectural requirements, and alternative approaches considered.

---

#### Q5: Main File Population

**Problem:** How much should Step 1 populate the main file (`issue-{N}-{name}.md`)?

**Options:**
- **A)** Full structure (overview summary, ToC, status) but placeholder text
- **B)** Just the header and issue link, rest added by later steps
- **C)** Complete ToC with links to all files (even if stubs)

**User Decision:** [PENDING]

**Rationale:** [To be documented after decision]

---

### Open Discussion Topics

[Additional topics to be added as discussion progresses]
