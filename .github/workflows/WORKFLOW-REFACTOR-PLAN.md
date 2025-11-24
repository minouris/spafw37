# Workflow Refactor Implementation Plan

## Overview

This document defines the implementation plan for refactoring the GitHub Actions workflows to create a unified, parameterised release architecture that handles both dev and prod releases through a single reusable workflow.

## Goals

1. **Unified Release Architecture**: Dev and prod releases use the same underlying workflow, driven by configuration flags
2. **Python Build Consolidation**: Single Python build per workflow run, all jobs restore from cache
3. **Configurable Coverage**: 80% for dev releases, 95% for prod releases
4. **Dry Run Support**: All preparation steps visible, only final commits/pushes/publishes skipped
5. **Smart Changelog Aggregation**: First release gets full changelog, subsequent releases get issue-specific changes
6. **README Link Management**: Tags contain `/vX.Y.Z/` links, main branch maintains `/main/` links

## Current State Assessment

### Existing Workflows

- **`build-python.yml`**: Reusable workflow that builds Python 3.7.9 from source with caching ✅ (Complete)
- **`test.yml`**: Reusable workflow with `coverage_threshold` parameter ✅ (Complete)
- **`build-and-verify.yml`**: Reusable workflow for building and verifying wheel/sdist ✅ (Complete)
- **`increment-version.yml`**: Reusable workflow with `dry_run` support ✅ (Complete)
- **`release-dev.yml`**: Dev release launcher workflow (currently `publish-testpypi.yml`), needs coverage_threshold pass-through
- **`release-stable.yml`**: Prod release launcher workflow (currently `release.yml`), already uses coverage_threshold conditionally ✅
- **`milestone-release.yml`**: Creates GitHub releases, needs dry_run support

### Existing Scripts

- **`generate_changelog.py`**: Aggregates CHANGES from plan files ✅ (Python 3.7 compliant)
- **`generate_dev_release_notes.py`**: Generates release notes with smart aggregation
- **`increment_version.py`**: Bumps dev version counter ✅ (Python 3.7 compliant)
- **`find_artifacts.py`**: Extracts metadata from built packages ✅

## Implementation Steps

### Step 1: Update Triggers and Add Coverage Threshold

**File**: `.github/workflows/release-dev.yml` (rename from `publish-testpypi.yml`)

**Changes**:

1. **Update triggers**:
```yaml
on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run (skip TestPyPI publish and version bump)'
        required: false
        type: boolean
        default: false
```

2. **Set dry_run based on trigger**:
```yaml
jobs:
  prepare-python:
    uses: ./.github/workflows/build-python.yml
    with:
      python_version: '3.7.9'
      dry_run: ${{ github.event_name != 'push' || github.event.inputs.dry_run == 'true' }}
```

3. **Add coverage_threshold to test job**:
```yaml
test:
  needs: prepare-python
  uses: ./.github/workflows/test.yml
  with:
    python_version: '3.7.9'
    coverage_threshold: 80
```

**Logic**:
- Push to main: Live release (dry_run=false)
- Pull request or other branch push: Dry run preview (dry_run=true)
- Manual dispatch: User-controlled dry_run

**Rationale**: 
- Branch pushes and PRs should preview the release without publishing
- Only main branch pushes trigger actual releases
- Explicitly set 80% coverage requirement for dev releases

### Step 2: Create Unified Release Workflow

**File**: `.github/workflows/release-common.yml` (NEW)

**Purpose**: Single reusable workflow for both dev and prod releases

**Inputs**:
- `python_version` (string, default: '3.7.9')
- `coverage_threshold` (number, default: 80)
- `publish_to` (string: 'pypi' or 'testpypi')
- `version_operation` (string: 'increment-dev', 'strip-dev', or 'none')
- `create_release_branch` (boolean: true for prod, false for dev)
- `create_bugfix_branch` (boolean: true for prod, false for dev)
- `create_release` (boolean: true = release, false = pre-release)
- `generate_full_changelog` (boolean: true for prod, false for dev)
- `dry_run` (boolean, default: false)

