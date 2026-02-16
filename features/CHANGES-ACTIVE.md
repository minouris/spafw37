# Active Changes Registry

**Tracking Issue:** [#98](https://github.com/minouris/spafw37/issues/98)

## Active Changes

### v1.1.0

#### Features

| Change ID | Component | Ticket ID | Description | Status |
|-----------|----------|-----------|-------------|--------|
| feat-fix-020 | feat-cycle-api | [#94](https://github.com/minouris/spafw37/issues/94) | Bug: _cycles_are_equivalent() does not normalize CYCLE_COMMAND for comparison | Planning |

### v1.2.0

#### Features

| Change ID | Component | Ticket ID | Description | Status |
|-----------|----------|-----------|-------------|--------|
| feat-add-021 | feat-log-output | [#16](https://github.com/minouris/spafw37/issues/16) | Colourful output | Planning |
| feat-add-022 | feat-param-registration | [#23](https://github.com/minouris/spafw37/issues/23) | Std-In Param (buffered mode only) | Planning |
| feat-add-023 | feat-cmd-registration | [#21](https://github.com/minouris/spafw37/issues/21) | Graceful Shutdown | Planning |

### No Milestone

#### Tools

| Change ID | Component | Ticket ID | Description | Status |
|-----------|----------|-----------|-------------|--------|
| tool-add-017 | tool-workflow | [#100](https://github.com/minouris/spafw37/issues/100) | Change Registry System (Active and Archived) | In Progress |
| tool-enh-015 | tool-workflow | [#95](https://github.com/minouris/spafw37/issues/95) | Planning Workflow Prompt Refinements Based on Issue #63 Implementation Experience | In Progress |
| tool-enh-012 | tool-workflow | [#96](https://github.com/minouris/spafw37/issues/96) | Category 2: Processing Capacity - Multi-file plan structure refinements | Planning |
| tool-ref-005 | tool-workflow | [#93](https://github.com/minouris/spafw37/issues/93) | Proposal: Split feature plan documents into multiple focused files | In Progress |

## Component Identification

### Features

| Component | Name | Description | First Milestone | Status |
|----------|------|-------------|-----------------|--------|
| feat-cmd-registration | Command Registration | Define and register commands | v1.1.0 | Active |
| feat-conf-unset | Config Unset | Un-setting configuration parameters | v1.1.0 | Active |
| feat-cycle-api | Cycles API | Top-level cycle definition API | v1.1.0 | Active |
| feat-cycle-loops | Cycle Loops | Loop start/end markers and iteration control | v1.1.0 | Active |
| feat-data-tools | Data Tools | Data processing and manipulation utilities | v1.1.0 | Active |
| feat-help-display | Help Display | Usage information and help text generation | v1.1.0 | Active |
| feat-log-errors | Error Logging | Error output and stderr handling | v1.1.0 | Active |
| feat-log-output | Logging Output | Log message output, formatting, and suppression control | v1.1.0 | Active |
| feat-param-defaults | Parameter Defaults | Default value handling and timing | v1.1.0 | Active |
| feat-param-groups | Parameter Groups | Grouped switch behaviour and parameter organization | v1.1.0 | Active |
| feat-param-prompts | User Prompts | Interactive user input and prompting | v1.1.0 | Active |
| feat-param-registration | Parameter Registration | Add and register parameters with the framework | v1.1.0 | Active |
| feat-param-validation | Parameter Validation | Allowed values, required parameters, validation rules | v1.1.0 | Active |

### Tools

| Component | Name | Description | First Milestone | Status |
|----------|------|-------------|-----------------|--------|
| tool-cicd | CI/CD | Workflows, automation, and release processes | v1.1.0 | Active |
| tool-instructions | Instructions | Copilot instructions and coding standards | v1.1.0 | Active |
| tool-workflow | Planning Workflow | Planning prompts, checklists, and workflow steps | v1.1.0 | Active |

### Documentation

| Component | Name | Description | First Milestone | Status |
|----------|------|-------------|-----------------|--------|
| docs-user | User Guides | User-facing documentation and examples | v1.1.0 | Active |

## Column Definitions

**Component Identification:**
- **Component**: Stable identifier with descriptive code (3-5 letters per hyphenated group for clarity)
- **Name**: Short component name
- **Description**: Brief description
- **First Milestone**: Version where component was introduced
- **Status**: Active (in use), Deprecated (discouraged), Removed (no longer available)

**Active Changes:**
- **Change ID**: Stable identifier in format `{subject}-{verb}-{NNN}` (e.g., `feat-add-001`, `tool-fix-003`)
  - Subjects: `feat` (feature), `tool` (tools), `docs` (documentation)
  - Verbs: `add` (add new), `enh` (enhance), `ref` (refactor), `fix` (bugfix)
  - Numbers: 3-digit sequential per subject (001-999)
- **Component**: Reference to component from identification registry above
- **Ticket ID**: GitHub issue number (links to issue when created)
- **Description**: Short description of the change
- **Status**: Current state (Draft, Planning, Ready, In Progress, Review, Complete, Rejected)

**Milestone Sections:** Changes are organized by milestone (e.g., "v1.1.0", "No Milestone"). The milestone is implicit from the section heading. The current milestone appears first, followed by "No Milestone" (for infrastructure/tooling work not tied to product releases), then other milestones chronologically.

**Note:** When a change is rejected and moved to CHANGES-ARCHIVED.md, all columns except Status are displayed with strikethrough formatting.

## Lifecycle States

- **Draft**: Initial exploration, pre-ticket creation
- **Planning**: Ticket created, detailed planning in progress
- **Ready**: Planning complete, ready for implementation
- **In Progress**: Implementation underway
- **Review**: Implementation complete, under review
- **Complete**: Merged to main branch (removed from this registry)
- **Rejected**: Proposal declined or abandoned (moved to archived with Rejected status)

## Related Files

- [CHANGES-ARCHIVED.md](CHANGES-ARCHIVED.md) - Historical archive of all completed changes

## About This Registry

This file tracks all active changes to the spafw37 project. Changes reference component IDs from the identification registries above.

**Purpose:**
- Current work in progress across all change types
- Component identification for features, tools, and documentation
- Planning pipeline for upcoming work
- Quick overview of development status
- Foundation for release planning

**Milestone Organization:** Active changes are organized with the current milestone first, followed by "No Milestone" (for infrastructure/tooling work not tied to product releases), then any other milestones in chronological order.

**When to add new components:** New components are created when an `add-*` change introduces a new area that could be subject to future enhancements, fixes, or refactoring. Subsequent changes (enh-*, fix-*, ref-*) reference existing components. Multiple `add-*` changes may reference the same component if adding to an existing area.
