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