# Release Process

This document describes the release process for spafw37.

## Prerequisites

Before creating a release, ensure:

1. All changes for the release are merged to `main`
2. All tests are passing on `main`
3. PyPI Trusted Publisher is configured for this repository (see [Configuration](#configuration) below)

## Creating a Release

Releases are created manually using GitHub Actions:

1. Go to the **Actions** tab in the GitHub repository
2. Select the **Release** workflow from the left sidebar
3. Click **Run workflow** button
4. Select the `main` branch (should be selected by default)
5. Click **Run workflow** to start the release process

## What Happens During Release

The release workflow automatically:

1. **Runs all tests** - Verifies that all tests pass and coverage targets are met (80%)

2. **Removes development suffix** - Changes version from `X.Y.Z.devN` to `X.Y.Z` in `setup.cfg`

3. **Generates changelog** - Uses AI to create a concise, categorized summary of changes (or falls back to structured commit list if AI is unavailable)

4. **Creates release branch** - Creates a `release/vX.Y.Z` branch with updated README links pointing to the tagged documentation

5. **Updates README links** - Changes all documentation and example links from `/main/` to `/vX.Y.Z/` so the README on the tag points to the correct tagged documentation

6. **Creates git tag** - Creates a version tag (e.g., `v1.0.0`) from the release branch and pushes it

7. **Creates bugfix branch** - Creates a `bugfix/X.Y.x` branch from the tag for future patch releases

8. **Publishes to PyPI** - Builds distribution packages and uploads them using PyPI Trusted Publisher (OIDC authentication, no API token needed)

9. **Bumps development version** - Increments the patch version and adds `.dev0` suffix on `main` (e.g., `1.0.0` → `1.0.1.dev0`)

10. **Creates GitHub Release** - Creates a GitHub Release with install instructions

All commits use `[skip ci]` to avoid triggering the test workflow unnecessarily.

## Version Numbering

spafw37 uses semantic versioning with development suffixes:

- **Release versions**: `X.Y.Z` (e.g., `1.0.0`, `1.2.3`)
- **Development versions**: `X.Y.Z.devN` (e.g., `1.0.1.dev0`, `1.0.1.dev5`)

The release workflow automatically:
- Removes `.devN` suffix for the release
- Increments the patch version (`Z`) by one after release
- Adds `.dev0` suffix for continued development

## Example Release Cycle

```
1.0.0.dev9        # Current development version
    ↓
1.0.0             # Release workflow removes .dev9
    ↓
[Tagged as v1.0.0 and published to PyPI]
    ↓
[Branch bugfix/1.0.x created from v1.0.0]
    ↓
1.0.1.dev0        # Workflow bumps to next dev version on main
    ↓
1.0.1.dev1        # TestPyPI workflow increments on each push
1.0.1.dev2
...
```

## Bugfix Branches

Each release automatically creates a bugfix branch for that release series:

- Release `1.0.0` creates branch `bugfix/1.0.x`
- Release `1.1.0` creates branch `bugfix/1.1.x`
- Release `2.0.0` creates branch `bugfix/2.0.x`

### Using Bugfix Branches

To create a bugfix release (e.g., `1.0.1` after `1.0.0` is released):

1. **Cherry-pick or commit fixes** to the bugfix branch:
   ```bash
   git checkout bugfix/1.0.x
   git cherry-pick <commit-hash>
   # or make direct commits
   git commit -m "Fix critical bug"
   ```

2. **Update version** in `setup.cfg` manually:
   ```
   version = 1.0.1
   ```

3. **Commit the version change**:
   ```bash
   git commit -am "Prepare bugfix release 1.0.1 [skip ci]"
   git push origin bugfix/1.0.x
   ```

4. **Run release workflow** targeting the bugfix branch:
   - Go to Actions → Release → Run workflow
   - Select the `bugfix/1.0.x` branch (not main)
   - Click Run workflow

The workflow will:
- Tag as `v1.0.1`
- Publish to PyPI
- Update changelog
- Bump version to `1.0.2.dev0` on the bugfix branch

### When to Use Bugfix Branches

- Critical security fixes for older releases
- Bug fixes for production deployments not yet on latest version
- Maintaining multiple supported versions

**Note**: Regular development continues on `main`. Only use bugfix branches for patch releases to older versions.

## Manual Version Management

If you need to do a minor or major version bump instead of patch:

1. Manually edit `setup.cfg` before running the release workflow
2. Change version to desired release version (e.g., `1.1.0` or `2.0.0`)
3. Commit and push: `git commit -am "Prepare for X.Y.Z release [skip ci]"`
4. Run the release workflow as normal

The workflow will use whatever version is in `setup.cfg` (minus any `.dev` suffix) as the release version.

## Changelog Format

The `CHANGELOG.md` is automatically generated using AI to create concise, categorized summaries:

```markdown
# Changelog

## [1.0.0] - 2025-11-15

### Added
- Inline definitions feature for parameters and commands
- AI-powered changelog generation in release workflow

### Changed
- Updated documentation with inline definition examples
- Improved parameter validation error messages

### Fixed
- Parameter conflicts with framework-reserved names in examples

*For detailed changes, see the [commit history](https://github.com/minouris/spafw37/compare/v0.9.0...v1.0.0).*

## [0.9.0] - 2025-11-01

### Added
- Initial release
```

The workflow uses a multi-tier approach:
1. **GitHub Copilot** (if available via `gh` CLI)
2. **OpenAI API** (if `OPENAI_API_KEY` secret is configured)
3. **Structured commit list** (fallback if no AI is available)

The AI analyzes:
- Commit messages
- Changed files
- Diff statistics

And generates a changelog that:
- Groups changes by category (Added, Changed, Fixed, Removed, etc.)
- Uses clear, user-friendly language
- Highlights the most important changes
- Keeps entries concise
- Links to full commit history

**Tip**: Write clear, descriptive commit messages as they feed into the AI's analysis.

## Troubleshooting

### Release Workflow Fails

If the release workflow fails:

1. Check the workflow logs in the Actions tab to identify the failure point
2. Common issues:
   - Tests failing (fix tests and retry)
   - Missing `PYPI_API_TOKEN` secret (add in repository settings)
   - Permission issues (check repository permissions)

### Version Already Published

If you try to publish a version that already exists on PyPI:

1. The workflow will fail at the PyPI upload step
2. You cannot overwrite existing PyPI versions
3. Manually increment the version in `setup.cfg` and retry

### Rollback a Release

To rollback a release:

1. The PyPI package cannot be deleted (PyPI policy)
2. Create a new patch release with fixes
3. You can delete the GitHub Release and tag if needed:
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

## Configuration

### PyPI Trusted Publisher

This project uses **PyPI Trusted Publisher** for secure, token-free publishing. This uses OpenID Connect (OIDC) to authenticate GitHub Actions directly with PyPI.

**Setup** (one-time configuration):

1. Go to PyPI project settings: <https://pypi.org/manage/project/spafw37/settings/publishing/>
2. Add a new "Trusted Publisher":
   - **Owner**: `minouris`
   - **Repository name**: `spafw37`
   - **Workflow name**: `release.yml`
   - **Environment name**: (leave blank)
3. Save the configuration

**Benefits**:
- No API tokens to manage or rotate
- More secure (scoped to specific workflow)
- Automatic authentication via OIDC
- No secrets to configure in GitHub

### GitHub Secrets

The following secrets can be configured in repository settings:

- `OPENAI_API_KEY` - *Optional* - OpenAI API key for AI-powered changelog generation
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

**Note**: If `OPENAI_API_KEY` is not provided, the workflow will try GitHub Copilot (via `gh` CLI) or fall back to a structured commit list.

### Workflow Permissions

The release workflow requires:
- `contents: write` - For creating releases and pushing commits/tags
- `id-token: write` - For PyPI Trusted Publisher OIDC authentication

- `contents: write` - For creating tags, releases, and pushing commits
- Standard `GITHUB_TOKEN` permissions for other operations
