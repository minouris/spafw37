# PR Review Response Prompt

Review and address all unresolved comments in the active pull request.

## Requirements from `.github/instructions/general.instructions.md`

When reviewing pull requests following a code review:

1. **Retrieve ALL unresolved comments** - Use the GitHub Pull Request extension (`github-pull-request_openPullRequest`) to retrieve the ACTUAL pull request data, not just a subset

2. **Check resolution status** - Only consider comments explicitly marked as RESOLVED by an actual human being. Do not assume comments are resolved just because you made changes

3. **Read response threads** - Review ALL comments made in RESPONSE to reviewer comments, as these often contain important decisions and clarifications

4. **Address all file types** - PR comments may reference:
   - Source code files (tests, implementation)
   - Documentation files (markdown, examples)
   - Planning documents (features/*.md) - these must follow the structure rules in `.github/instructions/plan-structure.instructions.md` and code examples must follow the same standards as production code

5. **No assumptions** - Do not assume you've addressed a comment without explicit confirmation

## Critical First Step

**ALWAYS start by retrieving the actual PR data using `github-pull-request_openPullRequest` to get:**
- All unresolved comments
- Review comments and their resolution status
- PR description and details
- Response threads with decisions and clarifications

Do not proceed with changes until you have retrieved and reviewed all unresolved comments.
