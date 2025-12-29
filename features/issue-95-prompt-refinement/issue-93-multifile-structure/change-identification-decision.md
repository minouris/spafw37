# Change Identification Decision

This document analyses industry standard practices and architectural requirements for uniquely identifying work items (changes, features, bugs) in the spafw37 planning workflow.

**Focus:** Work item tracking and identification, not software release versioning.

## Table of Contents

1. [Architectural Requirements](#architectural-requirements)
   - [Project Constraints](#project-constraints)
   - [Multi-Developer Scenario Challenges](#multi-developer-scenario-challenges)
   - [Requirements for Identifier Scheme](#requirements-for-identifier-scheme)
2. [Core Work Item Identification Schemes](#core-work-item-identification-schemes)
   - [1. Issue Tracking System IDs](#1-issue-tracking-system-ids)
   - [2. SAFe Hierarchical Work Items](#2-safe-hierarchical-work-items)
   - [3. Kanban Card Identification](#3-kanban-card-identification)
   - [4. Hierarchical Descriptive Names](#4-hierarchical-descriptive-names)
   - [5. Context-Aware Identifiers](#5-context-aware-identifiers)
   - [6. Developer Namespace Schemes](#6-developer-namespace-schemes)
3. [Analysis](#analysis)
   - [Summary: Tradeoffs Matrix](#summary-tradeoffs-matrix)
   - [Key Insights from Agile/SAFe/Kanban](#key-insights-from-agilesafekanban)
4. [Decision Analysis](#decision-analysis)
5. [Appendix A: Software Release Versioning Schemes](#appendix-a-software-release-versioning-schemes)

**Referenced by:** [architecture.md - Q1: Change Identification and Registry](architecture.md#q1-change-identification-and-registry)

---

## Architectural Requirements

### Project Constraints

**Critical Stipulation:** We cannot start work on a change without a ticket (and therefore a ticket ID to link the work to), but we should not create empty tickets in the ticketing system.

**Complexity: Request vs. Implementation Tickets**

There is an important distinction between request tickets and implementation tickets:
- **Request tickets** (external): Describe problems or desired outcomes from user perspective (bug reports, feature requests)
- **Implementation tickets** (internal): Describe changes to the codebase (bugfixes, features, enhancements)

**Implications:**
- Multiple request tickets may be addressed by one implementation ticket
- One request ticket may require multiple implementation tickets
- Implementation tickets are what get planned and executed
- Changes (implementations) need an identity that may be independent of request ticket IDs

**Scalability Requirement:** The naming scheme must work for both small teams and large organisations. Very formal processes that are necessary for large organisations add overhead that, when not required, are cumbersome for smaller teams.

**Design Goal:** Support both lightweight workflows (small teams) and formal processes (large organisations) without forcing unnecessary overhead on either.

**AI Agent Requirement:** For the AI agent to correctly create and track change planning, it must know:
1. What identification scheme is being used
2. What is being used to track change identifiers (registry file, issue list, directory scan, etc.)
3. How to create new identifiers without collisions
4. How to resolve what identifiers already exist

This means any scheme must be:
- **Well-defined:** Documented in prompts/instructions
- **Discoverable:** AI can query what identifiers exist
- **Programmatic:** AI can generate valid new identifiers
- **Collision-resistant:** AI can detect/avoid duplicates

**Configuration Storage:** The project-wide decision about which scheme to use should be stored in a project configuration file. This configuration file (tracked in [minouris/prompt-driven-development#31](https://github.com/minouris/prompt-driven-development/issues/31)) informs planning prompts which configurable behaviors to use.

### Scope

**For Issue #93 (This Project - spafw37):**
- Design ONE identification scheme suitable for spafw37's needs
- Define how AI discovers existing identifiers
- Define how AI generates new identifiers without collisions
- Implement that scheme in Step 1 prompt

**Out of Scope:** 
- Multiple scheme designs for general framework use
- Project configuration file integration
- Scheme flexibility across different project scales

These wider concerns are tracked in [minouris/prompt-driven-development#71](https://github.com/minouris/prompt-driven-development/issues/71)

### Multi-Developer Scenario Challenges

With multiple developers working concurrently:
- **Numeric IDs**: Almost certain to create conflicts when developers independently assign sequential numbers
- **Short GUIDs**: Collision-resistant but difficult to reference in shorthand (not memorable)
- **Datetime-based**: Possible collisions if two developers create plans at same time
- **Developer prefix + sequence**: Requires coordination, still has collision risk
- **Issue numbers**: Solves collision problem by centralizing ID assignment

### Requirements for Identifier Scheme

1. **Collision-resistant**: Works with multiple concurrent developers
2. **Human-friendly**: Easy to reference in conversation and documentation
3. **Sortable**: Ideally chronological or logical ordering
4. **Short enough**: Usable in file names and branch names
5. **Issue-linked**: Must connect to GitHub issue (cannot be independent of external systems)
6. **No premature ticketing**: Cannot require creating empty tickets

**Resolution:** Given the constraint "cannot start work without a ticket," issue numbers become the natural identifier. The question becomes: what format when issue exists?

**Options under consideration:**
- `issue-{N}-{descriptive-name}` (current approach)
- `{N}-{descriptive-name}` (shorter)
- `issue-{N}` only (minimal, description in metadata)

---

---

## Table of Contents

### Core Work Item Identification Schemes
1. [Issue Tracking System IDs](#1-issue-tracking-system-ids)
2. [SAFe Hierarchical Work Items](#2-safe-hierarchical-work-items)
3. [Kanban Card Identification](#3-kanban-card-identification)
4. [Hierarchical Descriptive Names](#4-hierarchical-descriptive-names)
5. [Context-Aware Identifiers](#5-context-aware-identifiers)
6. [Developer Namespace Schemes](#6-developer-namespace-schemes)

### Analysis
7. [Summary: Tradeoffs Matrix](#summary-tradeoffs-matrix)
8. [Key Insights from Agile/SAFe/Kanban](#key-insights-from-agilesafekanban)
9. [Recommendations for This Project](#recommendations-for-this-project)

### Appendix
- [Appendix A: Software Release Versioning Schemes](#appendix-a-software-release-versioning-schemes)

---

## 1. Issue Tracking System IDs

**Format:** `PROJECT-NUMBER` (e.g., `JIRA-1234`, `GH-93`)

**Collision Avoidance:** Centralized system assigns sequential IDs

**Human-Friendly:** Yes - short, memorable, project-scoped

**Usage:**
- Jira issues
- GitHub issues
- Linear tickets
- Azure DevOps work items

**Strengths:**
- Automatically assigned by system
- Guaranteed unique within project
- Human-friendly and memorable
- Bidirectional linking (commit ↔ issue)
- Rich metadata (assignee, status, comments)

**Weaknesses:**
- Requires issue to exist before getting number
- Can't create plan before issue (chicken-egg problem)
- External dependency on tracking system

**Source:** [Atlassian Jira Documentation](https://community.atlassian.com/t5/Jira-Software-articles/The-Ultimate-Jira-Setup-Guide-2025/ba-p/2955217)

[↑ Back to top](#table-of-contents)

---

## 2. SAFe Hierarchical Work Items

**Format:** Hierarchical naming (Epic > Feature > Story)

**Collision Avoidance:** Relies on external system (Jira, Azure DevOps) to assign unique IDs

**Human-Friendly:** Yes - descriptive names with hierarchy

**Structure:**
- **Portfolio Epic**: Large strategic initiatives (months to years)
- **Program Epic/Capability**: Cross-team efforts (multiple PIs)
- **Feature**: Team-level deliverables (1-2 Program Increments)
- **Story**: Small work items (1 iteration/sprint)

**Typical Identification:**
- Each level has its own ID from tracking system
- Hierarchy shown by parent-child relationships
- Example: Epic PLATFORM-123 contains Feature FEAT-456 contains Story STORY-789

**Strengths:**
- Clear scope hierarchy
- Well-suited for large organisations
- Explicit value stream mapping
- Standardised methodology

**Weaknesses:**
- Requires tracking system for ID assignment
- Heavy process overhead
- Doesn't solve pre-issue creation problem
- Multiple levels can be confusing

**Source:** [SAFe Work Breakdown Structure](https://www.ndia.org/-/media/sites/ndia/meetings-and-events/2017/april/7a01---agile-in-government/miller.ashx), [Atlassian SAFe Guide](https://www.atlassian.com/agile/agile-at-scale/what-is-safe)

[↑ Back to top](#table-of-contents)

---

## 3. Kanban Card Identification

**Format:** Descriptive title + optional Task ID

**Collision Avoidance:** Optional - Task ID if cross-tool tracking needed

**Human-Friendly:** Yes - emphasizes clear, descriptive titles

**Card Fields (Typical):**
- Title (required)
- Owner (required)
- Description (required)
- Task ID (optional - for cross-system tracking)
- Priority tags/colors
- Size (T-shirt or Fibonacci)

**Philosophy:**
- Focus on flow, not tracking numbers
- Identification by description and owner
- Metrics focus: lead time, cycle time, throughput
- Pull-based (WIP limits), not assignment-based

**Strengths:**
- Lightweight - no mandatory numbering
- Optimizes for flow over tracking
- Clear visual prioritization
- Works well with continuous delivery

**Weaknesses:**
- No built-in collision prevention
- Harder to reference specific items in discussion
- Optional Task ID still requires external system
- Not suitable for audit trails or formal documentation

**Source:** [Wrike Kanban Guide](https://www.wrike.com/kanban-guide/kanban-cards/), [Atlassian Kanban Cards](https://www.atlassian.com/agile/kanban/cards)

[↑ Back to top](#table-of-contents)

---

## 4. Hierarchical Descriptive Names

**Format:** `{scope}/{type}/{descriptive-name}` (e.g., `platform/feature/multifile-structure`)

**Collision Avoidance:** Namespace scoping reduces collisions

**Human-Friendly:** Yes - self-documenting hierarchy

**Examples:**
- `cycles/feature/cycle-storage-api`
- `prompts/enhancement/step-8-clarity`
- `config/bugfix/param-defaults-timing`

**Strengths:**
- No external system required
- Self-documenting hierarchy
- Filesystem-friendly (matches directory structures)
- Easy to filter and search

**Weaknesses:**
- Same-scope collisions still possible
- Longer names for deep hierarchies
- Requires discipline in naming conventions

[↑ Back to top](#table-of-contents)

---

## 5. Context-Aware Identifiers

**Format:** Changes identifier format based on context

**Strategy:**
- Issue exists → use issue number: `issue-93-multifile-structure`
- No issue yet → descriptive: `feature-multifile-structure`
- Multiple parallel features → add timestamp: `20251229-multifile-structure`

**Collision Avoidance:** Context-dependent

**Human-Friendly:** Yes - adapts to situation

**Strengths:**
- Flexible - supports both workflows
- Uses best identifier for each situation
- No premature coordination needed
- Graceful degradation

**Weaknesses:**
- Inconsistent naming patterns
- Requires naming convention documentation
- May need renaming when issue created
- Harder to enforce in tooling

[↑ Back to top](#table-of-contents)

---

## 6. Developer Namespace Schemes

**Format:** `DEV-SEQ` (e.g., `alice-001`, `bob-003`)

**Collision Avoidance:** Developer-scoped namespaces

**Human-Friendly:** Yes - shows ownership

**Strengths:**
- Collision-resistant within developer scope
- Shows who created the change
- Simple sequential numbering

**Weaknesses:**
- Requires developer identification
- Coordination needed for sequence within developer
- Harder to reassign ownership

[↑ Back to top](#table-of-contents)

---

## Summary: Tradeoffs Matrix

| Scheme | Collision-Resistant | Human-Friendly | Sortable | Pre-Issue Creation | Notes |
|--------|-------------------|----------------|----------|-------------------|-------|
| Issue IDs | ✅ | ✅ | ✅ | ❌ | Requires issue first |
| SAFe Hierarchy | ✅ | ✅ | ⚠️ | ❌ | Requires tracking system |
| Kanban Cards | ❌ | ✅ | ❌ | ✅ | Lightweight, optional IDs |
| Hierarchical Names | ⚠️ | ✅ | ⚠️ | ✅ | Namespace scoping |
| Context-Aware | Varies | ✅ | Varies | ✅ | Adapts to situation |
| Developer + Seq | ✅ | ✅ | ⚠️ | ✅ | Developer-scoped only |

[↑ Back to top](#table-of-contents)

---

## Key Insights from Agile/SAFe/Kanban

### 1. Hierarchy Over Flat Numbering
SAFe demonstrates that hierarchical structures (Epic > Feature > Story) provide better organisation than flat sequential numbering, especially in larger contexts.

**Application:** Could use hierarchical folder structure with scope-based naming (e.g., `prompts/step-8/clarity-improvements`)

### 2. Flow Over Tracking
Kanban philosophy prioritizes flow metrics (lead time, cycle time) over unique identifiers. Task IDs are optional - descriptions and owners are sufficient for most workflows.

**Application:** Consider whether unique identifiers are actually necessary, or if descriptive names + owner + status are sufficient for this project's scale.

### 3. Lightweight Identification
Kanban cards show that minimal required fields (title, owner, description) are often enough. Additional identifiers add value only when they enable specific capabilities (cross-system tracking, auditing, formal documentation).

**Application:** Start with simplest viable identification, add complexity only when needed.

### 4. Context-Dependent Granularity
SAFe shows different levels need different identification granularity:
- Portfolio level: Long-term identifiers (years)
- Program level: Medium-term (quarters/PIs)
- Team level: Short-term (sprints/iterations)

**Application:** Different change types may need different identification strategies (major features vs. bug fixes).

### 5. Pull-Based vs. Assignment-Based
Kanban's pull model means work items don't need pre-assignment. They're identified when pulled from backlog.

**Application:** Changes could be identified at creation time without requiring pre-coordination or central registry.

[↑ Back to top](#table-of-contents)

---

## Decision Analysis

### Impact of Constraint on Options

Given the constraint "cannot start work without a ticket," several approaches become infeasible:

- ~~**Pure descriptive names:**~~ Requires work without ticket, violates constraint
- ~~**Context-aware identifiers:**~~ "no issue yet" case is not allowed
- ~~**Developer namespace:**~~ Still requires independent ID assignment, doesn't leverage ticket system

### Remaining Options

With issues created before work begins, format options include:

**Option A: `issue-{N}-{descriptive-name}`**
- Folder: `features/issue-93-multifile-structure/`
- Branch: `feature/issue-93-multifile-structure`
- Strengths: Human-friendly, self-documenting
- Weaknesses: Longer names

**Option B: `{N}-{descriptive-name}`**
- Folder: `features/93-multifile-structure/`
- Branch: `feature/93-multifile-structure`
- Strengths: Shorter
- Weaknesses: Less clear what "93" refers to

**Option C: `issue-{N}` only**
- Folder: `features/issue-93/`
- Branch: `feature/issue-93`
- Strengths: Minimal, consistent
- Weaknesses: Not self-documenting, requires looking up issue for context

### Common Strengths (All Options)

- **Collision-resistant**: GitHub assigns unique sequential IDs
- **Bidirectional linking**: Folder ↔ issue ↔ branch ↔ PR
- **No premature ticketing**: Issue is meaningful (has title, description) before work begins
- **Sortable**: Issue numbers provide rough chronological order

### Industry Alignment

Issue-first workflow aligns with:
- **Jira/Linear/GitHub Issues**: Standard issue tracking workflow
- **SAFe**: Work items have IDs before development begins
- **Kanban**: Task IDs optional, but when required, assigned before work starts

### Decision

[PENDING - user to select option A, B, or C]

[↑ Back to top](#table-of-contents)

---

## Appendix A: Software Release Versioning Schemes

These schemes are primarily for software release versioning rather than work item identification. They're included for completeness but are less relevant to the change identification problem.

### A.1 Semantic Versioning (SemVer)

**Format:** `MAJOR.MINOR.PATCH` (e.g., `2.1.4`)

**Usage:** Python packages, npm packages, software releases

**Purpose:** Communicates API compatibility changes

**Not suitable for:** Individual work item identification before release

### A.2 Calendar Versioning (CalVer)

**Format:** `YEAR.MONTH` or `YEAR.WEEK.SEQUENTIAL` (e.g., `2025.12`)

**Usage:** pip, Ubuntu releases, monorepo automated versioning

**Purpose:** Conveys age of release

**Not suitable for:** Pre-release work item identification

### A.3 Git-Based Identifiers

**Format:** `SHA` or `short-SHA` (e.g., `abc1234`)

**Usage:** Git commits, setuptools-scm

**Purpose:** Unique commit identification

**Not suitable for:** Human-friendly work item references

### A.4 Conventional Commits

**Format:** `type(scope): description` (e.g., `feat(cycles): add cycle storage API`)

**Usage:** Git commit messages, changelog generation

**Purpose:** Structured commit messages for automation

**Not suitable for:** Unique work item identification (names may collide)

### A.5 Feature Flags

**Format:** Feature flag keys (e.g., `enable_cycles_api`)

**Usage:** Google monorepo, Meta, Shopify deployments

**Purpose:** Continuous deployment with incomplete features

**Not suitable for:** Tracking planning artifacts

[↑ Back to top](#table-of-contents)
