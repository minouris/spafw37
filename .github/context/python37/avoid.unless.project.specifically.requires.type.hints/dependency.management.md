## Dependency Management

**Be careful with external dependencies:**
- Many packages have dropped Python 3.7 support
- Pin dependency versions to ensure Python 3.7 compatibility
- Test all dependencies with Python 3.7.0
- Consider vendoring critical dependencies if they drop 3.7 support