# Issue #100 Analysis: Change Registry System

**Date:** 2026-02-16
**Branch:** feature/issue-100-change-registry-system
**Current State:** In Progress (not ready for main)

## Executive Summary

Issue #100 is implementing a change tracking system independent of GitHub issues. The system is partially implemented with core registry files created but workflow integration not yet complete. The branch should NOT be merged to main in its current state.

## What's Been Completed

### 1. Core Registry Files (✅ Complete)
- `features/CHANGES-ACTIVE.md` - Tracks active work with 1 feature + 4 tools currently listed
- `features/CHANGES-ARCHIVED.md` - Historical record of 32 completed changes from v1.1.0
- Change ID system: `{subject}-{verb}-{NNN}` format (e.g., `feat-add-001`, `tool-fix-013`)
- Component identification system: 14 components defined
- GitHub labels synchronized with component names

### 2. Planning Documentation (✅ Complete)
- Main plan: `features/tool-add-017-change-registry-system/tool-add-017-change-registry-system.md`
- Architecture decisions: `architecture.md` (546 lines)
- Implementation details: `implementation-details.md`
- 8 detailed step files for implementing workflow prompts

### 3. Updated Active Registry (✅ Complete - just now)
- Added v1.2.0 section with 3 new change IDs (feat-add-021, 022, 023)
- Properly organized milestones: v1.1.0, v1.2.0, No Milestone

## What's NOT Complete (❌ Blockers)

### 1. Workflow Prompt Integration (Not Started)
The plan calls for 5 new prompts + modifications to 2 existing prompts:
- `change-create.md` - Create and register new changes
- `change-complete.md` - Move changes to archived registry
- `change-update-status.md` - Update change status in registry
- `change-create-component.md` - Define new component IDs
- `change-reject.md` - Mark changes as rejected
- Modifications to `1-create-plan-skeleton.md` and `8-implement-from-plan.md`

**Impact:** Without these prompts, the change registry system can't be used in the workflow.

### 2. Documentation Updates (Not Started)
- `planning-workflow.instructions.md` needs update for new prompts

### 3. Integration Testing (Not Started)
- No testing of the workflow with the new prompts

## Instruction Files: .bak vs Active

### Files in `.github/instructions.bak/` (7 files, ~2,651 lines)

1. **planning.instructions.md** (912 lines)
   - Issue planning document structure
   - Program flow analysis section format
   - Changes documentation format
   - VERY detailed with extensive examples

2. **mermaid.instructions.md** (726 lines)
   - Mermaid diagram syntax and examples
   - Extensive diagram type coverage

3. **documentation.instructions.md** (350 lines)
   - Markdown standards
   - Documentation structure guidelines

4. **general.instructions.md** (235 lines)
   - NO GUESSING POLICY
   - UK English/localization rules
   - Git operations policy
   - Communication style
   - Documentation requirements

5. **architecture.instructions.md** (235 lines)
   - Architecture document standards
   - Design decision documentation

6. **issue-workflow.instructions.md** (131 lines)
   - Starting work on issues
   - Branch naming conventions
   - Plan document creation

7. **bash.commands.instructions.md** (57 lines)
   - Shell command best practices

### Files in `.github/instructions/` (9 files, ~1,874 lines)

The active instructions are MORE FOCUSED and SPLIT into smaller files:

1. **plan-structure.instructions.md** (435 lines)
   - Extracted from planning.instructions.md
   - Plan document structure only

2. **python.instructions.md** (475 lines)
   - Python coding standards
   - Anti-patterns and examples

3. **python-tests.instructions.md** (265 lines)
   - Test structure standards

4. **python37.instructions.md** (166 lines)
   - Python 3.7 compatibility

5. **planning-workflow.instructions.md** (222 lines)
   - Workflow step invocation
   - Extracted from planning.instructions.md

6. **accuracy.instructions.md** (123 lines)
   - NO GUESSING POLICY
   - Extracted from general.instructions.md

7. **communication.instructions.md** (49 lines)
   - Communication style
   - Extracted from general.instructions.md

