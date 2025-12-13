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