## Best Practices for Python 3.7 Projects

**Write code that's obviously compatible:**
- Prefer explicit, verbose code over clever shortcuts that might use new features
- Test with Python 3.7.0 specifically, not just 3.7.x
- Use CI/CD to enforce Python 3.7.0 compatibility
- Document any version-specific workarounds with comments

**When in doubt:**
- Check the Python 3.7 documentation specifically
- Test the feature in a Python 3.7.0 environment
- Prefer standard library features that existed in Python 3.6 (guaranteed to work in 3.7)
