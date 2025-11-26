---
applyTo: "doc/**/*.md,*.md"
---

# Documentation Standards

These instructions apply to all Markdown documentation files in the `doc/` directory and project root.

## CRITICAL: Writing Style

### UK English
- Use UK English spelling and conventions (colour, behaviour, organise, centre, licence, defence)
- Use metric units (metres, kilometres, kilograms, Celsius, litres)
- Use internationally neutral examples (avoid US-specific geography, conventions, or cultural references)

### Tone and Voice

**Use dispassionate, matter-of-fact technical writing:**
- ✅ `unset_param()` removes parameter value completely from configuration.
- ❌ `unset_param()` provides a flexible way to remove parameter values.
- ✅ `PARAM_IMMUTABLE` constant marks parameter as write-once.
- ❌ `PARAM_IMMUTABLE` is an exciting new constant that gives you powerful protection.

**No marketing language:**
- Avoid: "exciting", "powerful", "elegant", "clever", "beautiful", "revolutionary", "innovative"
- Avoid: "enhanced", "improved" (without specific metrics)
- Use: factual descriptions of what the code does

**No internal development jargon:**
- Avoid: "flexible resolution", "semantic richness", "orthogonal concerns"
- Use: clear, specific technical descriptions users can understand
- If technical terms are necessary, define them clearly on first use

**Function descriptions format:**
```
function_name() does X. Raises ErrorType if Y.
```

**Tense usage:**
- Present tense for what exists: "function returns value", "parameter defines behaviour"
- Past tense for historical changes: "added support for", "fixed issue where"

## Document Structure

### Navigation

**All documentation files must include:**
1. **Top-level navigation** - Links to README/index and adjacent documents
2. **Table of contents** - For documents longer than 3 sections
3. **Section links** - Back-references to TOC from major sections (optional but recommended)

**Example navigation:**
```markdown
# Document Title

[← Previous Doc](previous.md) | [Index](README.md#documentation) | [Next Doc →](next.md)

## Table of Contents
...
```

### Headings

