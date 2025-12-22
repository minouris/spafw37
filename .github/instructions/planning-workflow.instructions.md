---
applyTo: "features/**/*.md"
---

# Planning Workflow Quick Reference

This document provides plain English instructions for the planning workflow prompts in `.github/prompts/`.

## When to Use This Workflow

Use this workflow when:
- Starting work on a new feature or bug fix
- Making substantial changes that require planning
- Need to document implementation approach before coding

## Workflow Steps

### Step 1: Create Plan Skeleton

**Prompt:** `.github/prompts/1-create-plan-skeleton.md`

**What it does:** Creates the initial plan document structure with overview, table of contents, and placeholder sections.

**User instruction:** "Create the plan skeleton for issue #{NUMBER}"

### Step 2: Analysis and Planning

**Prompt:** `.github/prompts/2-analyse-and-plan.md`

**What it does:** Analyses the current code, identifies what needs to change, breaks work into logical steps.

**User instruction:** "Do the analysis and planning step for issue #{NUMBER}"

### Step 3: Generate Test Specifications

**Prompt:** `.github/prompts/3-generate-tests.md`

**What it does:** Creates Gherkin test specifications for all implementation steps. Tests come before implementation code.

**User instruction:** "Generate preliminary test specs for issue #{NUMBER}"

### Step 4: Generate Implementation Code

**Prompt:** `.github/prompts/4-generate-implementation.md`

**What it does:** Writes detailed implementation code blocks with proper structure. For complex implementations, uses scratch files in `features/scratch/`.

**User instruction:** "Continue with step 4: generate implementation code for issue #{NUMBER}"

**Note:** Uses scratch file approach for complex steps to prevent file corruption.

### Step 5: Generate Documentation Changes

**Prompt:** `.github/prompts/5-generate-documentation.md`

**What it does:** Specifies what documentation files need updating and what changes to make.

**User instruction:** "Generate documentation changes for issue #{NUMBER}"

### Step 6: Generate CHANGES Section

**Prompt:** `.github/prompts/6-generate-changelog.md`

**What it does:** Creates the CHANGES section for the release notes in the plan document.

**User instruction:** "Generate CHANGES section for issue #{NUMBER}"

### Step 7: Implement from Plan

**Prompt:** `.github/prompts/7-implement-from-plan.md`

**What it does:** Implements the actual code in `src/` and `tests/` based on the completed plan document. This is where you write the real production code.

**User instruction:** "Implement issue #{NUMBER} from the plan"

**Note:** This is the only step where you modify actual source code files. All previous steps work on plan documents only.

### Update Prompts Workflow

**Prompt:** `.github/prompts/update-prompts.md`

**What it does:** Updates the planning workflow prompt files themselves. Creates an issue, branches, commits prompt changes, and merges back.

**User instruction:** "Update the prompts with [description of changes]"

**Note:** This is a meta-workflow for improving the prompts themselves, not for feature development. Use when refining prompt instructions, adding examples, or fixing ambiguities.

## Complete Example Workflow

```
1. "Create plan for issue #61"
2. "Do the analysis and planning step"
3. "Generate test specs"
4. "Generate implementation code" (creates scratch files if complex)
5. "Generate documentation changes"
6. "Generate CHANGES section"
7. "Implement the feature from the plan" (writes actual code)
```

## Important Reminders

- **Steps 1-6:** Work on plan documents only (`features/*.md`)
- **Step 7:** Implements actual code (`src/`, `tests/`)
- **Scratch files:** `features/scratch/` contains temporary working files, delete before merge
- **TDD approach:** Tests are written before implementation code
- **Review each step:** Verify output before proceeding to next step

## Common Patterns

**If plan needs updates:**
- Use `.github/prompts/2-update-plan-local.md` to modify existing plan sections
- Use `.github/prompts/2-answer-plan-question.md` to clarify ambiguities

**If implementation reveals issues:**
- Update plan document first
- Then re-run implementation step

**If tests fail:**
- Check if implementation matches plan specifications
- Verify all helpers are implemented
- Ensure test expectations are correct

## Cross-References

- **NO GUESSING POLICY:** `.github/instructions/accuracy.instructions.md`
- **Python standards:** `.github/instructions/python.instructions.md`
- **Python 3.7 compatibility:** `.github/instructions/python37.instructions.md`
- **Test standards:** `.github/instructions/python-tests.instructions.md`
- **Plan structure:** `.github/instructions/plan-structure.instructions.md`
