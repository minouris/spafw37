---
applyTo: "features/**/*.md"
---

# Planning Workflow Instructions

This document provides plain English instructions for the issue planning workflow. Each prompt file in `.github/prompts/` corresponds to a phase in the workflow.

## Quick Reference

| Step | Prompt File | Plain English Instruction |
|------|-------------|---------------------------|
| 1 | `1-create-plan-skeleton.md` | Create plan document skeleton and git branch |
| 2a | `2-analyse-and-plan.md` | Analyse issue and create implementation plan |
| 2b | `2-answer-plan-question.md` | Answer a specific question in the plan |
| 2c | `2-update-plan-local.md` | Update plan document without posting to GitHub |
| 3 | `3-generate-tests.md` | Generate Gherkin test specifications |
| 4 | `4-generate-implementation.md` | Generate implementation code blocks |
| 5 | `5-generate-documentation.md` | Generate documentation changes |
| 6 | `6-generate-changelog.md` | Generate CHANGES section for release |

## When to Use Each Instruction

### Step 1: Starting a New Issue

**Use:** `1-create-plan-skeleton.md`

**Plain English:** "Create a plan document for issue #XX"

**What it does:**
- Creates a new markdown file in `features/` directory
- Sets up the basic structure (Overview, Table of Contents, placeholders)
- Creates a git branch for the work
- Does NOT commit or push

**Example usage:**
```
Create a plan document for issue #61 about refactoring add_command()
```

---

### Step 2a: Planning the Implementation

**Use:** `2-analyse-and-plan.md`

**Plain English:** "Analyse issue #XX and break down the implementation"

**What it does:**
- Reads the issue description and existing codebase
- Identifies affected files and functions
- Creates numbered implementation steps
- Documents architectural decisions
- Posts questions to GitHub if clarification needed
- Records question IDs for tracking

**Example usage:**
```
Analyse issue #61 and create the implementation breakdown
```

---

### Step 2b: Answering Plan Questions

**Use:** `2-answer-plan-question.md`

**Plain English:** "Answer question X in the plan for issue #XX"

**What it does:**
- Updates a specific question section in the plan
- Records the answer and rationale
- Updates architectural decisions if needed
- Does NOT post to GitHub (local update only)

**Example usage:**
```
Answer question 2 in the plan: Should we extract validation into a helper?
Answer: Yes, extract to _validate_command_name() because validation is reused in multiple places.
```

---

### Step 2c: Updating Plan Locally

**Use:** `2-update-plan-local.md`

**Plain English:** "Update the plan document for issue #XX with [changes]"

**What it does:**
- Updates sections of the plan document
- Refines implementation steps
- Adds architectural details
- Does NOT post to GitHub (local only)

**Example usage:**
```
Update the plan for issue #61: Add a section about preserving test coverage during refactoring
```

---

### Step 3: Adding Test Specifications

**Use:** `3-generate-tests.md`

**Plain English:** "Generate test specifications for issue #XX"

**What it does:**
- Creates Gherkin test specs for each implementation step
- Follows Python test standards (module-level functions, docstrings)
- Documents expected behaviour
- Uses Given-When-Then format

**Example usage:**
```
Generate test specifications for issue #61 steps
```

---

### Step 4: Adding Implementation Code

**Use:** `4-generate-implementation.md`

**Plain English:** "Generate implementation code for issue #XX"

**What it does:**
- Adds detailed code blocks to the plan document
- Numbers blocks sequentially (Block X.Y.Z)
- Includes code-then-test pattern
- Adds context comments for each block
- **ONLY edits the plan document** - does NOT modify source files

**Example usage:**
```
Generate implementation code for issue #61 step 3 (extract validation helper)
```

---

### Step 5: Adding Documentation

**Use:** `5-generate-documentation.md`

**Plain English:** "Generate documentation changes for issue #XX"

**What it does:**
- Documents what files need documentation updates
- Specifies new sections, examples, or API reference entries
- Uses UK English
- Follows technical writing style
- Completes success criteria checklist

**Example usage:**
```
Generate documentation changes for issue #61
```

---

### Step 6: Adding Changelog

