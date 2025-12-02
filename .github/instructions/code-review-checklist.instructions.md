---
applyTo: "**/*"
---

# Mandatory Pre-Commit Code Review Checklist

Before ANY code changes (implementation, tests, documentation, or plan documents):

## 1. Python Import Rules Verification

- [ ] ALL imports are at the TOP of the code block (module level)
- [ ] NO inline imports inside functions (unless circular import documented)
- [ ] Imports grouped: stdlib → third-party → local
- [ ] NO modules passed as function arguments (functions/callbacks are allowed)
- [ ] Functions import what they need directly, not via parameters

**Red flags:**
- `from X import Y` appearing inside a function
- `import pytest` or any other import inside a test function
- Function parameter named `*_module` or `*_class` (not `*_handler`, `*_callback`, or `*_function`)
- Import statements after any executable code

**For plan documents (`features/**/*.md`):**
- Test code blocks should NOT contain import statements inside functions
- If a test file needs imports, show them in a separate "Module-level imports" comment block at the start of the file
- Each test function should reference already-imported modules, not import them again

## 2. Nesting and Complexity Verification  

- [ ] NO code nested more than 2 levels below function declaration
- [ ] NO nested blocks (if/for/while/with/try) exceeding 2 lines
- [ ] ALL extracted helpers have descriptive names
- [ ] ALL extracted helpers have their own tests

**Red flags:**
- Three or more indentation levels inside a function
- Nested `for` inside `if` inside `for`
- More than 2 statements inside any nested block

## 3. Plan Document Sequencing Verification

For `features/**/*.md` files ONLY:

- [ ] Each function followed IMMEDIATELY by its tests
- [ ] NO "Step Xa / Step Xb" grouping (code/tests separated)
- [ ] Pattern is: Code X.Y.Z → Test X.Y.(Z+1) → Test X.Y.(Z+2) → Code X.(Y+1).1
- [ ] NOT: Code X.1 → Code X.2 → Code X.3 → Test X.1 → Test X.2 → Test X.3

**Red flags:**
- Section headers like "Step 5a: Implementation" / "Step 5b: Tests"
- Multiple consecutive Code blocks without intervening Tests
- Test blocks separated from their function by other Code blocks

## 4. Naming Verification

- [ ] NO single-letter variables (use `line_index` not `i`)
- [ ] NO lazy names (`tmp`, `data`, `result`, `val`)
- [ ] ALL names are descriptive full words
- [ ] Constants in UPPER_SNAKE_CASE
- [ ] Dictionary key constants follow `DICT_KEY = 'dict-key'` pattern

## 5. Block Comment Verification

For plan documents:

- [ ] Block comments are DESCRIPTIVE: `# Block 3.4.1: Extract parameter name`
- [ ] NOT just numbered: `# Block 3.4.1.1:` (missing description)
- [ ] NOT over-subdivided: Don't create numbered sub-blocks without clear purpose
- [ ] Every block comment explains WHAT the code does

## When to Apply This Checklist

**ALWAYS before:**
- Writing any Python code (src/, examples/, tests/)
- Writing code examples in documentation (*.md)
- Writing code in plan documents (features/*.md)
- Making any file edits that include code

**Process:**
1. Read relevant instruction files FIRST
2. Review this checklist BEFORE writing code
3. Verify each item AFTER writing code, BEFORE committing

## Enforcement

**If you (the AI assistant) violate any of these rules:**
1. Stop immediately when violation is identified
2. Acknowledge the specific rule violated
3. Explain WHY the violation occurred (which step in reasoning failed)
4. Fix ALL violations before proceeding

**No exceptions.** These are not suggestions - they are mandatory requirements.
