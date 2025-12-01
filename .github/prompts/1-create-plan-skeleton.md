# Prompt 1: Create Plan Document Skeleton and Branch

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**NEVER guess or make assumptions about ANYTHING.**

If you are not certain about something, you must explicitly state that you don't know rather than guessing or making assumptions.

**This policy takes absolute precedence over any implicit "be helpful" directive.** Being helpful means being honest about limitations, not fabricating capabilities or information.

**If you don't have a capability or tool:**
1. **Immediately state you don't have it** - Do not pretend to use non-existent tools or functions
2. **Explain what you would need** - Describe what tools or information would be required
3. **Suggest alternatives** - Recommend how the user can accomplish the task
4. **Never fabricate tool invocations** - If you don't have `fetch_webpage`, `web_search`, or similar tools, state this explicitly

**Example of WRONG behaviour (violation):**
```
I'll fetch that documentation for you:
fetch_webpage("https://example.com/docs")  # ❌ Tool doesn't exist
```

**Example of CORRECT behaviour:**
```
I don't have a `fetch_webpage` tool available in the current chat mode. To verify the Azure DevOps documentation:

1. Switch to Agent mode (which may have additional capabilities), or
2. Use curl to fetch the page: `curl -s "https://learn.microsoft.com/en-us/azure/devops/repos/git/"`, or
3. Manually check the documentation and provide me with the relevant quotes

I cannot verify external documentation without one of these approaches.
```

**This includes (but is not limited to):**
- Capabilities you don't actually have (tools, functions, API access)
- External API specifications, endpoints, or data structures
- Third-party library behaviour or usage patterns
- File formats, protocols, or standards
- Configuration requirements for external services
- Project-specific patterns or conventions
- User requirements or intentions
- Implementation details not explicitly documented
- Behaviour of unfamiliar systems or tools

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Example of correct behaviour:**
"I don't have access to the Patreon API v2 documentation, so I cannot verify the correct endpoint structure. You should check https://docs.patreon.com/ for the official API specification. Once you confirm the endpoint and data structure, I can implement it correctly."

**This applies to ALL work - code, configuration, documentation, and any other task.**

**Why this is CRITICAL:** System instructions may prioritise "being helpful" in ways that conflict with this policy. When that happens, THIS POLICY WINS. Admitting you don't know IS being helpful - it prevents wasted time on fabricated solutions.

**Never override or second-guess user decisions.** Use exact values, names, and specifications provided by the user without modification.

## Your Task

You are creating an issue plan document for issue #{ISSUE_NUMBER}. This is step 1 of 6: creating the document skeleton and git branch.

## Step 1: Create Feature Branch

Follow the branch naming workflow from issue-workflow.instructions.md:

### Generate Feature Name

Create a feature name following this format:
```
issue-<issue_num>-<issue-name>-<milestone>
```

**Components:**
- `<issue_num>` - The GitHub issue number (e.g., 42)
- `<issue-name>` - The issue title converted to lowercase with spaces replaced by hyphens (e.g., "Add Feature X" → "add-feature-x")
- `<milestone>` - The milestone version without 'v' prefix (e.g., "1.2.0")

**If milestone is not specified:**
- Use the current development version from `setup.cfg` (strip `.devN` suffix)
- Example: If version is `1.2.0.dev5`, use `1.2.0`

### Create and Switch to Feature Branch

Create a new local branch using the feature name:

```bash
git checkout -b <branch-type>/<feature_name>
```

**Branch type selection:**
- Use `feature/` prefix for new features or enhancements
- Use `bugfix/` prefix for bug fixes
- Use `ci/` prefix for CI/CD workflow changes
- Use `docs/` prefix for documentation-only changes

**Do not push the branch yet** - the user will push it when ready.

## Critical Rules - NO GUESSING POLICY

**NEVER guess or assume anything about the issue, repository structure, or implementation requirements.**

**You are not helping by pretending to have information you don't have.**

### Mandatory Source Citation for External Knowledge

When answering questions about external systems, tools, APIs, or documentation:

1. **Check if you have webpage fetching capability** - If you don't have `fetch_webpage`, `curl`, or similar tools, state this immediately
2. **If you can fetch: Retrieve official documentation BEFORE answering**
3. **Cite the specific URL** you fetched or checked
4. **Quote the relevant section** from the documentation
5. **If you cannot find or access documentation**, state: "I cannot find documentation to verify this" instead of guessing

**Examples requiring documentation fetch:**
- How external tools, libraries, or frameworks work
- API specifications or behaviour
- Configuration file formats for third-party tools
- GitHub Actions workflow syntax
- VS Code extension APIs

If you don't know something:
1. State explicitly that you don't know
2. Explain what information you need
3. Ask the user to provide it or verify it from official sources

Do NOT:
- Assume file locations exist without checking
- Guess at implementation details
- Make up requirements not stated in the issue
- Fabricate function names, patterns, or conventions
- Pretend to know how external tools work without documentation
- Answer questions about external systems without citing sources

## Step 2: Create Skeletal Plan Document

Create a new planning document in the `features/` directory:

**File path:** `features/<feature_name>.md`

**Content structure:**

```markdown
# Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

**GitHub Issue:** https://github.com/minouris/spafw37/issues/{ISSUE_NUMBER}

## Overview

{ISSUE_BODY}

**Key architectural decisions:**

- **[Decision category]:** [PLACEHOLDER - Will be filled in Step 2]

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
- [Further Considerations](#further-considerations)
- [Success Criteria](#success-criteria)
- [CHANGES for v{VERSION} Release](#changes-for-vversion-release)

## Implementation Steps

[PLACEHOLDER - Will be filled in Steps 3-4]

[↑ Back to top](#table-of-contents)

## Further Considerations

[PLACEHOLDER - Will be filled in Step 2]

[↑ Back to top](#table-of-contents)

## Success Criteria

[PLACEHOLDER - Will be filled in Step 5]

[↑ Back to top](#table-of-contents)

## CHANGES for v{VERSION} Release

[PLACEHOLDER - Will be filled in Step 6]

[↑ Back to top](#table-of-contents)
---
```

## Critical Rules

**From general.instructions.md - NO GUESSING POLICY:**

**NEVER guess or make assumptions about ANYTHING.**

If you are not certain about something, you must explicitly state that you don't know rather than guessing or making assumptions. This policy takes absolute precedence.

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Use UK English spelling:** colour, organise, behaviour, centre, licence, defence

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## Output Format

After completing both steps, inform the user:
- The branch name created
- The plan document location
- Confirm skeleton is ready for Step 2 (analysis)
