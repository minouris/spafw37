# Prompt: Answer Plan Question

## Your Task

You are answering design question #{QUESTION_NUMBER} for issue #{ISSUE_NUMBER}. This prompt helps coordinate answers between the plan document and GitHub issue comments.

## Parameters

- `{ISSUE_NUMBER}` - The GitHub issue number
- `{QUESTION_NUMBER}` - The question number (Q1, Q2, Q3, etc.)

## Usage

```bash
# Answer question Q1 for issue #15
@2-answer-plan-question 15 Q1
```

## Process

### Step 1: Read the Plan Document

Locate the plan document at `features/{FEATURE_NAME}.md` and find the question section for Q{QUESTION_NUMBER}.

Extract:
- The question text
- The GitHub comment ID (from the link in the question header)
- Any existing answer in the plan document

### Step 2: Check for Answer in Plan Document

Look for an answer section under the question. Answers may be formatted as:

```markdown
**Q1: [Category]** ([#issuecomment-XXXXXX](...))
[Question text]

**Answer:** [Answer text]

[↑ Back to top](#table-of-contents)
```

Or under "Further Considerations" with:

```markdown
### N. [Consideration name] - RESOLVED

**Question:** [Question text]

**Answer:** [Answer text]

**Rationale:** [Explanation]
```

### Step 3: Post Answer to GitHub

If an answer exists in the plan document:

1. **Extract the answer text** from the plan document
2. **Get the comment ID** from the question link
3. **Post a reply** to that specific comment using `gh` CLI:

```bash
cat > /tmp/answer.md << 'EOF'
**Answer:**

[Answer text from plan document]
EOF

# Reply to the specific comment thread
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/{owner}/{repo}/issues/comments/{comment_id}/replies \
  -f body="$(cat /tmp/answer.md)"
```

**Alternative method using gh issue comment with proper formatting:**

```bash
# Get the original comment URL
COMMENT_URL="https://github.com/{owner}/{repo}/issues/{issue_number}#issuecomment-{comment_id}"

# Create reply that references the question
cat > /tmp/answer.md << 'EOF'
> **Q{N}: [Category]**

**Answer:**

[Answer text from plan document]
EOF

# Post as regular comment (GitHub will thread it appropriately if done via web UI)
gh issue comment {ISSUE_NUMBER} --body-file /tmp/answer.md
```

### Step 4: Update Plan Document Status

If the question was marked "PENDING REVIEW" in Further Considerations, update it to "RESOLVED":

```markdown
### N. [Consideration name] - RESOLVED

**Question:** [Question text]

**Answer:** [Answer text from plan document]

**Rationale:** [Explanation]

**Implementation:** [Impact on implementation]
```

### Step 5: Confirm Completion

Report back to the user:
- Question number answered
- GitHub comment ID where answer was posted
- Link to the comment thread
- Whether plan document was updated

## If No Answer Exists

If no answer is found in the plan document:

1. **State that no answer exists**
2. **Ask the user to provide an answer**
3. **Explain where the answer should be added in the plan document**

Example:
```
No answer found for Q{N} in the plan document.

Please provide an answer, and I can:
1. Add it to the plan document under the question
2. Post it as a reply to the GitHub comment
3. Update the "Further Considerations" section if applicable

The question is: [question text]
GitHub comment: [link]
```

## Output Requirements

When complete, provide:
- ✅ Confirmation that answer was posted to GitHub
- ✅ Link to the comment thread
- ✅ Confirmation that plan document was updated (if applicable)
- ✅ Summary of what was answered

## UK English

All text must use UK English spelling: behaviour, colour, organise, etc.
