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

### Step 2: Analysis and Planning (Iterative)

**IMPORTANT:** Step 2 is iterative. It may require multiple back-and-forth cycles with the user to resolve questions before proceeding.

#### Step 2a: Initial Analysis

**Prompt:** `.github/prompts/2-analyse-and-plan.md`

**What it does:** 
- Analyses current code and identifies what needs to change
- Breaks work into logical implementation steps
- Creates questions requiring user clarification (posted to GitHub issue)
- Adds Planning Checklist items for each question: `- [ ] Q{N} answered and resolved (Comment #...)`

**User instruction:** "Do the analysis and planning step for issue #{NUMBER}"

**Output:** Plan document with Overview, Steps, Further Considerations (with questions), and Success Criteria. Questions marked PENDING REVIEW.

#### Step 2b: Answer Questions Locally

**Prompt:** `.github/prompts/2-update-plan-local.md`

**What it does:**
- Updates plan document with user's answers to questions
- Changes question status from PENDING REVIEW → RESOLVED
- Marks question Planning Checklist items complete: `- [x] Q{N} answered and resolved`
- Marks Step 2 complete when ALL questions resolved

**User instruction:** "Update the plan with: [answers to questions]"

**Repeat Step 2b for each set of answers until all questions resolved.**

#### Step 2c: Post Answers to GitHub

**Prompt:** `.github/prompts/2-answer-plan-question.md`

**What it does:**
- Posts answers from plan document back to GitHub issue comment threads
- Ensures GitHub discussion stays synchronized with plan document

**User instruction:** "Post answers to GitHub for issue #{NUMBER}"

**Note:** Step 2 is only complete when:
1. All major sections filled (Overview, Steps, Considerations, Success Criteria), AND
2. Either no questions were needed, OR all questions marked RESOLVED and Planning Checklist items checked

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

### Step 7: Verify Plan Readiness

**Prompt:** `.github/prompts/7-verify-plan-readiness.md`

**What it does:** Comprehensive verification that plan is complete and meets all standards before implementation. Checks for placeholders, code standards violations, test coverage, and updates Planning Checklist.

**User instruction:** "Verify the plan is ready for implementation"

**Note:** Final quality gate before Step 8. If issues are found, they must be fixed before proceeding.

### Step 8: Implement from Plan

**Prompt:** `.github/prompts/8-implement-from-plan.md`

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

2a. "Do the analysis and planning step"
    → Creates questions, posts to GitHub, adds Planning Checklist items for each question
    
2b. User answers questions in chat
    "Update the plan with: [answers]"
    → Marks question items [x] in Planning Checklist
    
2b. User answers more questions
    "Update the plan with: [more answers]"
    → Marks more question items [x]
    → When all questions [x], marks Step 2 complete
    
2c. "Post answers to GitHub for issue #61"
    → Synchronizes answers back to GitHub issue

3. "Generate test specs"
   → Marks Step 3 complete in Planning Checklist

4. "Generate implementation code" (creates scratch files if complex)
   → Marks Step 4 complete in Planning Checklist

5. "Generate documentation changes"
   → Marks Step 5 complete in Planning Checklist

6. "Generate CHANGES section"
   → Marks Step 6 complete in Planning Checklist

7. "Verify the plan is ready for implementation"
   → Final verification, updates Planning Checklist with any issues

8. "Implement the feature from the plan" (writes actual code)
```

## Important Reminders

- **Steps 1-7:** Work on plan documents only (`features/*.md`)
- **Step 8:** Implements actual code (`src/`, `tests/`)
- **Step 7 is mandatory:** Always verify plan before implementation
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
