## Pull Request Review Requirements

When reviewing pull requests following a code review:

1. **Retrieve ALL unresolved comments** - Use the GitHub Pull Request extension (`github-pull-request_openPullRequest`) to retrieve the ACTUAL pull request data, not just a subset
2. **Check resolution status** - Only consider comments explicitly marked as RESOLVED by an actual human being. Do not assume comments are resolved just because you made changes
3. **Read response threads** - Review ALL comments made in RESPONSE to reviewer comments, as these often contain important decisions and clarifications
4. **Address all file types** - PR comments may reference:
   - Source code files (tests, implementation)
   - Documentation files (markdown, examples)
   - Planning documents (features/*.md) - these often contain code examples that must follow the same standards as production code
5. **No assumptions** - Do not assume you've addressed a comment without explicit confirmation
