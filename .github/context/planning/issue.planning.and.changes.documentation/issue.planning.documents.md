## Issue Planning Documents

When creating issue planning documents, follow the structure defined in the ISSUE-PLAN template (see `.github/instructions/templates/ISSUE-PLAN.md`).

**Required sections (in order):**
1. **Overview** - Problem statement, architectural decisions, end result
2. **Implementation Methodology** (optional) - If following a specific pattern
3. **Table of Contents** - Links to all sections
4. **Program Flow Analysis** (when applicable) - Comparison of old vs new program flow
5. **Implementation Steps** - Numbered, detailed steps with files, tests, code examples
6. **Further Considerations** - Questions, decisions, and rationale
7. **Fixing Regressions** (if applicable) - Additional steps discovered during testing
8. **Success Criteria** - How to verify the implementation is complete
9. **Implementation Plan Changes** (if applicable) - Documents evolution of the plan
10. **CHANGES for vX.Y.Z Release** - See Changes Documentation below

**Key principles:**
- Be thorough and specific - include file paths, function names, exact specifications
- Break work into logical, sequential steps
- Include code examples for complex implementations
- Specify test requirements for each step
- Document architectural decisions and trade-offs
- Link back to table of contents from each section

**Reference the template at:** `.github/instructions/templates/ISSUE-PLAN.md`

### Program Flow Analysis Section

**When to include:** For issues that change how code flows through the system (refactorings, architectural changes, new execution paths).

**Position in document:** After Table of Contents, before Implementation Steps.

**Purpose:** Provide high-level understanding of what changes before diving into implementation details.

**Structure:**

1. **Section heading:** Use a descriptive title focused on the primary feature/behaviour being changed (not implementation-specific)
2. **Current Behaviour (Before Changes)** subsection with:
   - One paragraph summary explaining the current flow at a high level
   - Separate breakdowns for each usage scenario (if they differ) showing step-by-step flow
   - Result summary explaining the outcome
3. **New Behaviour (After Changes)** subsection with:
   - One subsection per behaviour mode/option
   - Each mode includes:
     - One paragraph summary explaining how this mode changes the flow
     - Separate breakdowns for each usage scenario (if they differ) showing complete step-by-step flow
     - Result summary explaining the outcome
4. **Key architectural changes** summary (bullet list of major implementation approach changes)

**Flow breakdown format:**

- Use numbered steps showing the complete call chain
- Include function names and module boundaries (e.g., "CLI → _parse_command_line()")
- Show data flowing through the system (e.g., "Receives tokenized params `[...]`")
- Indent sub-steps with bullet points to show nested calls
- Highlight decision points and branching logic
- Show where errors occur and how they propagate
- **Only include multiple usage scenarios if the flow differs between them** (e.g., CLI vs programmatic, synchronous vs asynchronous, different execution modes)

**Example structure:**

````markdown