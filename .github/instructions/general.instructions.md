# General Instructions (All Projects)

These instructions apply to all files across all projects.

## CRITICAL: NO GUESSING POLICY

**NEVER guess or make assumptions about ANYTHING.**

If you are not certain about something, you must explicitly state that you don't know rather than guessing or making assumptions.

**This includes (but is not limited to):**
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

## CRITICAL: LOCALIZATION AND INTERNATIONALIZATION

**Use UK English spelling and conventions:**
- colour, not color
- organise, not organize
- behaviour, not behavior
- centre, not center
- licence, not license
- defence, not defense

**Use metric units:**
- metres, kilometres (not feet, miles)
- kilograms (not pounds)
- Celsius (not Fahrenheit)
- litres (not gallons)

**Do not use US-specific examples:**
- Do not assume US geography (no us-east, us-west, etc.)
- Do not assume US conventions, standards, or cultural references
- Use internationally neutral examples (north, south, east, west OR region-a, region-b, etc.)
- Do not use US-centric measurements, dates, or formats

**This applies to ALL work - code, documentation, examples, and any other content.**

## Communication Style

**Maintain clarity and directness in all responses:**
- Deliver complete information while matching response depth to the task's complexity
- For straightforward queries, keep answers brief - typically a few lines excluding code or tool invocations
- Expand detail only when dealing with complex work or when explicitly requested
- Optimize for conciseness while preserving helpfulness and accuracy
- Address only the immediate request, omitting unrelated details unless critical
- Target 1-3 sentences for simple answers when possible

**Avoid extraneous framing:**
- Skip unnecessary introductions or conclusions unless requested
- After completing file operations, confirm completion briefly rather than explaining what was done
- Respond directly without phrases like "Here's the answer:", "The result is:", or "I will now..."

**When executing non-trivial commands:**
- Explain their purpose and impact so users understand what's happening
- Particularly important for system-modifying operations

**Do NOT use emojis unless explicitly requested by the user.**

## Documentation Requirements

**All code must include appropriate documentation:**
- Public functions and classes require comprehensive docstrings
- Private/internal helpers require at minimum a one-line docstring explaining purpose
- Docstrings should explain purpose, inputs, outputs, and side-effects
- Use proper formatting for the language (e.g., Markdown for documentation files, language-specific docstring conventions for code)

**Code examples in documentation must follow all coding rules:**
- Python code examples must follow `python.instructions.md` naming and style rules
- Python 3.7 projects must follow `python37.instructions.md` compatibility rules
- Test code examples must follow `python-tests.instructions.md` structure rules
- All code in documentation is subject to the same standards as production code
- Do not use lazy placeholders or poor naming in examples - they teach bad habits

## Before Making Changes

**Always understand existing patterns first:**
1. Read relevant instruction files for the file type you're modifying
2. Examine existing patterns in the target file before adding new code
3. Check for related tests when modifying source code
4. Verify language/framework version compatibility requirements
5. Run existing tests to establish a baseline before changes

**When adding features:**
- Create focused, single-responsibility functions/classes
- Write comprehensive documentation
- Add appropriate tests
- Verify compliance with project standards

**When fixing bugs:**
- Identify the root cause
- Add a test that reproduces the bug (if applicable)
- Fix the underlying issue (do not modify tests to pass)
- Verify the fix with tests
- Check for similar issues elsewhere

## Domain-Specific Instructions

This general instructions file works in conjunction with domain-specific instruction files:

- **Python projects:** See `python.instructions.md` for Python coding standards
- **Python 3.7 projects:** See `python37.instructions.md` for version-specific requirements
- **Python tests:** See `python-tests.instructions.md` for test structure and standards
- **Planning/Changes:** See `planning.instructions.md` for issue planning and change documentation

Always consult the relevant domain-specific files when working in those areas.
