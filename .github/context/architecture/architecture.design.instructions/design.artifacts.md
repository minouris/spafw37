## Design Artifacts

### Required Deliverables
1. **High-level architecture** - System boundaries, major components, responsibilities
2. **Component diagrams** - Internal structure, relationships, interfaces
3. **Interaction diagrams** - Message flows, sequence diagrams, state machines
4. **Design patterns** - Document patterns used and why
5. **Trade-off analysis** - Document alternatives considered and decisions made

### Code Examples in Architecture Documents

**CRITICAL RULE: NO CODE IMPLEMENTATIONS IN ARCHITECTURE DOCUMENTS**

Architecture documents are for **design**, not implementation. Code examples are **FORBIDDEN** unless:

1. **Explicitly requested** by the user with clear permission
2. **Absolutely minimal** - showing ONLY:
   - Function/method signatures (first line only)
   - Class definition headers (class name and inheritance only)
   - Interface contracts (method names and parameters only)
3. **Context-specific** - illustrating ONLY the concept being discussed in that specific section
4. **Never include**:
   - Implementation details (method bodies, logic, algorithms)
   - Multiple methods or functions in one example
   - Usage examples or instantiation code
   - Import statements or setup code
   - Comments explaining implementation

**USE DIAGRAMS INSTEAD:**
- Class diagrams for structure
- Sequence diagrams for interactions
- State diagrams for behaviour
- Flowcharts for logic

See `mermaid.instructions.md` for diagram examples and patterns.

**When in doubt: Use a diagram. Never use code.**

### Diagram Types
- **Context diagrams**: System boundaries and external actors
- **Component diagrams**: Static structure and relationships
- **Sequence diagrams**: Temporal interactions and message flows
- **State diagrams**: Component lifecycle and state transitions
- **Deployment diagrams**: Runtime organisation (if applicable)