8. **git-operations.instructions.md** (52 lines)
   - Git policies
   - PR review requirements
   - Extracted from general.instructions.md

9. **code-review-checklist.instructions.md** (92 lines)
   - Pre-commit verification
   - NEW file, not in .bak

### Key Differences

#### What's MISSING from Active Instructions (moved to .bak)
1. **issue-workflow.instructions.md** - How to start work on an issue
2. **documentation.instructions.md** - Markdown/docs standards
3. **architecture.instructions.md** - Architecture document standards
4. **bash.commands.instructions.md** - Shell command guidelines
5. **mermaid.instructions.md** - Diagram syntax
6. **Most of planning.instructions.md** - The extensive examples and detailed guidance

#### What's NEW in Active Instructions
1. **code-review-checklist.instructions.md** - Mandatory pre-commit checklist
2. **Better modularity** - Single concerns per file
3. **More focused** - Less duplication, clearer scope

#### What Was Split/Reorganized
- `general.instructions.md` → `accuracy.instructions.md`, `communication.instructions.md`, `git-operations.instructions.md`
- `planning.instructions.md` → `plan-structure.instructions.md`, `planning-workflow.instructions.md`

### Why Files Were Moved to .bak

**Context Bloat:** The .bak files totaled ~2,651 lines. When all loaded into context:
- Token usage too high
- AI gets overwhelmed with instructions
- Harder to find relevant guidance
- Conflicting or redundant instructions

**Modularization Strategy:**
- Split large files into focused concerns
- Keep only essential instructions active
- Move detailed examples/guidance to .bak for reference
- Rely on AI's base knowledge + focused rules rather than exhaustive examples

**The "serious AI misbehaviour" mentioned:**
Likely refers to when certain critical rules (NO GUESSING POLICY, code review checklist) weren't prominent enough, causing:
- Guessing at implementation details
- Skipping validation steps
- Not following coding standards
- Making assumptions about user intent

**Resolution:**
- `accuracy.instructions.md` - Makes NO GUESSING POLICY most prominent
- `code-review-checklist.instructions.md` - Mandatory verification before any code
- `git-operations.instructions.md` - Clear git policies

## Copilot Instructions File Status

The `.github/copilot-instructions.md` file REFERENCES files that don't exist:
- Line 60: References `general.instructions.md` (should be `accuracy.instructions.md`)
- Line 65: References `documentation.instructions.md` (in .bak)
- Line 66: References `planning.instructions.md` (partially split)
- Line 68: References `architecture.instructions.md` (in .bak)

**This explains the "lobotomized" comment** - the main copilot instructions reference files that have been moved or renamed!

## Recommendations

### For Issue #100 (Change Registry)
1. **DO NOT merge this branch yet** - Integration not complete
2. Keep working on this branch to implement the 5 prompts
3. OR defer #100 entirely and focus on v1.1.0 release (#94)
4. The registry files (CHANGES-ACTIVE/ARCHIVED.md) are valuable and could be cherry-picked if needed

### For Instruction Files
1. **Update `.github/copilot-instructions.md`** to reference correct active files
2. **Consider restoring some .bak files:**
   - `issue-workflow.instructions.md` - Useful for starting work
   - `documentation.instructions.md` - Good to have for markdown standards
   - Maybe abbreviated versions to avoid context bloat
3. **OR keep current split** and update copilot-instructions.md to reflect reality

### For v1.1.0 Release
1. Switch to main branch
2. Create new branch for #94
3. Fix the cycles bug
4. Release v1.1.0
5. Come back to #100 later when ready

## Risk Assessment

**Merging current branch would break things because:**
- Copilot instructions reference non-existent files
- Planning workflow can't actually use the change registry (prompts not implemented)
- The ".tmp/" directory has untracked files
- No clear indication which instruction files are authoritative

**Safest path forward:**
1. Stash/commit work on this branch
2. Fix copilot-instructions.md first (either path: restore files or update references)
3. Then decide: finish #100 or defer it?
4. Focus on #94 for v1.1.0

