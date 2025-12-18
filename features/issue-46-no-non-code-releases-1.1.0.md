# Issue #46: Add check to workflows to only build / bump version number if there are code changes in src

**GitHub Issue:** https://github.com/minouris/spafw37/issues/46

## Overview

The current CI/CD workflow configuration triggers builds and version bumps for all changes pushed to the main branch, regardless of whether those changes affect the actual package code. This results in unnecessary TestPyPI releases and version increments when only CI/CD configuration files, GitHub metadata, or other non-code files are modified.

Changes to files in the `.github/` directory, documentation that doesn't affect the package itself, or other metadata files should not trigger publication workflows. Only changes to actual Python code in `src/`, `tests/`, or `examples/`, or changes to user-facing documentation that ships with the package, should result in a new release.

This implementation will add a file change detection mechanism to the Pre-Publish Validation workflow that checks whether relevant files have changed since the last release. If no relevant changes are detected, the workflow will skip the build and artifact upload steps, preventing the subsequent Publish Dev Release workflow from running.

**Key architectural decisions:**

- **Detection point:** File change detection occurs in the Pre-Publish Validation workflow before running tests and building distributions
- **Scope of relevant changes:** Changes to `src/`, `tests/`, `examples/`, `doc/`, `README.md`, `setup.py`, `setup.cfg`, `pyproject.toml` trigger releases
- **Workflow control:** Use GitHub Actions conditional execution to skip build and publish jobs when no relevant changes are detected
- **Git-based detection:** Use `git diff` to compare current commit against the most recent release tag to identify changed files
- **Backward compatibility:** Manual workflow_dispatch triggers bypass the check and always build/publish

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add file change detection step to pre-publish workflow](#1-add-file-change-detection-step-to-pre-publish-workflow)
  - [2. Add conditional execution to build and test jobs](#2-add-conditional-execution-to-build-and-test-jobs)
  - [3. Update publish-dev workflow to handle skipped builds](#3-update-publish-dev-workflow-to-handle-skipped-builds)
- [Further Considerations](#further-considerations)
  - [1. Should documentation changes trigger releases?](#1-should-documentation-changes-trigger-releases)
  - [2. What about changes to dependencies?](#2-what-about-changes-to-dependencies)
  - [3. How to handle the very first commit with no previous release?](#3-how-to-handle-the-very-first-commit-with-no-previous-release)
  - [4. Should manual workflow dispatches bypass the check?](#4-should-manual-workflow-dispatches-bypass-the-check)
- [Success Criteria](#success-criteria)

[↑ Back to top](#table-of-contents)

## Implementation Steps

### 1. Add file change detection step to pre-publish workflow

**File:** `.github/workflows/pre-publish.yml`

Add a new job at the start of the Pre-Publish Validation workflow that:
1. Checks out the repository with full history (`fetch-depth: 0`)
2. Finds the most recent release tag (e.g., `v1.0.1.dev3`)
3. Uses `git diff` to list files changed between that tag and the current commit
4. Determines whether any of the changed files are in the relevant directories/files
5. Sets an output variable indicating whether to proceed with build

The job will run before all other jobs and its output will be used to conditionally execute subsequent jobs.

**Implementation details:**

- **Relevant file patterns:** `src/`, `tests/`, `examples/`, `doc/`, `README.md`, `setup.py`, `setup.cfg`, `pyproject.toml`
- **Tag detection:** Use `git describe --tags --abbrev=0` to find the most recent tag
- **Fallback:** If no tags exist (first release), assume changes exist and proceed with build
- **Manual triggers:** When workflow is manually triggered via `workflow_dispatch`, bypass the check and always build

**Detailed implementation:**

Add this new job immediately after the `jobs:` declaration and before `prepare-python:`:

```yaml
jobs:
  check-changes:
    runs-on: ubuntu-latest
    outputs:
      has_code_changes: ${{ steps.check.outputs.has_code_changes }}
    steps:
    - name: Checkout code with full history
      uses: actions/checkout@v3
      with:
        fetch-depth: 0

    - name: Check for relevant file changes
      id: check
      run: |
        # If manually triggered, always proceed with build
        if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
          echo "Manual trigger detected - bypassing file change check"
          echo "has_code_changes=true" >> $GITHUB_OUTPUT
          exit 0
        fi
        
        # Find the most recent tag
        LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
        
        # If no tags exist, allow build to proceed
        if [ -z "$LATEST_TAG" ]; then
          echo "No tags found - allowing build to proceed"
          echo "has_code_changes=true" >> $GITHUB_OUTPUT
          exit 0
        fi
        
        echo "Checking changes since tag: $LATEST_TAG"
        
        # Get list of changed files since the last tag
        CHANGED_FILES=$(git diff --name-only "$LATEST_TAG" HEAD)
        
        # Define patterns for files that should trigger a release
        RELEASE_PATTERNS="^(src/|tests/|examples/|doc/|README\.md|setup\.py|setup\.cfg|pyproject\.toml)"
        
        # Check if any changed files match the release patterns
        if echo "$CHANGED_FILES" | grep -E "$RELEASE_PATTERNS" > /dev/null; then
          echo "Release-worthy changes detected:"
          echo "$CHANGED_FILES" | grep -E "$RELEASE_PATTERNS"
          echo "has_code_changes=true" >> $GITHUB_OUTPUT
        else
          echo "No release-worthy changes detected"
          echo "Changed files:"
          echo "$CHANGED_FILES"
          echo "has_code_changes=false" >> $GITHUB_OUTPUT
        fi
```

**Logic explanation:**

1. **Manual trigger bypass:** First check if `github.event_name` is `workflow_dispatch` - if so, set `has_code_changes=true` and exit
2. **Find latest tag:** Use `git describe --tags --abbrev=0` with error handling (`2>/dev/null || echo ""`)
3. **Handle missing tags:** If `LATEST_TAG` is empty, set `has_code_changes=true` and exit
4. **Get changed files:** Use `git diff --name-only "$LATEST_TAG" HEAD` to list all changed files
5. **Pattern matching:** Use `grep -E` with regex pattern to check if any files match release-worthy patterns
6. **Set output:** Set `has_code_changes` to either `true` or `false` based on whether matches were found

[↑ Back to top](#table-of-contents)

### 2. Add conditional execution to build and test jobs

**File:** `.github/workflows/pre-publish.yml`

Modify the existing jobs (`prepare-python`, `test`, `build-and-verify`, `update-changelog`) to conditionally execute based on the output from the file change detection job. Jobs should:
- Always run if `has_code_changes == 'true'`
- Always run if the workflow was manually triggered (handled by check-changes job)
- Skip execution if `has_code_changes == 'false'` and workflow was automatic

This ensures that CI/CD metadata changes don't waste compute resources running unnecessary builds and tests.

**Implementation approach:**
- Add `needs: check-changes` to jobs that should be conditional
- Add `if:` conditions that check the output from the `check-changes` job
- Preserve the existing job logic unchanged
- Jobs that depend on conditional jobs will automatically skip via dependency chain

**Detailed implementation:**

**Change 1:** Update `prepare-python` job (currently line 16):

```yaml
  prepare-python:
    needs: check-changes
    if: needs.check-changes.outputs.has_code_changes == 'true'
    runs-on: ubuntu-latest
```

**Change 2:** Update `test` job (currently line 60):

```yaml
  test:
    needs: [check-changes, prepare-python]
    if: needs.check-changes.outputs.has_code_changes == 'true'
    runs-on: ubuntu-latest
```

**Note:** The `build-and-verify` and `update-changelog` jobs already depend on `test` through their `needs:` declarations, so they will automatically be skipped when `test` is skipped. No additional changes needed for those jobs.

**Dependency chain:**
- `check-changes` → `prepare-python` → `test` → `build-and-verify` → `update-changelog`
- If `check-changes` outputs `has_code_changes=false`, all subsequent jobs skip automatically

[↑ Back to top](#table-of-contents)

### 3. Update publish-dev workflow to handle skipped builds

**File:** `.github/workflows/publish-dev.yml`

The Publish Dev Release workflow is triggered when Pre-Publish Validation completes successfully. However, if the build was skipped due to no code changes, the workflow should not proceed with publishing.

Update the workflow to:
1. Check whether the `dist-packages` artifact exists (it won't if build was skipped)
2. Skip the publish step if no artifact is available
3. Add informational logging to indicate why the publish was skipped

This prevents attempting to publish non-existent packages and makes the workflow behaviour explicit in the logs.

**Detailed implementation:**

**Change 1:** Add artifact existence check step after "Download pre-built packages" (after line 42):

```yaml
    - name: Check if artifacts exist
      if: github.event_name == 'workflow_run'
      id: check_artifacts
      run: |
        if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
          echo "Artifacts found - proceeding with publish"
          echo "has_artifacts=true" >> $GITHUB_OUTPUT
        else
          echo "No artifacts found - build was skipped due to no code changes"
          echo "has_artifacts=false" >> $GITHUB_OUTPUT
        fi
```

**Change 2:** Make the "Publish to TestPyPI" step conditional (currently line 103):

```yaml
    - name: Publish to TestPyPI
      if: |
        github.event_name == 'workflow_dispatch' || 
        (github.event_name == 'workflow_run' && steps.check_artifacts.outputs.has_artifacts == 'true')
      uses: actions/download-artifact@v4
      with:
        repository-url: https://test.pypi.org/legacy/
        password: ${{ secrets.TEST_PYPI_API_TOKEN }}
```

**Change 3:** Make version bump conditional on artifacts existing (currently line 109):

```yaml
    - name: Bump version after successful publish
      if: |
        inputs.skip_version_bump != 'true' &&
        (github.event_name == 'workflow_dispatch' || 
         (github.event_name == 'workflow_run' && steps.check_artifacts.outputs.has_artifacts == 'true'))
      id: bump_version
```

**Change 4:** Make subsequent steps (tag creation, release notes, GitHub release) also conditional on artifacts existing by adding the same condition pattern to each step.

**Logic explanation:**

1. After downloading artifacts (which will be empty/missing if build skipped), check if `dist/` directory exists and contains files
2. Set `has_artifacts` output variable based on this check
3. Make all publish-related steps conditional on either:
   - Manual trigger (`workflow_dispatch`), OR
   - Automatic trigger (`workflow_run`) AND artifacts exist
4. This ensures manual triggers always work, but automatic triggers only proceed when artifacts were actually built

**Note:** The workflow will complete successfully even when skipping publish steps, which is the desired behaviour.

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Should documentation changes trigger releases? - RESOLVED

**Question:** Should changes to documentation files in `doc/` trigger a new release, or should only code changes (src/, tests/, examples/) trigger releases?

**Answer:** Yes, documentation in `doc/` should trigger a release. Documentation changes may be to correct errors in documentation, and these corrections should be made available to users via a new release.

**Rationale:**
- Documentation is part of the package and ships with the package on PyPI
- Documentation corrections and improvements are valuable to users
- Users may want updated docs available when they install the package
- Including `doc/` ensures documentation fixes are properly versioned and distributed

**Implementation:** The file pattern list in Step 1 will include `doc/` as a release-triggering directory

[↑ Back to top](#table-of-contents)

---

### 2. What about changes to dependencies? - RESOLVED

**Question:** Should changes to `requirements.txt` or `requirements-dev.txt` trigger a release even if no code changed?

**Answer:** No, dependency changes should not trigger releases on their own. Dependency changes will most likely occur prior to, or alongside, code commits that require those dependencies.

**Rationale:**
- Dependency updates typically accompany code changes that use those dependencies
- Standalone dependency updates without corresponding code changes are rare
- If a dependency must be updated for security or compatibility, it will be accompanied by code that uses or requires the updated dependency
- Both `requirements.txt` and `requirements-dev.txt` should be excluded from release-triggering patterns

**Implementation:** The file pattern list in Step 1 will exclude both `requirements.txt` and `requirements-dev.txt`

[↑ Back to top](#table-of-contents)

---

### 3. How to handle the very first commit with no previous release? - RESOLVED

**Question:** What should happen when there are no release tags yet (new repository or before first release)?

**Answer:** The workflow should not rely on a previous tag existing. If no tags exist, the workflow should handle this gracefully and allow the build to proceed. While the very first commit of the project is unlikely to contain usable code and it is acceptable for this to fail, the build system must not break due to missing tags.

**Rationale:**
- If no tags exist, `git describe --tags` or similar commands will fail
- The workflow must handle this case without breaking
- Assuming changes exist and allowing the build to proceed is the safest approach
- This is a one-time edge case that won't occur after the first release
- Relying on a tag existing may itself be a bug that needs to be addressed

**Implementation:** Add fallback logic in Step 1 that detects when no tags exist and defaults to allowing the build to proceed

[↑ Back to top](#table-of-contents)

---

### 4. Should manual workflow dispatches bypass the check? - RESOLVED

**Question:** When a user manually triggers the workflow via `workflow_dispatch`, should the file change check be bypassed?

**Answer:** Yes, manual workflow invocations should skip the file change check. Direct user intervention should always override automated behaviours.

**Rationale:**
- Manual triggers indicate explicit user intent to publish regardless of detected changes
- Users may need to force a release for various reasons (hotfix, republish, etc.)
- Automated checks serve to prevent unintended releases, but manual triggers are intentional
- This provides an escape hatch for edge cases not covered by automated logic

**Implementation:** Add conditional check in Step 1 to detect `github.event_name == 'workflow_dispatch'` and bypass file change detection when true

[↑ Back to top](#table-of-contents)

---

## Success Criteria

The implementation is successful when:

- [ ] Pre-Publish Validation workflow includes a file change detection step
- [ ] File change detection correctly identifies whether relevant files changed since last release
- [ ] Build and test jobs are skipped when only CI/CD files or GitHub metadata changed
- [ ] Build and test jobs run normally when code/docs/examples/tests changed
- [ ] Publish Dev Release workflow handles skipped builds gracefully
- [ ] Manual workflow triggers (via workflow_dispatch) can override the skip behaviour
- [ ] First release (no prior tags) works correctly
- [ ] All existing tests continue to pass
- [ ] Workflow runs complete successfully for both "changes detected" and "no changes" scenarios
- [ ] Version numbers are not bumped when no relevant code changes occurred

[↑ Back to top](#table-of-contents)

---
