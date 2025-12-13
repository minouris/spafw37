## Example Workflow

**User request:** "Start work on issue #42"

**Steps performed:**
1. Fetch issue details from GitHub
2. Determine milestone (e.g., v1.2.0)
3. Generate feature name: `issue-42-add-feature-x-1.2.0`
4. Create branch: `git checkout -b feature/issue-42-add-feature-x-1.2.0`
5. Create plan: `features/issue-42-add-feature-x-1.2.0.md`
6. Inform user of completion