**Jobs**:
1. `prepare-python`: Call build-python.yml
2. `test`: Call test.yml with coverage_threshold
3. `get_version`: Read setup.cfg, calculate release version
4. `prepare_release`: Git operations (branch, version, changelog, README, tag)
5. `build_and_verify`: Call build-and-verify.yml
6. `publish`: Publish to PyPI or TestPyPI
7. `post_release`: Version bump, release notes, GitHub release

**Key Logic**:

**Git Operations** (prepare_release job):
1. Create release branch (if `create_release_branch=true`)
   - Branch name: `release/vX.Y.Z`
   - Base: current commit
2. Update version in setup.cfg based on `version_operation`
   - `strip-dev`: X.Y.Z.devN → X.Y.Z
   - `increment-dev`: X.Y.Z.devN → X.Y.Z.dev(N+1)
   - `none`: No change
3. Update CHANGELOG.md version/date (if `generate_full_changelog=true`)
   - Change `[X.Y.Z.devN]` → `[X.Y.Z]` and add date
4. Update README.md links (if on release branch)
   - `/tree/main/` → `/tree/vX.Y.Z/`
   - `/blob/main/` → `/blob/vX.Y.Z/`
5. Commit changes to release branch
6. Create tag from release branch
   - Tag name: `vX.Y.Z` (or `vX.Y.Z.devN` for dev)
7. Create bugfix branch from tag (if `create_bugfix_branch=true`)
   - Branch name: `bugfix/X.Y.x`
8. Merge release branch to main (if release branch exists)
   - Use `git merge release/vX.Y.Z~1` to exclude README commit
   - This brings version/changelog changes to main, but keeps /main/ links

**Release Notes** (post_release job):
1. Generate notes via `generate_dev_release_notes.py`
   - Script checks for previous releases with same version prefix
   - First release: Full changelog aggregation
   - Subsequent: Current PR only
   - Prod (no .dev): Always full changelog (treated as "first")
2. Create GitHub release or pre-release
   - Release if `create_release=true`
   - Pre-release otherwise

**Version Bump** (post_release job):
1. After prod release: X.Y.Z → X.Y.(Z+1).dev0
2. After dev release: X.Y.Z.devN → X.Y.Z.dev(N+1)

**Dry Run Behavior**:
- All steps execute and show output
- Only skip: git push, PyPI publish, GitHub release creation
- Use step-level `if: inputs.dry_run != true` conditions

### Step 3: Refactor release-dev.yml Job Dependencies

**File**: `.github/workflows/release-dev.yml` (rename from `publish-testpypi.yml`)

**Current Job Sequence**:
```
prepare-python → test → build_and_verify → publish → increment-version
                                                   → dev-release
```

**New Job Sequence**:
```
prepare-python → test → build_and_verify → publish → increment-version → dev-release
```

**Key Changes**:
1. Make `dev-release` depend on `increment-version` (currently parallel)
2. Pass calculated `dry_run` value to all reusable workflows
3. Ensure all jobs respect dry_run flag

**Rationale**: 
- Dev release should happen after version increment (logical order)
- Consistent dry_run behavior across all jobs

### Step 4: Refactor release-stable.yml to Use release-common.yml

**File**: `.github/workflows/release-stable.yml` (rename from `release.yml`)

**Current**: Full implementation inline (468 lines)

**New**: Simple wrapper that calls release-common.yml

```yaml
name: Release (Stable)

on:
  workflow_dispatch:
    inputs:
      mode:
        description: 'Release mode'
        required: true
        type: choice
        options:
          - full-release
          - docs-only
        default: 'full-release'
      dry_run:
        description: 'Dry run (skip git push and PyPI publish)'
        required: false
        type: boolean
        default: false

jobs:
  release:
    uses: ./.github/workflows/release-common.yml
    with:
      python_version: '3.7.9'
      coverage_threshold: ${{ inputs.mode == 'full-release' && 95 || 80 }}
      publish_to: 'pypi'
      version_operation: 'strip-dev'
      create_release_branch: true
      create_bugfix_branch: true
      create_release: true
      generate_full_changelog: true
      dry_run: ${{ inputs.dry_run }}
    secrets: inherit
```

