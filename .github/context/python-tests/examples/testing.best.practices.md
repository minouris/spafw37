## Testing Best Practices

**Write clear, maintainable tests:**
- Keep tests simple and focused
- Use descriptive assertion messages when helpful
- Avoid complex logic in tests - tests should be obviously correct
- Use test fixtures and helpers to reduce duplication, but keep tests readable
- Mock external dependencies to keep tests fast and isolated
- Test the public API, not internal implementation details (unless testing internal helpers directly)