- Use sentence case for headings (not Title Case)
- Use descriptive, specific heading text
- Maintain consistent heading hierarchy (don't skip levels)
- Use `##` for major sections, `###` for subsections

### Version Annotations

**When documenting new features, always include:**
- "**Added in vX.Y.Z**" note at the start of new sections
- "What's New in vX.Y.Z" section near the top of relevant guides
- This helps users discover features and understand when they were introduced

**Example:**
```markdown
## New Feature Name

**Added in v1.2.0**

Description of the feature...
```

## Code Examples

### Python Code in Documentation

**All Python code examples must follow the project's Python coding standards:**
- Follow naming conventions from `python.instructions.md`
- Follow Python 3.7 compatibility rules from `python37.instructions.md`
- Use proper snake_case for functions and variables
- Use SCREAMING_SNAKE_CASE for constants
- Include proper docstrings where appropriate

**Code examples teach by example - poor code in docs teaches bad habits.**

### Code Block Formatting

**All code examples must conform to project coding standards** (see `python.instructions.md`, `python37.instructions.md`):

```python
# Use proper syntax highlighting
# Include clear, runnable examples
# Show expected output when relevant

from spafw37 import core as spafw37

# Good: Clear, complete example
def my_command():
    """Process the data."""
    value = spafw37.get_param('count')
    print(f"Processing {value} items")
```

**Avoid:**
- Incomplete or non-runnable snippets (unless explicitly showing pseudocode)
- Poor naming in examples (no `foo`, `bar`, `x`, `y` unless demonstrating syntax)
- Missing imports or context
- Examples that violate project coding standards

## Technical Accuracy

**Documentation must be factually correct:**
- Verify function signatures match actual source code
- Test code examples to ensure they work
- Check parameter names, types, and behaviour against implementation
- Validate external links are current and accessible
- Ensure version numbers are accurate

**When documenting external tools or APIs:**
- Cite official documentation with specific URLs (use `fetch_webpage` to find and verify third-party sources)
- Link to authoritative sources
- Use exact terminology from official docs
- Verify version-specific behaviour

## Documentation Types

### User Guides (`doc/*.md`)

**Purpose**: Teach users how to use features

**Structure:**
- Overview - High-level introduction
- Key capabilities - What can users do?
- Detailed explanations - How do they do it?
- Examples - Show it in action
- Best practices - How should they use it?
- Common pitfalls - What should they avoid?

**Focus on:**
- User-facing functionality
- Practical examples
- Common use cases
- Clear, step-by-step instructions

### API Reference (`doc/api-reference.md`)

**Purpose**: Complete reference for all functions, classes, and constants

**Structure:**
- Function signature
- Description (what it does, not how)
- Parameters (name, type, purpose)
- Return value (type, meaning)
- Exceptions raised
- Version added (if not original)
- Related functions

**Focus on:**
- Completeness - document everything
- Precision - exact signatures and types
- Clarity - unambiguous descriptions

### README Files

**Purpose**: Entry point and overview

**Root README.md contains:**
- Project description
- Features list
- Installation instructions
- Quick start example
- Links to documentation
- What's new in latest version

**Directory READMEs contain:**
- Purpose of the directory
- File organisation
- Index of contents
- Links to relevant documentation

### CHANGELOG.md

**Purpose**: Complete release history for users

**Structure:**
- Most recent version first
- Version number and date
- Changes organised by type:
  - Added - new features
  - Changed - changes to existing functionality
  - Deprecated - features to be removed
  - Removed - features removed
  - Fixed - bug fixes
  - Security - security fixes

**Style:**
- One line per change
- Start with past tense verb ("Added", "Fixed", "Changed")
- Include issue/PR numbers
- Be specific about what changed

## Links and References

### Internal Links

- Use relative paths for links within the repository
- Verify links work from the file's location
- Use descriptive link text (not "click here")

**Example:**
```markdown
See [Parameters Guide](parameters.md) for details.
See [Configuration section](configuration.md#basic-configuration) for examples.
```

### External Links

- Use full URLs for external resources
- Include link text that describes the destination
- Verify links are current and accessible

### Code References

- Use backticks for inline code: `function_name()`
- Use triple backticks for code blocks with language specification
- Reference specific files, functions, or line numbers when relevant

## Formatting Standards

### Lists

**Use bullet lists for unordered items:**
- Item one
- Item two
- Item three

**Use numbered lists for sequential steps:**
1. First step
2. Second step
3. Third step

**Use consistent punctuation:**
- End list items with periods if they're complete sentences.
- Omit periods for short phrases or single words

### Emphasis

- Use **bold** for important terms on first use or key concepts
- Use *italics* sparingly for emphasis
- Use `code formatting` for function names, variables, constants, file paths

### Tables

Use tables for structured comparisons or reference material:

```markdown
| Feature | Description | Version |
|---------|-------------|---------|
| Feature1 | Does X | v1.0.0 |
| Feature2 | Does Y | v1.1.0 |
```

## Examples and Demonstrations

### Complete Working Examples

**All examples should:**
- Be runnable without modification (unless explicitly marked as pseudocode)
- Include necessary imports
- Show expected output where relevant
- Demonstrate real-world use cases
- Follow project coding standards

### Example Files (`examples/*.py`)

**When referencing examples:**
- List the example file in the documentation
- Provide a brief description of what it demonstrates
- Link to the file in the repository
- Consider including key snippets inline

**Example:**
```markdown
See [`examples/params_basic.py`](../examples/params_basic.py) for a complete example of parameter definition and access.
```

## Maintenance

### Keeping Documentation Current

**When code changes:**
- Update affected documentation immediately
- Check for related documentation in other files
- Update examples to reflect new APIs or patterns
- Add version annotations for new features

**When reviewing PRs:**
- Verify documentation is included
- Check examples are correct and follow standards
- Ensure navigation links are updated
- Confirm version annotations are present

### Documentation Checklist

Before completing documentation work:

- [ ] UK English spelling and conventions used
- [ ] Dispassionate, factual tone throughout
- [ ] No marketing language or internal jargon
- [ ] Navigation links present and correct
- [ ] Table of contents for longer documents
- [ ] Code examples follow project coding standards
- [ ] Version annotations for new features
- [ ] Internal links verified
- [ ] External links checked
- [ ] API signatures verified against source code
- [ ] Examples are complete and runnable
- [ ] Related documentation updated

## Planning Documents - Decision Status

**CRITICAL:** When creating or updating planning documents in `features/`:

- **Never mark decisions as "RESOLVED" without explicit user confirmation**
- Use "PENDING REVIEW" for proposed answers to "Further Considerations"
- Only change status to "RESOLVED" when the user explicitly approves the decision
- Decisions are resolved when the user is satisfied, not when the agent proposes an answer

## Related Instructions

This documentation standards file works in conjunction with:

- **`general.instructions.md`** - NO GUESSING POLICY, UK English, source citation requirements
- **`python.instructions.md`** - Python coding standards for code examples
- **`python37.instructions.md`** - Python 3.7 compatibility for code examples
- **`planning.instructions.md`** - CHANGES documentation style and structure

Always consult these files when working on documentation that includes code examples or when writing release notes.
