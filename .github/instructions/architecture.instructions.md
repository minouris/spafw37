---
applyTo: "doc/architecture/**/*"
---

# Architecture Design Instructions

## CRITICAL: NO GUESSING POLICY

> Fully documented in [NO GUESSING POLICY in general.instructions.md](general.instructions.md#critical-no-guessing-policy) - those instructions should take priority.

**NEVER guess or make assumptions about:**
- External API specifications, endpoints, or data structures
- Third-party library behavior or usage patterns
- File formats, protocols, or standards you're not certain about
- Configuration requirements for external services

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Example of correct behavior:**
"I don't have access to the Patreon API v2 documentation, so I cannot verify the correct endpoint structure. You should check https://docs.patreon.com/ for the official API specification. Once you confirm the endpoint and data structure, I can implement it correctly."

**This applies to ALL work - code, configuration, documentation, and any other task.**

## Context

This instructions file applies to work in the `doc/architecture/**` folder. 

## Core Principles

### Clean Slate Design
- **No legacy assumptions**: Do not assume the new design must match any current implementation
- **Technology-agnostic**: Do not assume specific protocols, frameworks, or libraries without explicit requirements
- **Fresh thinking**: Question all previous design decisions and evaluate alternatives
- **Ground-up rebuild**: Start from requirements and design the optimal solution

### Design-First Approach
- **Design before implementation**: Complete architectural design before writing any code
- **Documentation-driven**: All design decisions must be documented before implementation
- **Iterative refinement**: Designs evolve through discussion and review
- **Validate assumptions**: Question and verify all design assumptions

## Design Workflow

### 1. Start High-Level
- Begin with conceptual models and system boundaries
- Define responsibilities and interfaces before internal details
- Use the glossary (`glossary.md`) to establish shared vocabulary
- Reference the index (`index.md`) to maintain document structure

### 2. Progressive Elaboration
- **Do NOT run ahead**: Wait for user direction before adding details
- Start with high-level concepts and flesh them out fully before drilling down
- Move from abstract to concrete only when explicitly requested
- Ask clarifying questions rather than making assumptions

### 3. Suggest, Don't Assume
- Offer design alternatives and trade-offs
- Present options rather than making unilateral decisions
- Explain reasoning behind recommendations
- Wait for user acceptance before proceeding

## Documentation Standards

### Architecture Documents
- **Location**: `doc/architecture/` directory. Create new documents under this directory
- **Format**: Markdown with Mermaid diagrams
- **Structure**: Modular files discussing different aspects
- **Navigation**: Maintain `index.md` and cross-references

### Mermaid Diagrams
- **Required**: Use Mermaid for all architectural diagrams
- **Style guide**: Follow `doc/architecture/reference.md` colour palette and conventions
- **Consistency**: Use the same colours for the same concepts across all diagrams
- **Clarity**: Create small, focused diagrams rather than monolithic ones
- **Dark mode**: Use dark backgrounds with white text (`colour:#fff`) as specified in reference.md

### Colour Palette (from reference.md)
- **Client/External Layer**: Dark red/pink tones
- **Adapter Layer**: Dark blue tones
- **Central Control Layer**: Dark purple tones
- **Backend/Data Layer**: Dark green tones
- **Supporting Components**: Dark magenta/purple tones
- **Synchronization**: Locks (red), Conditions (blue), Queues (magenta), Events (amber)

All nodes must explicitly set:
```
style NodeName fill:#1565c0,stroke:#333,stroke-width:2px,colour:#fff
```

### Document Organisation
- **Glossary**: Define all terms in `glossary.md` before using them
- **Index**: Update `index.md` when adding new documents
- **Cross-references**: Link related concepts across documents
- **Versioning**: Note design version and date in each document

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
- State diagrams for behavior
- Flowcharts for logic

**Example of ACCEPTABLE minimal code** (only when explicitly requested):
```python
def create_handler(base_class, config=None):
    class Handler(base_class):
        # Implementation details omitted

    return Handler
```

**Example of FORBIDDEN code** (NEVER include):
```python
def create_handler(base_class, config=None):
    class Handler(base_class):
        def __init__(self):
            super().__init__()
            self._processor = Processor(**config)
            # ... more implementation
        
        def handle_event(self, data):
            self._processor.dispatch(data)
            # ... more implementation
```

**When in doubt: Use a diagram. Never use code.**

### Diagram Types
- **Context diagrams**: System boundaries and external actors
- **Component diagrams**: Static structure and relationships
- **Sequence diagrams**: Temporal interactions and message flows
- **State diagrams**: Component lifecycle and state transitions
- **Deployment diagrams**: Runtime organisation (if applicable)

## Design Considerations

### Interface Independence
- **No interface assumptions**: Design should support multiple interface types and communication protocols
- **Adapter pattern**: Use adapters to isolate interface and protocol specifics
- **Canonical models**: Define interface-independent internal models and data structures
- **Extensibility**: Design for easy addition of new interfaces and protocols

### Deployment Environment Constraints
- **Version compatibility**: Designs must work within specified language/platform version constraints
- **Dependency management**: Consider restrictions on external dependencies and libraries
- **Resource efficiency**: Must run efficiently within target environment resource limits
- **Fault isolation**: Application failures must not crash or corrupt the host environment
- **Standard libraries**: Prefer standard libraries where possible to minimise dependencies

### Deployment Flexibility
- **Package formats**: Consider various packaging and distribution formats
- **Loading mechanisms**: Account for standard and non-standard loading patterns
- **Process constraints**: Consider subprocess limitations in target environments
- **Concurrency**: Design for thread-safety and concurrent operation where required

## Design Patterns to Consider

### Recommended Patterns
- **Adapter**: Isolate protocol and platform specifics
- **Mediator**: Central control coordinating components
- **Observer/Listener**: Event-driven communication
- **Command**: Encapsulate operations as objects
- **Factory**: Enable dependency injection and testing
- **State**: Model component lifecycle
- **Strategy**: Pluggable algorithms and behaviour variations

### Anti-Patterns to Avoid
- **God Object**: Distribute responsibilities appropriately
- **Tight Coupling**: Use interfaces and dependency injection
- **Premature Optimisation**: Design for clarity first
- **Feature Creep**: Focus on core requirements
- **Monolithic Components**: Favour small, focused components

## Design Review Checklist

Before finalising any design:

- [ ] All terms defined in glossary
- [ ] Mermaid diagrams follow style guide
- [ ] Interface independence maintained
- [ ] Language/platform version constraints respected
- [ ] Dependency constraints addressed
- [ ] Deployment environment constraints addressed
- [ ] Concurrency requirements considered
- [ ] Fault isolation ensured
- [ ] Design alternatives documented
- [ ] Trade-offs explained
- [ ] Component responsibilities clear
- [ ] Interfaces well-defined
- [ ] Index updated with new documents

## Interaction Style

### DO
- Ask clarifying questions before making design decisions
- Present multiple options with trade-offs
- Explain reasoning behind recommendations
- Start high-level and wait for direction to elaborate
- Use the established glossary and terminology
- Create focused, modular diagrams
- Document alternatives considered
- Follow the Mermaid style guide religiously
- **Use diagrams to illustrate all design concepts**
- **Show only minimal function/class signatures if explicitly requested**

### DON'T
- Provide code implementations (this is design work only)
- **Include ANY code examples unless explicitly requested and approved**
- **Show implementation details, method bodies, or logic in code**
- Assume specific protocols, frameworks, or libraries without requirements
- Make assumptions based on any previous implementation
- Add features or details without being asked
- Create monolithic diagrams trying to show everything
- Use light backgrounds or light text (breaks dark mode)
- Skip glossary definitions
- Anticipate or assume next steps

## Success Criteria

A good architecture design:

1. **Clear**: Easy to understand and communicate
2. **Modular**: Components have well-defined boundaries and responsibilities
3. **Flexible**: Can accommodate change and new requirements
4. **Testable**: Components can be tested in isolation
5. **Documented**: Decisions and trade-offs are recorded
6. **Interface-agnostic**: Not tied to specific interfaces or protocols without justification
7. **Constraint-aware**: Respects language, platform, and deployment environment constraints
8. **Maintainable**: Future developers can understand and modify

---

**Remember**: We are designing software from scratch. Question everything. Document thoroughly. Wait for user direction.
