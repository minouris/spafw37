## Architectural Patterns

**Facade Pattern:** If a project uses a facade module (e.g., `core.py`) as the public API, application code should import from the facade and use its delegate methods, not directly import internal modules.

**Respect Existing Architecture:** When modifying code, always understand the architectural intent before making changes. If a module uses a facade pattern, dependency injection, or other architectural patterns, preserve them. Do not mechanically apply import rules without considering the broader design.

**Internal vs. Public APIs:** Internal implementation modules should not be imported directly by external code. The public API should be clearly documented and separated from internal implementation details.
