# GitHub Actions Workflows

## Workflows

### test.yml

Reusable workflow for running tests.

- Builds Python 3.7.9 from source (with caching via `build-python.yml`)
- Installs dependencies
- Runs pytest with coverage
- Requires 80% test coverage by default (configurable)
- Called by other workflows via `workflow_call`

### build-python.yml

Reusable workflow for building Python from source.

- Builds Python 3.7.9 from source on ubuntu-latest
- Caches the built Python to speed up subsequent runs
- Called by `test.yml` and other workflows

### build-and-verify.yml

Reusable workflow for building and verifying the package.

- Builds source distribution and wheel
- Verifies package metadata with twine
- Uploads build artefacts

### pre-publish.yml

Runs on every push to any branch and on pull requests to the `main` branch.

- Prepares Python environment (builds from source with caching)
- Runs tests with 80% coverage requirement
- Builds and verifies package
- **Generates changelog** from issue plan files (runs `.github/scripts/generate_changelog.py`)
- Commits changelog updates with `[skip ci]`

### publish-dev.yml

Publishes dev releases to TestPyPI.

- Triggered by successful `Pre-Publish Validation` workflow on `main` branch
- Can also be triggered manually via `workflow_dispatch`
- Downloads pre-built packages from pre-publish workflow
- Publishes to TestPyPI
- Increments dev version (e.g., 1.0.0.dev0 → 1.0.0.dev1)
- Creates git tag and GitHub pre-release

### publish-stable.yml

Manual workflow for production releases to PyPI.

- Triggered manually via `workflow_dispatch` only
- Runs tests with 95% coverage requirement
- Strips `.dev` suffix from version
- Creates release branch
- Publishes to PyPI using Trusted Publisher (OIDC)
- Creates git tag and GitHub Release
- Bumps to next dev version for continued development

### backout-release.yml

Manual workflow for rolling back a release.

- Triggered manually via `workflow_dispatch`
- Requires version number and reason inputs
- Deletes GitHub Release
- Deletes git tag (local and remote)
- Deletes release branch
- Resets main branch to dev version
- **Note:** Cannot delete PyPI package (PyPI policy)

### update-pypi-docs.yml

Manual workflow for updating PyPI documentation without creating a new release.

- Triggered manually via `workflow_dispatch`
- Requires version number input
- Checks out the release tag
- Rebuilds and re-uploads package to PyPI
- Uses `skip-existing: true` to avoid conflicts
- Useful for fixing documentation errors after release
- Requires PyPI Trusted Publisher OIDC configuration

## Changelog Generation

The changelog is generated automatically as part of the `pre-publish.yml` workflow. This ensures:

1. **Proper Python environment**: Uses the cached Python 3.7.9 build from source (same as tests)
2. **Only runs after successful builds**: Changelog generation happens after tests and build verification pass
3. **Script-based generation**: Uses `.github/scripts/generate_changelog.py` to extract CHANGES sections from issue plan files in `features/`

### How Changelog Generation Works

1. The script reads the current version from `setup.cfg`
2. Finds all issue plan files (`features/issue-*.md`) targeting that version
3. Extracts CHANGES sections from each plan file
4. Combines them into a single changelog entry
5. Updates `CHANGELOG.md` with the new entry
6. Commits with `[skip ci]` to avoid triggering another workflow run

### Manual Changelog Generation

To generate a changelog manually:

```bash
# Generate for current version and update CHANGELOG.md
python3 .github/scripts/generate_changelog.py

# Generate for specific issues (output to stdout)
python3 .github/scripts/generate_changelog.py --issues 26,27,33 --output -

# Generate for specific version to file
python3 .github/scripts/generate_changelog.py --version 1.2.0 --output changelog_entry.md
```

## Setup Instructions

### 1. Create TestPyPI Account and API Token

1. Create an account at https://test.pypi.org/account/register/
2. Verify your email
3. Go to https://test.pypi.org/manage/account/token/
4. Create a new API token with scope "Entire account" (you can limit it to just this project after the first upload)
5. Copy the token (starts with `pypi-`)

### 2. Add Token to GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `TEST_PYPI_API_TOKEN`
5. Value: Paste the token from TestPyPI
6. Click **Add secret**

### 3. Configure PyPI Trusted Publisher (for stable releases)

For production releases to PyPI, configure Trusted Publisher OIDC:

1. Go to https://pypi.org/manage/project/spafw37/settings/publishing/
2. Add a new trusted publisher for GitHub Actions
3. Configure repository owner, name, and workflow file (`publish-stable.yml`)

### 4. Version Management

The version in `setup.cfg` follows the format: `X.Y.Z.devN`

- **Dev increments**: When code is published to TestPyPI, the version is automatically incremented (`.dev0` → `.dev1` → `.dev2`, etc.)
- **Stable releases**: The `.devN` suffix is stripped for production releases

### 5. First-Time Setup

On your first publish, TestPyPI might reject the package name if it's already taken. You may need to:
1. Choose a unique package name or
2. Claim the existing name if you own it

## How It Works

### Pre-Publish Flow

1. **Trigger**: Push to any branch or PR to `main`
2. **Prepare Python**: Build Python 3.7.9 from source (with caching)
3. **Test**: Run pytest with 80% coverage requirement
4. **Build**: Create source distribution and wheel
5. **Verify**: Check package metadata with twine
6. **Changelog**: Generate changelog from issue plan files
7. **Commit**: Push changelog updates with `[skip ci]`

### Dev Publish Flow

1. **Trigger**: Successful Pre-Publish workflow on `main`, or manual dispatch
2. **Download**: Get pre-built packages from pre-publish workflow
3. **Publish**: Upload to TestPyPI
4. **Version**: Increment dev version in `setup.cfg`
5. **Tag**: Create git tag and GitHub pre-release
6. **Commit**: Push version bump with `[skip ci]`

### Stable Release Flow

1. **Trigger**: Manual dispatch only
2. **Test**: Run tests with 95% coverage requirement
3. **Build**: Create source distribution and wheel
4. **Version**: Strip `.dev` suffix
5. **Branch**: Create release branch
6. **Publish**: Upload to PyPI via Trusted Publisher
7. **Tag**: Create git tag and GitHub Release
8. **Bump**: Increment to next dev version for continued development

### Testing the Package

After publishing to TestPyPI, you can test installation:

```bash
pip install -i https://test.pypi.org/simple/ spafw37
```

After a stable release, install from PyPI:

```bash
pip install spafw37
```

## Troubleshooting

### Workflow fails with "No such secret: TEST_PYPI_API_TOKEN"
- Make sure you've added the secret in GitHub repository settings
- The secret name must be exactly `TEST_PYPI_API_TOKEN`

### Package already exists on TestPyPI
- TestPyPI doesn't allow re-uploading the same version
- The workflow increments the version after each publish to prevent this
- If you need to test the same code again, manually increment the version first

### Version commit fails
- Check that the repository has write permissions
- The workflow uses `GITHUB_TOKEN` which should have push access by default
- If you have branch protection, you may need to allow the workflow to bypass it

### Changelog not being generated
- Ensure issue plan files exist in `features/` directory
- Plan files must have `## CHANGES for vX.Y.Z` section
- File names should match `issue-*.md` pattern
- Check that the version in `setup.cfg` matches the version in plan files
