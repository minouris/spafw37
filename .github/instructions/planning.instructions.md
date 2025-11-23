---
applyTo: 'features/**/*.md'
---

# Planning and Changes Documentation

These instructions apply to issue planning documents and changelog documentation.

## Issue Planning Documents

When creating issue planning documents, follow the structure defined in the ISSUE-PLAN template (see `.github/instructions/templates/ISSUE-PLAN.md`).

**Required sections (in order):**
1. **Overview** - Problem statement, architectural decisions, end result
2. **Implementation Methodology** (optional) - If following a specific pattern
3. **Table of Contents** - Links to all sections
4. **Implementation Steps** - Numbered, detailed steps with files, tests, code examples
5. **Further Considerations** - Questions, decisions, and rationale
6. **Success Criteria** - How to verify the implementation is complete
7. **CHANGES for vX.Y.Z Release** - See Changes Documentation below

**Key principles:**
- Be thorough and specific - include file paths, function names, exact specifications
- Break work into logical, sequential steps
- Include code examples for complex implementations
- Specify test requirements for each step
- Document architectural decisions and trade-offs
- Link back to table of contents from each section

**Reference the template at:** `.github/instructions/templates/ISSUE-PLAN.md`

## Changes Documentation (CHANGES)

When documenting changes for release, follow the structure defined in the CHANGES template (see `.github/instructions/templates/CHANGES.md`).

**Mandatory sections (in order):**
1. **Issues Closed** - List of issue numbers and titles
2. **Additions** - New functions, constants, features
3. **Removals** - Deprecated or removed functionality
4. **Changes** - Behavioural changes to existing functionality
5. **Migration** - How to update code for breaking changes
6. **Documentation** - Documentation files added or changed
7. **Testing** - Test counts, coverage, new test files
8. **Footer** - Changelog link and issue/PR links

**Critical writing style rules:**

**Use dispassionate, matter-of-fact tone:**
- ✅ `unset_param()` removes parameter value completely from configuration.
- ❌ `unset_param()` provides a flexible way to remove parameter values.
- ✅ `PARAM_IMMUTABLE` constant marks parameter as write-once.
- ❌ `PARAM_IMMUTABLE` is an exciting new constant that gives you powerful protection.

**No marketing language:**
- Avoid: "exciting", "powerful", "elegant", "clever", "beautiful"
- Avoid: "enhanced", "improved", "revolutionary", "innovative"
- Use: factual descriptions of what the code does

**No internal jargon:**
- Avoid: "flexible resolution", "semantic richness", "orthogonal concerns"
- Use: clear, specific technical descriptions users can understand

**Function descriptions format:**
```
function_name() does X. Raises error if Y.
```

**Tense usage:**
- Present tense for what exists: "function returns value"
- Past tense for what was done: "added support for", "fixed issue where"

**Consolidation when merging multiple issues:**
- Consolidate all bullets across issues in each section
- Do not break down per-issue within sections
- Ensure consistent style across all items

**Empty sections:**
- Include section heading
- Write "None." if nothing to report in that section

**Reference the template at:** `.github/instructions/templates/CHANGES.md`

## Documentation Update Requirements

When adding new features, always update:
- `README.md` - Reflect new functionality in features list, code examples, examples list
- Add "What's New in vX.Y.Z" section
- Add "**Added in vX.Y.Z**" notes at the start of new documentation sections
- This helps users discover new features and understand when they were introduced

## Best Practices

**Be specific and factual:**
- State exactly what was added, changed, or removed
- Include function names, file paths, and technical details
- Avoid vague descriptions like "improved performance" without metrics

**Think about the user:**
- What do they need to know to use this feature?
- What will break if they upgrade?
- What do they need to change in their code?

**Maintain consistency:**
- Use the same format for similar items
- Follow the established templates exactly
- Keep tone and style consistent throughout
