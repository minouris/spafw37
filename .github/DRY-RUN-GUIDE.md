# Dry Run Mode for GitHub Actions

## Overview

Both the `release.yml` and `publish-testpypi.yml` workflows now support a **dry run mode** that lets you test the complete workflow without making permanent changes to git or publishing to PyPI/TestPyPI.

## What Gets Skipped in Dry Run Mode

### Release Workflow (`release.yml`)
When `dry_run: true`:
- ✅ Runs all tests with coverage requirements
- ✅ Builds Python from source (if needed)
- ✅ Creates local git branches and commits
- ✅ Builds package (sdist + wheel)
- ✅ Verifies wheel metadata
- ❌ **Skips** all `git push` operations
- ❌ **Skips** PyPI publish
- ❌ **Skips** GitHub Release creation

### Publish to TestPyPI Workflow (`publish-testpypi.yml`)
When `dry_run: true`:
- ✅ Runs tests
- ✅ Builds package
- ✅ Verifies metadata
- ❌ **Skips** TestPyPI publish
- ❌ **Skips** version increment commit

## How to Use

### Manual Trigger (Recommended for Testing)

#### Release Workflow
1. Go to **Actions** → **Release**
2. Click **Run workflow**
3. Select branch: `ci/verify-wheel-metadata` (or your feature branch)
4. Choose **Release mode**: `full-release` or `docs-only`
5. ✅ **Check** the **Dry run** checkbox
6. Click **Run workflow**

#### Publish to TestPyPI Workflow
1. Go to **Actions** → **Publish to TestPyPI (Dev)**
2. Click **Run workflow**
3. Select branch: `ci/verify-wheel-metadata` (or your feature branch)
4. ✅ **Check** the **Dry run** checkbox
5. Click **Run workflow**

### Automatic Trigger
- `publish-testpypi.yml` still runs automatically on push to `main`
- Automatic runs use `dry_run: false` (default)
- Only manual triggers can enable dry run mode

## What You'll See

### Console Output
```
[DRY RUN] Skipping: git push origin release/v1.2.3
[DRY RUN] Skipping: git push origin v1.2.3
[DRY RUN] Skipping: git push origin main
[DRY RUN] Skipping PyPI publish
Would publish the following files:
-rw-r--r-- 1 runner docker 8.5K Nov 24 12:34 spafw37-1.2.3-py3-none-any.whl
-rw-r--r-- 1 runner docker  45K Nov 24 12:34 spafw37-1.2.3.tar.gz
```

### Workflow Summary
The summary page will show:
```
## Release Workflow Summary
**Mode:** full-release
**Version:** 1.2.3
**Dry Run:** true

⚠️ **This was a dry run - no permanent changes were made**
```

## Local State After Dry Run

After a dry run completes, your local git state in the workflow runner includes:
- New branches (e.g., `release/v1.2.3`, `bugfix/1.2.x`)
- Modified files (`setup.cfg`, `CHANGELOG.md`, `README.md`)
- Git tags (e.g., `v1.2.3`)

**But none of these are pushed to the remote repository.**

The runner is ephemeral and discarded after the workflow completes, so these changes don't persist anywhere.

## Testing Strategy

### Before a Real Release
1. **First**: Run with `dry_run: true` to verify:
   - Tests pass with required coverage
   - Package builds correctly
   - Metadata is valid (`Requires-Python: >=3.7`)
   - Version numbers are correct
   - No workflow syntax errors

2. **Then**: Run with `dry_run: false` to:
   - Actually publish the release
   - Push all branches and tags
   - Create GitHub Release

### Benefits
- Test complex release orchestration without consequences
- Validate workflow changes before merging
- Debug version numbering issues
- Verify metadata changes
- Confirm artifact building works on GitHub runners

## Example Use Cases

### Testing This PR (`ci/verify-wheel-metadata`)
```bash
# Dry run the release workflow on this branch
# Go to Actions → Release → Run workflow
# Branch: ci/verify-wheel-metadata
# Mode: full-release
# Dry run: ✅ (checked)
```

This will:
- Build the package with the new `build-and-verify` workflow
- Run the new verification scripts
- Show you what would be published
- Confirm all metadata is correct
- NOT push anything or publish anywhere

### Testing Version Bump Logic
```bash
# Dry run with docs-only mode to skip changelog generation
# This runs faster and focuses on version logic
# Branch: main
# Mode: docs-only
# Dry run: ✅ (checked)
```

## Pro Tips

1. **Check the Artifacts**: Even in dry run mode, the `dist` artifact is uploaded. You can download it from the workflow run page to inspect the built packages locally.

2. **Review Logs**: The dry run logs show exactly what commands would have been executed, making it easy to spot issues.

3. **Fast Iteration**: Use dry run mode to quickly test workflow changes without waiting for slow operations like PyPI uploads.

4. **Coverage Testing**: Use `full-release` mode with `dry_run: true` to test the higher (95%) coverage threshold without making a release.