**Rationale**: 
- Eliminates ~400 lines of duplicate logic
- Single source of truth for release process
- Prod uses 95% coverage threshold

### Step 5: Add dry_run to milestone-release.yml

**File**: `.github/workflows/milestone-release.yml`

**Current State**: Already has dry_run input for workflow_call ✅

**Verification**: Ensure tag/release creation properly skipped when dry_run=true

### Step 6: Update generate_dev_release_notes.py

**File**: `.github/scripts/generate_dev_release_notes.py`

**Current Logic**: Checks for previous .dev releases

**Required Change**: Handle prod releases (no .dev suffix)

**New Logic** in `check_previous_dev_releases()`:
```python
def check_previous_dev_releases(version):
    # If version has no .dev suffix, it's a prod release
    # Prod releases should always get full changelog
    if not re.search(r'\.dev\d+$', version):
        return False
    
    # Dev release logic continues...
    base_version = re.sub(r'\.dev\d+$', '', version)
    # ... rest of existing logic
```

**Rationale**: Prod releases always treated as "first release" for changelog aggregation

## Verification Plan

### Phase 1: Dev Release Testing

1. **Dry Run Mode**:
   - Trigger release-dev workflow with dry_run=true
   - Verify all prep steps execute
   - Verify no commits/pushes/publishes occur
   - Check logs show version changes, changelog updates

2. **Live Dev Release**:
   - Trigger release-dev workflow with dry_run=false
   - Verify 80% coverage enforced
   - Verify version incremented (X.Y.Z.devN → X.Y.Z.dev(N+1))
   - Verify TestPyPI publication successful
   - Verify GitHub pre-release created
   - Verify changelog aggregation correct (first vs subsequent)

### Phase 2: Prod Release Testing

1. **Dry Run Mode**:
   - Trigger release-stable workflow with dry_run=true, mode=full-release
   - Verify release branch created
   - Verify version stripped (.devN → release)
   - Verify README links updated on branch
   - Verify tag created
   - Verify bugfix branch created
   - Verify no pushes to GitHub or PyPI

2. **Live Prod Release**:
   - Trigger release-stable workflow with dry_run=false, mode=full-release
   - Verify 95% coverage enforced
   - Verify version stripped correctly
   - Verify PyPI publication successful
   - Verify GitHub release created (not pre-release)
   - Verify bugfix branch exists
   - Verify main has version changes but /main/ links
   - Verify tag has /vX.Y.Z/ links in README
   - Verify full changelog in release notes

## Success Criteria

- ✅ All workflows use single Python build (restore from cache)
- ✅ Dev releases enforce 80% coverage
- ✅ Prod releases enforce 95% coverage
- ✅ Dry run mode shows complete preview
- ✅ Dev and prod share same workflow logic
- ✅ Changelog aggregation works correctly
- ✅ README links correct in tags vs main
- ✅ No duplicate code between workflows
- ✅ All scripts Python 3.7.0 compliant

## Risk Mitigation

1. **Test on Feature Branch First**: All changes tested on ci/verify-wheel-metadata branch
2. **Incremental Rollout**: Implement and test each step independently
3. **Rollback Plan**: Keep original workflows as .bak files until verified
4. **Dry Run First**: Always test dry_run mode before live releases

## Timeline

1. **Step 1**: Rename, update triggers, and add coverage_threshold to release-dev.yml (15 min)
2. **Step 2**: Create release-common.yml (60 min)
3. **Step 3**: Refactor release-dev.yml job dependencies (10 min)
4. **Step 4**: Rename and refactor release-stable.yml (15 min)
5. **Step 5**: Verify milestone-release.yml (5 min)
6. **Step 6**: Update generate_dev_release_notes.py (10 min)
7. **Testing**: Phase 1 and 2 verification (30 min)

**Total Estimated Time**: 2.5 hours

## Notes

- All commits use `[skip ci]` where appropriate to avoid workflow loops
- Python build caching already consolidated ✅
- Type hints already removed from scripts ✅
- Job ordering already correct (test before build) ✅
