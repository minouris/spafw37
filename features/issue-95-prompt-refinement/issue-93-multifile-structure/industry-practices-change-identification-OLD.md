# Industry Standard Practices: Change Identification Schemes

This document surveys industry standard practices for uniquely identifying work items (changes, features, bugs) in software development, particularly in multi-developer and distributed team contexts.

**Focus:** Work item tracking and identification, not software release versioning.

## Referenced by

[architecture.md - Q5: Change Identification and Registry](architecture.md#q5-change-identification-and-registry)

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

### Appendix: Release Versioning Schemes
- [Appendix A: Software Release Versioning](#appendix-a-software-release-versioning)

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

## 5. Conventional Commits

**Format:** `type(scope): description` (e.g., `feat(cycles): add cycle storage API`)

**Collision Avoidance:** None - descriptive names may collide

**Human-Friendly:** Yes - self-documenting

**Usage:**
- Git commit messages
- Changelog generation
- Semantic release automation

**Strengths:**
- Self-documenting
- Enables automated changelog generation
- Communicates intent and scope
- Works with existing Git workflow

**Weaknesses:**
- Not unique identifiers (multiple features can have similar names)
- No collision prevention
- Requires developer discipline

**Source:** [Conventional Commits Specification](https://dev.to/itxshakil/commit-like-a-pro-a-beginners-guide-to-conventional-commits-34c3)

[↑ Back to top](#table-of-contents)

---

## 6. Trunk-Based Development with Feature Flags

**Format:** Feature flag keys (e.g., `enable_cycles_api`)

**Collision Avoidance:** String-based namespacing

**Human-Friendly:** Yes - descriptive names

**Usage:**
- Google monorepo
- Meta internal tools
- Shopify deployments

**Strengths:**
- Enables continuous deployment with incomplete features
- Features identified by purpose, not number
- Works well with monorepos
- No coordination needed for naming

**Weaknesses:**
- Flags accumulate over time (cleanup required)
- Naming collisions possible
- Not suitable for tracking planning artifacts

**Source:** [Graphite - Monorepo Branching Strategies](https://graphite.com/guides/branching-strategies-monorepo)

[↑ Back to top](#table-of-contents)

---

## 7. Hybrid Schemes

### 7a. Timestamp + Descriptor

**Format:** `YYYYMMDD-descriptive-name` (e.g., `20251229-multifile-structure`)

**Collision Avoidance:** Same-day collisions require manual resolution

**Human-Friendly:** Yes - sortable and descriptive

**Strengths:**
- Chronological sorting
- Descriptive names
- Mostly collision-resistant

**Weaknesses:**
- Same-day collisions possible
- Timestamp not meaningful for long-running work

### 7b. Developer Namespace + Sequential

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

## 8. Agile/SAFe Hierarchical Work Items

### 8a. SAFe Work Breakdown Structure

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

### 8b. Kanban Card Identification

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

## 9. Hybrid Agile Approaches

### 9a. Hierarchical Descriptive Names

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

### 9b. Context-Aware Identifiers

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

## Summary: Tradeoffs Matrix

| Scheme | Collision-Resistant | Human-Friendly | Sortable | Pre-Issue Creation | Notes |
|--------|-------------------|----------------|----------|-------------------|-------|
| SemVer | ❌ | ✅ | ✅ | ❌ | Requires coordination |
| CalVer | ⚠️ (with seq) | ✅ | ✅ | ✅ | Needs sequential component |
| Git SHA | ✅ | ❌ | ❌ | ✅ | Not memorable |
| Issue IDs | ✅ | ✅ | ✅ | ❌ | Requires issue first |
| Conventional Commits | ❌ | ✅ | ❌ | ✅ | Not unique |
| Feature Flags | ⚠️ | ✅ | ❌ | ✅ | Naming collisions possible |
| Timestamp + Name | ⚠️ | ✅ | ✅ | ✅ | Same-day collisions |
| Developer + Seq | ✅ | ✅ | ⚠️ | ✅ | Developer-scoped only |
| SAFe Hierarchy | ✅ | ✅ | ⚠️ | ❌ | Requires tracking system |
| Kanban Cards | ❌ | ✅ | ❌ | ✅ | Lightweight, optional IDs |
| Hierarchical Names | ⚠️ | ✅ | ⚠️ | ✅ | Namespace scoping |
| Context-Aware | Varies | ✅ | Varies | ✅ | Adapts to situation |

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

## Recommendations for This Project

Based on industry practices, possible approaches:

1. **Issue-first workflow:** Use GitHub issue numbers when available, descriptive names otherwise
2. **Hybrid approach:** `{issue-number}-{descriptive-name}` when issue exists, `{descriptive-name}` when architecture-first
3. **CalVer-inspired:** `YYYYWW.SEQ-{name}` with weekly sequence reset
4. **Pure descriptive:** Use only descriptive names, track issue numbers in metadata

Each has tradeoffs between collision resistance, human-friendliness, and workflow support.

[↑ Back to top](#table-of-contents)