**Use:** `6-generate-changelog.md`

**Plain English:** "Generate CHANGES section for issue #XX"

**What it does:**
- Creates the CHANGES section following the template
- Documents additions, removals, changes
- Specifies migration requirements
- Lists documentation updates
- This content gets posted as closing comment and consumed by release workflow

**Example usage:**
```
Generate CHANGES section for issue #61
```

---

## Common Patterns

### Full Planning Workflow (Steps 1-6)

```
1. Create plan document for issue #XX
2. Analyse issue #XX and create implementation breakdown
   [If questions arise, answer them with Step 2b]
3. Generate test specifications for issue #XX
4. Generate implementation code for issue #XX
5. Generate documentation changes for issue #XX
6. Generate CHANGES section for issue #XX
```

### Iterative Refinement

If you need to refine the plan after creating it:

```
1. Update plan for issue #XX: [what to change]
   (uses 2-update-plan-local.md)
2. Answer question X: [question and answer]
   (uses 2-answer-plan-question.md)
3. Re-generate [tests|implementation|docs|changelog] for updated steps
   (uses 3, 4, 5, or 6 as needed)
```

### Skipping Steps

You can skip steps if they're not needed:
- **Step 2b/2c:** Only needed if you have questions or updates
- **Step 3:** Only needed for complex features requiring detailed test specs
- **Step 5:** Only needed if user-facing changes require documentation
- **Step 6:** Always required for tracking in release workflow

---

## Key Principles

### Do NOT Guess
- Never assume API behaviour - fetch documentation
- Never assume codebase patterns - read the source
- Never assume test expectations - verify behaviour
- If uncertain, explicitly state what you don't know

### Do NOT Commit Without Permission
- All prompts include: "Do NOT commit or push changes without explicit user permission"
- Create changes locally, let the user review, then commit when instructed

### Follow Coding Standards
All code (even in plan documents) must follow:
- `.github/instructions/python.instructions.md` - General Python standards
- `.github/instructions/python37.instructions.md` - Python 3.7 compatibility
- `.github/instructions/python-tests.instructions.md` - Test structure
- `.github/instructions/plan-structure.instructions.md` - Plan document format

### UK English
Use UK spelling everywhere:
- colour, behaviour, organise, centre, licence, initialise

---

## Example: Complete Workflow for Issue #61

```
Step 1: Create plan document for issue #61
> Creates features/issue-61-refactor-add-command.md with skeleton

Step 2: Analyse issue #61 and break down the implementation
> Reads command.py, identifies add_command() function
> Creates 5 implementation steps for extracting helpers
> Documents decision to maintain test coverage at each step

Step 2b: Answer question about helper naming convention
> Question: Should helpers be public or private?
> Answer: Private with _ prefix, since they're internal implementation details

Step 3: Generate test specifications for issue #61
> Creates Gherkin specs for each helper extraction
> Documents expected behaviour for validation, storage, etc.

Step 4: Generate implementation code for issue #61
> Adds detailed code blocks for each step
> Numbers blocks: 1.1.1, 1.1.2, 1.2.1, etc.
> Includes tests immediately after each code block

Step 5: Generate documentation changes for issue #61
> No user-facing changes, so minimal documentation
> Notes that internal refactoring doesn't affect API

Step 6: Generate CHANGES section for issue #61
> Documents refactoring under "Changes"
> Notes "No migration required"
> Lists test files updated
```

---

## Tips for Using These Instructions

### Be Specific
Instead of: "Work on issue #61"
Use: "Analyse issue #61 and create implementation breakdown" (Step 2)

### Use Step Numbers
"Proceed with Step 4 for issue #61" is clearer than "Add the implementation code"

### Chain Steps When Appropriate
"Complete steps 3-6 for issue #61" works if the plan is already created and finalised

### One Step at a Time for Complex Issues
For high-risk or complex changes, do one step, review, then continue

---

## Related Files

- **Prompt files:** `.github/prompts/*.md` - Detailed technical prompts
- **Instruction files:** `.github/instructions/*.md` - Coding standards and rules
- **Template files:** `features/*.md` - Examples of completed plans
