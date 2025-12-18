---
applyTo: "**/*"
---
# CRITICAL: GitHub CI/CD Git Operations Policy

## Mandatory Full Log Review for CI/CD Failures

When diagnosing GitHub Actions workflow failures or any CI/CD errors:

1. **ALWAYS retrieve and examine the COMPLETE log output** for the failed step/job
2. **Never grep for specific error patterns** before seeing the full context
3. **Read the entire step output** from start to finish to understand what happened
4. **Look for multiple errors** - the visible error may be a consequence of an earlier issue
5. **Check surrounding steps** - failures may cascade from previous steps

**Why this is critical:**
- Searching for specific patterns introduces confirmation bias
- You may miss earlier errors that caused the visible failure
- Context before/after the error often reveals the root cause
- Multiple errors may occur in sequence

**Example of correct behaviour:**
```bash
# WRONG - searching for a specific error
gh run view 12345 --log | grep "SomeError"

# RIGHT - retrieve full output for the failed step
gh run view 12345 --log 2>&1 | awk '/StepName.*##\[group\]/,/##\[error\]/'
```

**This applies to ALL remote error diagnosis - GitHub Actions, CI systems, remote servers, etc.**

## CRITICAL: Git General Operations Policy

**YOU MAY NOT COMMIT CODE. YOU MAY NOT PUSH CODE.**

You do not have permission to run `git commit` or `git push` under any circumstances. These operations must be performed by the human user only.

**Rationale:** You have repeatedly claimed work was complete when it was not, making it unsafe to allow you to commit or push changes.

## CRITICAL: Pull Request Review Requirements

When reviewing pull requests following a code review:

1. **Retrieve ALL unresolved comments** - Use the GitHub Pull Request extension (`github-pull-request_openPullRequest`) to retrieve the ACTUAL pull request data, not just a subset
2. **Check resolution status** - Only consider comments explicitly marked as RESOLVED by an actual human being. Do not assume comments are resolved just because you made changes
3. **Read response threads** - Review ALL comments made in RESPONSE to reviewer comments, as these often contain important decisions and clarifications
4. **Address all file types** - PR comments may reference:
   - Source code files (tests, implementation)
   - Documentation files (markdown, examples)
   - Planning documents (features/*.md) - these often contain code examples that must follow the same standards as production code
5. **No assumptions** - Do not assume you've addressed a comment without explicit confirmation
