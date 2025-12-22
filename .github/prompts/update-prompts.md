# Prompt: Update Planning Workflow Prompts

**IMPORTANT:** This prompt is for updating the prompt files themselves, not for working on feature issues.

## When to Use This Prompt

Use this prompt when you need to:
- Refine existing prompt instructions
- Add new guidance to prompts
- Fix ambiguities or errors in prompts
- Restructure prompt workflows
- Add examples or clarifications

**Do NOT use for:**
- Regular feature development (use the numbered prompts 1-7)
- Issue planning or implementation
- Documentation updates (unless they're about the prompts themselves)

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY.**

Key reminder: NEVER guess about what changes are needed or why. The user must explicitly describe the prompt improvements required.

## Workflow Overview

When updating prompts, follow this structured workflow to maintain clean git history and traceability:

1. **Create GitHub issue** documenting the prompt changes
2. **Create dedicated branch** for the prompt updates (based on current branch)
3. **Commit prompt changes** to the dedicated branch
4. **Switch back** to original branch
5. **Merge prompt changes** into original branch

This ensures prompt improvements are tracked separately from feature work while remaining integrated.

## Step 1: Document the Prompt Changes

Create a GitHub issue that explains:
- **Problem:** What confusion, ambiguity, or missing guidance exists?
- **Solution:** What improvements are being made?
- **Changes:** Specific prompt files affected and line counts
- **Benefits:** How this improves the planning workflow

**Template:**

```bash
cat > /tmp/issue.md << 'EOF'
# [Brief Title of Prompt Improvement]

## Problem

[Describe the issue with current prompts - confusion, missing guidance, ambiguity, etc.]

Example:
- Prompts conflated concepts X and Y
- Step N was unclear about when to do Z
- Missing guidance on how to handle situation W

## Solution

[Describe the improvements being made]

Example:
- Separate X and Y into distinct sections
- Add explicit guidance for Z in Step N
- Add examples demonstrating W

## Changes Made

- **Prompt 1:** [Description] (+X lines)
- **Prompt 2:** [Description] (+Y lines)
- **Prompt N:** [Description] (-Z lines)

Total: +N net lines of improved guidance

## Benefits

1. **[Benefit 1]** - [Explanation]
2. **[Benefit 2]** - [Explanation]
3. **[Benefit 3]** - [Explanation]
EOF

gh issue create \
  --title "[Brief title]" \
  --body-file /tmp/issue.md \
  --label enhancement
```

**Capture the issue URL** - you'll reference it in commit messages.

## Step 2: Create Dedicated Branch

Create a new branch specifically for the prompt updates, based on your current working branch:

```bash
# Branch naming: feature/issue-N-brief-description
git checkout -b feature/issue-73-restructure-workflow-checklists
```

**Branch naming convention:**
- `feature/issue-N-[brief-description]` for prompt improvements
- Keep description short and clear
- Use lowercase with hyphens

## Step 3: Stage and Commit Prompt Changes

Commit ONLY the prompt file changes to the dedicated branch:

```bash
# Add only prompt files
git add .github/prompts/

# Commit with detailed message
git commit -m "Issue #N: [Brief title]

[1-2 sentence summary of what was changed]

[Detailed breakdown of changes:]

1. [Change category 1]: [Description]
   - [Specific detail]
   - [Specific detail]

2. [Change category 2]: [Description]
   - [Specific detail]

Changes:
- Prompt 1: +X lines ([what was added/changed])
- Prompt 2: +Y lines ([what was added/changed])
- Prompt N: -Z lines ([what was removed])

Benefits: [Comma-separated list of key benefits]"
```

**Commit message guidelines:**
- First line: `Issue #N: [Brief title]` (50 chars max)
- Blank line
- Summary paragraph (2-3 sentences)
- Blank line
- Detailed breakdown (organized by category)
- Blank line
- Changes section (files and line counts)
- Benefits section (concise summary)

**Example commit message:**

```
Issue #73: Restructure planning workflow checklists

Separate three distinct checklist concepts:

1. Planning Checklist (Step 1): Track plan document completeness
   - Is structure complete?
   - Are implementation details specified?
   - Is quality verified?

2. Success Criteria (Step 2): Define feature outcome requirements
   - Functional requirements (behaviour correctness)
   - Performance requirements (speed, memory)
   - Compatibility requirements (Python 3.7+)
   - User experience requirements (clarity, usability)

3. Implementation Checklist (Step 4): Track TDD workflow
   - Test Phase (RED - expect failures)
   - Implementation Phase (GREEN - make tests pass)
   - Regression Phase (verify no breakage)

Changes:
- Prompt 1: +78 lines (Planning Checklist generation)
- Prompt 2: +77 lines (Success Criteria definition)
- Prompt 4: +126 lines (Implementation Checklist for TDD)
- Prompt 5: -45 lines (removed misplaced Success Criteria)

Benefits: Clear separation of concerns, proper workflow sequencing,
better tracking, less confusion between planning/requirements/execution.
```

## Step 4: Return to Original Branch

Switch back to the branch you were working on before the prompt updates:

```bash
git checkout feature/issue-61-refactor-add-command
```

**Verify you're on the correct branch:**
```bash
git branch --show-current
```

## Step 5: Merge Prompt Changes

Merge the prompt update branch into your current working branch:

```bash
git merge feature/issue-N-brief-description --no-ff -m "Merge issue #N: [Brief title]

[1-2 sentence summary of what was integrated]"
```

**Why `--no-ff` (no fast-forward)?**
- Preserves the branch history
- Shows the prompt updates as a distinct unit of work
- Makes it easier to understand git history

**Example merge message:**

```
Merge issue #73: Restructure planning workflow checklists

Integrate improved prompt structure with three distinct checklists:
- Planning Checklist (Step 1) - plan document completeness
- Success Criteria (Step 2) - feature outcome requirements  
- Implementation Checklist (Step 4) - TDD workflow tracking
```

## Step 6: Verify the Merge

Check that the merge was successful and the history is clean:

```bash
# View recent commit history
git log --oneline --graph -5

# Verify prompt files are updated
git diff HEAD~1 .github/prompts/ --stat
```

**Expected output:**
- Merge commit on current branch
- Prompt update commit on feature branch
- Clean merge without conflicts

## Step 7: Close the Issue

Close the GitHub issue now that the prompt improvements are integrated:

```bash
# Close the issue with a reference to the merge commit
gh issue close <ISSUE_NUMBER> --comment "Prompt improvements merged in commit $(git rev-parse --short HEAD)"
```

**Example:**

```bash
gh issue close 74 --comment "Prompt improvements merged in commit 16aa945"
```

**Why close the issue?**
- Prompt changes are now integrated
- Work is complete and verified
- Issue tracker stays clean and accurate

## Complete Workflow Example

```bash
# Step 1: Create issue
cat > /tmp/issue.md << 'EOF'
# Add Examples to Prompt 3 Test Generation

## Problem
Prompt 3 lacks concrete examples of good vs bad test structure.

## Solution
Add examples showing proper Gherkin + Python test format.

## Changes Made
- Prompt 3: +45 lines (added examples section)

## Benefits
1. Clearer guidance on test structure
2. Reduces mistakes in test generation
EOF

gh issue create \
  --title "Add examples to Prompt 3 test generation" \
  --body-file /tmp/issue.md \
  --label enhancement

# Output: https://github.com/minouris/spafw37/issues/74

# Step 2: Create branch
git checkout -b feature/issue-74-add-prompt3-examples

# Step 3: Commit changes
git add .github/prompts/3-generate-tests.md
git commit -m "Issue #74: Add examples to Prompt 3 test generation

Add concrete examples demonstrating proper test structure format.

Changes:
- Prompt 3: +45 lines (examples of Gherkin + Python tests)

Benefits: Clearer guidance, fewer formatting mistakes."

# Step 4: Return to original branch
git checkout feature/issue-61-refactor-add-command

# Step 5: Merge
git merge feature/issue-74-add-prompt3-examples --no-ff \
  -m "Merge issue #74: Add examples to Prompt 3

Integrate test structure examples into prompt guidance."

# Step 6: Verify
git log --oneline --graph -3

# Step 7: Close the issue
gh issue close 74 --comment "Prompt improvements merged in commit $(git rev-parse --short HEAD)"
```

## What NOT to Include in Prompt Update Branches

**Do NOT include:**
- Feature implementation code changes
- Test file modifications
- Documentation updates (unless about prompt usage)
- Example file changes
- Configuration changes
- Any non-prompt file modifications

**Only include:**
- Changes to `.github/prompts/*.md` files
- Related instruction file updates (if applicable)

**Why?** Prompt updates should be isolated from feature work to maintain clear separation and traceability.

## Edge Cases

### If You Have Uncommitted Work

If you have uncommitted changes on your current branch:

```bash
# Option 1: Stash changes temporarily
git stash push -m "WIP: feature work"
# ... do prompt updates workflow ...
git stash pop

# Option 2: Commit feature work first
git add [feature files]
git commit -m "WIP: [feature description]"
# ... do prompt updates workflow ...
# Continue feature work
```

### If You Need to Update Prompts Mid-Feature

This is normal! Prompt updates often arise from working on features. Just follow the workflow - the prompt improvements will be merged into your feature branch and will be included when the feature branch merges to main.

### If Multiple People Are Updating Prompts

Coordinate prompt updates to avoid conflicts:
1. Check if anyone else has prompt update branches in progress
2. Pull latest changes before creating your prompt update branch
3. Keep prompt update branches short-lived (merge within hours/days)
4. Communicate in the issue if major restructuring is planned

## Output Requirements

After completing the workflow, confirm:
- ✅ Issue created with URL
- ✅ Branch created with proper naming
- ✅ Prompt changes committed with detailed message
- ✅ Switched back to original branch
- ✅ Changes merged with no-fast-forward
- ✅ Git history verified
- ✅ Issue closed with merge commit reference

Inform the user:
- Issue number and URL
- Branch name created
- Commit SHA
- Merge commit SHA
- Files modified with line counts
- Issue closure confirmation

## UK English Requirements

All commit messages and issue descriptions must use UK English spelling: organise, behaviour, colour, centre, etc.
