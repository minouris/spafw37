# CHANGES Template for Issue Closing Comments

This template should be added to the end of each issue plan document under a "CHANGES for v1.1.0 Release" section. The content will be posted as the closing comment and consumed by the release workflow.

```markdown
## CHANGES for vX.Y.Z Release

Issue #XX: [Issue Title]

### Issues Closed

- #XX: [Issue Title]

### Additions

- [Function/constant name] [brief description of what it does]. 
- [Another addition] [description].

### Removals

[If none:]
None.

[If deprecating:]
These functions removed in vX.Y+2.Z (emit deprecation warnings in vX.Y.Z):

- [List of deprecated function names]

[If removing:]
- [Function name] removed.

### Changes

[If none:]
None.

[If changes exist:]
- [Brief description of behavioral change].
- [Another change].

### Migration

[If no migration needed:]
No migration required. New functionality only.

[If migration needed:]
- Change `old_function()` to `new_function()`
- Change `another_old()` to `another_new()`

### Documentation

- `doc/file.md` [what was added/changed]
- `doc/another.md` [what was added/changed]
- `examples/new_example.py` [brief description]

### Testing

- [XXX] tests pass
- [XX.XX]% code coverage
- [X] new tests in `test_file.py`
- [X] new tests in `test_another.py`

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...vX.Y.Z  
Issues: https://github.com/minouris/spafw37/issues/XX
```

## Style Guidelines

**Mandatory sections (in order):**
1. Issues Closed
2. Additions
3. Removals
4. Changes
5. Migration
6. Documentation
7. Testing

**Writing style:**
- Dispassionate, matter-of-fact tone
- No marketing language ("exciting new feature", "powerful capability")
- No internal jargon ("flexible resolution", "semantic richness")
- Sentence fragments acceptable, full sentences preferred for clarity
- Present tense for what exists, past tense for what was done
- Technical precision over narrative flow

**Consolidation of Issues (When Merging Changelogs)**

- In Additions, Removals, Changes, Migration, Documentation:
  - Consolidate bullets for all issues, do not break down per issue
  - Ensure that all items have the same style

**Function descriptions:**
- Start with function name
- State what it does factually
- Note error conditions if relevant
- Format: `function_name()` does X. Raises error if Y.

**Examples to follow:**
- GOOD: `unset_param()` removes parameter value completely from configuration. Raises error if parameter not found or is immutable.
- BAD: `unset_param()` provides a flexible way to remove parameter values using our powerful resolution system.
- GOOD: `PARAM_IMMUTABLE` constant marks parameter as write-once.
- BAD: `PARAM_IMMUTABLE` is an exciting new constant that gives you powerful protection.

**Section rules:**
- For empty sections, include the heading but leave content blank
- List items as bullet points with no sub-bullets
- Keep Migration examples concise (before/after pattern)
- Documentation lists files and what changed, not why
- Testing includes pass count, coverage percentage, new test counts

**Footer:**
- Always include full changelog link
- Always include issue links for all issues
- Include PR links if available
