# Prompt: Answer Plan Question

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

You are posting answers from the plan document to GitHub issue comment threads. This prompt scans the plan document for all answers (both in Design Questions and Further Considerations) and posts them to their corresponding GitHub comment threads if not already posted.

## Parameters

- `{ISSUE_NUMBER}` - The GitHub issue number

## Usage

```bash
# Post all answered questions for issue #15
@2-answer-plan-question 15
```

## Process

### Step 1: Read the Plan Document

Locate the plan document at `features/{FEATURE_NAME}.md` and scan for:

1. **Design Questions sections** with format:
```markdown
**Q{N}: [Category]** ([#issuecomment-XXXXXX](...))
[Question text]

**Answer:** [Answer text]
```

2. **Further Considerations sections** with format:
```markdown
### N. [Consideration name] - RESOLVED

([#issuecomment-XXXXXX](...))

**Question:** [Question text]

**Answer:** [Answer text]

**Rationale:** [Explanation]
```

Extract for each answered question/consideration:
- Question number (Q1, Q2, etc. or FC1, FC2, etc.)
- Question text
- Answer text
- GitHub comment ID (from the link)
- Status (RESOLVED vs PENDING REVIEW)

### Step 2: Check Which Answers Have Been Posted

For each comment ID found in Step 1, check if an answer has already been posted:

```bash
# Get all comments on the issue and check if answer exists
gh api /repos/minouris/spafw37/issues/{ISSUE_NUMBER}/comments/{COMMENT_ID} \
  --jq '.body' | grep -q "^**Answer:**"
```

Or check replies to the specific comment:

```bash
# Check if there are replies to this comment that contain "**Answer:**"
gh api "/repos/minouris/spafw37/issues/15/comments" --paginate | \
  python3 -c "
import sys, json
comments = json.load(sys.stdin)
# Look for comments that quote or reference the original comment
for c in comments:
    if '**Answer:**' in c['body']:
        print(c['id'])
"
```

Build a list of comment IDs that need answers posted.

### Step 3: Post Answers to GitHub

For each unanswered question/consideration:

1. **Get the original comment body:**

```bash
ORIGINAL_BODY=$(gh api /repos/minouris/spafw37/issues/comments/{COMMENT_ID} --jq '.body')
```

2. **Append the answer** to the original comment body:

```bash
cat > /tmp/answer_q{N}.md << EOF
${ORIGINAL_BODY}

---

**Answer:**

[Answer text from plan document]

[Additional context like Rationale or Implementation notes if present]
EOF
```

**Example result:**
```markdown
**Q1: Architecture Approach**

Should user input params be:
- Regular params with additional properties (e.g., `PARAM_PROMPT`, `PARAM_PROMPT_TIMING`)?
- A separate structure entirely (e.g., `INPUT_PROMPTS` at command level)?
- A hybrid approach where params define what can be prompted and commands control when?

---

**Answer:**

Option A - Param-level approach has been selected.

[Full answer details...]
```

3. **Update the original comment:**

```bash
gh api --method PATCH /repos/minouris/spafw37/issues/comments/{COMMENT_ID} -f body="$(cat /tmp/answer_q{N}.md)"
```

This appends the answer directly to the original question comment, keeping everything together in one place.

4. **Capture the response** to confirm update

### Step 4: Cross-Reference Answers

After posting answers, scan the plan document to identify if any answers address questions in other sections:

**Example scenarios:**
- Further Consideration 2 (Architecture Approach) resolves Q1 (Architecture Approach)
- Further Consideration 4 (User Experience) addresses Q8 (Silent/Batch Mode)

For each cross-reference found:

1. **Update the related question section** to reference the answer:

```markdown
**Q1: Architecture Approach** ([#issuecomment-XXXXXX](...))

Should user input params be:
- Regular params with additional properties (e.g., `PARAM_PROMPT`, `PARAM_PROMPT_TIMING`)?
- A separate structure entirely (e.g., `INPUT_PROMPTS` at command level)?
- A hybrid approach where params define what can be prompted and commands control when?

**Answer:** See [Further Consideration 2: Architecture Approach Trade-offs](#2-architecture-approach-trade-offs---resolved) - Option A (param-level approach) has been selected.

[↑ Back to top](#table-of-contents)
```

2. **Or update Further Consideration** to note it resolves a design question:

```markdown
### 2. Architecture Approach Trade-offs - RESOLVED

([#issuecomment-XXXXXX](...))

**Question:** What are the pros and cons of each architecture approach?

**Answer:** Option A - Param-level approach.

[Implementation details...]

**Resolves:** Q1 (Architecture Approach)
```

### Step 5: Update Status Markers

Ensure all answered questions/considerations have correct status:
- Change "PENDING REVIEW" to "RESOLVED" when answer is present
- Verify GitHub comment links are present for all items

### Step 6: Report Results

Provide a summary:
```
Posted answers to GitHub:
✅ Q1 (Architecture Approach) - Comment #issuecomment-XXXXXX
✅ FC2 (Architecture Approach Trade-offs) - Comment #issuecomment-XXXXXX

Cross-references updated:
✅ Q1 now references FC2
✅ FC2 notes it resolves Q1

Status updates:
✅ FC1: PENDING REVIEW → RESOLVED
✅ FC2: PENDING REVIEW → RESOLVED

Not posted (already answered on GitHub):
- Q2, Q3, Q4

Still pending answers:
- Q5, Q6, Q7, Q8
- FC3, FC4, FC5, FC6, FC7
```

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English

All text must use UK English spelling: behaviour, colour, organise, etc.
