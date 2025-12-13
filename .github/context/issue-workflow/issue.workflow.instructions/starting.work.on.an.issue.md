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
5. Mark "Further Considerations" with "PENDING REVIEW" status - never mark as "RESOLVED" without explicit user confirmation

**Template location:** `features/ISSUE-PLAN-TEMPLATE.md`

**Example:**
```bash