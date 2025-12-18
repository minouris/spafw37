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

[Detailed implementation and tests will be added in Steps 3-4]

[↑ Back to top](#table-of-contents)

### 2. Add conditional execution to build and test jobs

**File:** `.github/workflows/pre-publish.yml`

Modify the existing jobs (`test`, `build-and-verify`, `update-changelog`) to conditionally execute based on the output from the file change detection job. Jobs should:
- Always run if `has_code_changes == 'true'`
- Always run if the workflow was manually triggered
- Skip execution if `has_code_changes == 'false'` and workflow was automatic

This ensures that CI/CD metadata changes don't waste compute resources running unnecessary builds and tests.

**Implementation approach:**
- Add `needs: check-changes` to each job that should be conditional
- Add `if:` conditions that check the output from the `check-changes` job
- Preserve the existing job logic unchanged

[Detailed implementation will be added in Step 4]

[↑ Back to top](#table-of-contents)

### 3. Update publish-dev workflow to handle skipped builds

**File:** `.github/workflows/publish-dev.yml`

The Publish Dev Release workflow is triggered when Pre-Publish Validation completes successfully. However, if the build was skipped due to no code changes, the workflow should not proceed with publishing.

Update the workflow to:
1. Check whether the `dist-packages` artifact exists (it won't if build was skipped)
2. Skip the publish step if no artifact is available
3. Add informational logging to indicate why the publish was skipped

This prevents attempting to publish non-existent packages and makes the workflow behaviour explicit in the logs.

[Detailed implementation will be added in Step 4]

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

### 3. How to handle the very first commit with no previous release?

**Question:** What should happen when there are no release tags yet (new repository or before first release)?

**Answer:** TO BE DETERMINED - needs implementation decision

**Rationale:**
- If no tags exist, `git describe --tags` will fail
- We should assume this is a first release and allow the build to proceed
- This is a one-time edge case that won't occur after the first release

**Implementation:** Add fallback logic in Step 1 to handle missing tags

[↑ Back to top](#table-of-contents)

---

### 4. Should manual workflow dispatches bypass the check?

**Question:** When a user manually triggers the workflow via `workflow_dispatch`, should the file change check be bypassed?

**Answer:** TO BE DETERMINED - requires user input

**Rationale:**
- **Pro (bypass):** Manual triggers indicate user intent to publish regardless of changes
- **Con (check always):** Consistent behaviour regardless of trigger type
- **Recommendation:** Bypass the check for manual triggers to allow force-publishing if needed

**Implementation:** Add conditional check in Step 1 to detect `github.event_name == 'workflow_dispatch'`

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
