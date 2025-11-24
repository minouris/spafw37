---
applyTo: "**/*"
---

# Issue Workflow Instructions

These instructions apply when starting work on a new issue.

## Starting Work on an Issue

When instructed to start working on an issue (e.g., "start work on issue #42"), perform the following steps in order:

### 1. Generate Feature Name

Create a feature name following this format:

```
issue-<issue_num>-<issue-name>-<milestone>
```

**Components:**
- `<issue_num>` - The GitHub issue number (e.g., 42)
- `<issue-name>` - The issue title converted to lowercase with spaces replaced by hyphens (e.g., "Add Feature X" → "add-feature-x")
- `<milestone>` - The milestone version without 'v' prefix (e.g., "1.2.0")

**Example:**
- Issue #42: "Add Feature X" in milestone v1.2.0
- Feature name: `issue-42-add-feature-x-1.2.0`

**If milestone is not specified:**
- Use the current development version from `setup.cfg` (strip `.devN` suffix)
- Example: If version is `1.2.0.dev5`, use `1.2.0`

### 2. Create and Switch to Feature Branch

Create a new local branch using the feature name:

```bash
git checkout -b <branch-type>/<feature_name>
```

**Branch type selection:**
- Use `feature/` prefix for new features or enhancements
- Use `bugfix/` prefix for bug fixes
- Use `ci/` prefix for CI/CD workflow changes
- Use `docs/` prefix for documentation-only changes

**Example:**
```bash
git checkout -b feature/issue-42-add-feature-x-1.2.0
```

**Do not push the branch yet** - the user will push it when ready.

### 3. Create Skeletal Plan Document

Create a new planning document in the `features/` directory:

**File path:** `features/<feature_name>.md`

**Content:**
1. Use `ISSUE-PLAN-TEMPLATE.md` as the template
2. Fill in known information from the issue:
   - Issue number in title and throughout document
   - Issue title
   - Issue description (if provided) in Overview section
   - Milestone version in CHANGES section
3. Leave sections as placeholder text where information is not yet known
4. Include all template sections (do not remove any)

**Template location:** `features/ISSUE-PLAN-TEMPLATE.md`

**Example:**
```bash
# Create features/issue-42-add-feature-x-1.2.0.md with:
- Title: "Issue #42: Add Feature X"
- Overview populated with issue description
- Other sections with placeholder text from template
- CHANGES section targeting v1.2.0
```

### 4. Confirm Completion

After completing all steps, inform the user:
- The branch name created
- The plan document location
- Next steps (e.g., "Review and update the plan document with implementation details")

## Example Workflow

**User request:** "Start work on issue #42"

**Steps performed:**
1. Fetch issue details from GitHub
2. Determine milestone (e.g., v1.2.0)
3. Generate feature name: `issue-42-add-feature-x-1.2.0`
4. Create branch: `git checkout -b feature/issue-42-add-feature-x-1.2.0`
5. Create plan: `features/issue-42-add-feature-x-1.2.0.md`
6. Inform user of completion

## Integration with Other Instructions

This workflow integrates with:
- **`general.instructions.md`** - Git operations policy (no commits/pushes by agent)
- **`planning.instructions.md`** - Plan document format and structure
- **`documentation.instructions.md`** - UK English and style requirements

## Automated Changelog Generation

When feature or bugfix branches are pushed, the `update-changelog.yml` workflow automatically:

1. Reads the current version from `setup.cfg`
2. Finds all plan files targeting that version (checks filename and CHANGES section header)
3. Extracts CHANGES sections from each plan file
4. Combines them into a single changelog entry following `CHANGES-TEMPLATE.md` guidelines
5. Updates or replaces the version entry in `CHANGELOG.md`
6. Commits the changes with `[skip ci]` to avoid triggering additional workflows

**The workflow runs after Test and Packaging workflows complete successfully.**

This ensures `CHANGELOG.md` stays current as development progresses and is ready for release without manual consolidation.

## What NOT to Do

❌ Don't push the branch - the user will do this
❌ Don't commit the plan document - the user will review it first
❌ Don't start implementation without a completed plan
❌ Don't skip any of the three required steps
❌ Don't modify existing issues or branches
❌ Don't guess at information not provided in the issue
