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