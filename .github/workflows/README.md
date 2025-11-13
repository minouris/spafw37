# GitHub Actions Workflows

## Workflows

### test.yml
Runs on every push and PR to `main`, `master`, or `develop` branches.
- Builds Python 3.7.9 from source (with caching)
- Installs dependencies
- Runs pytest with coverage
- Requires 80% test coverage to pass
- Can be called by other workflows (reusable workflow)

### publish-testpypi.yml
Runs on every push to `main` branch (typically after merging PRs).
- Calls the test.yml workflow first (must pass)
- Builds the package
- Publishes to TestPyPI (dev repository)
- Calls increment-version.yml workflow after successful publish

### increment-version.yml
Auto-increments the dev version number and commits it back.
- Can be called by other workflows (reusable workflow)
- Can be triggered manually via workflow_dispatch
- Reuses the same Python cache as other workflows
- Increments version in setup.cfg (e.g., 1.0.0.dev0 → 1.0.0.dev1)
- Commits changes with `[skip ci]` to avoid triggering another workflow run

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

### 3. Version Management

The version in `setup.cfg` follows the format: `X.Y.Z.devN`

- **Dev increments**: When code is pushed to `main`, the publish workflow automatically increments the dev number (`.dev0` → `.dev1` → `.dev2`, etc.)
- **Base version changes**: When you manually update the base version (e.g., `1.0.0` → `1.1.0`), the dev counter automatically resets to `.dev0`

#### Manual Version Increment

You can increment the version in three ways:

**1. Automatically after publish** (default):
- The publish workflow automatically calls increment-version.yml after successful publish

**2. Manually trigger workflow**:
- Go to Actions → Increment Version → Run workflow
- Select branch and click "Run workflow"

**3. Run script locally**:
```bash
# Increment dev version
python3 .github/scripts/increment_version.py

# Change base version and reset dev counter
python3 .github/scripts/increment_version.py 1.1.0
```

### 4. First-Time Setup

On your first publish, TestPyPI might reject the package name if it's already taken. You may need to:
1. Choose a unique package name or
2. Claim the existing name if you own it

## How It Works

### Publishing Flow

1. **Trigger**: Push to `main` branch (or manual workflow dispatch)
2. **Test**: Calls test.yml workflow (must pass)
3. **Build**: Create source distribution and wheel
4. **Publish**: Upload to TestPyPI at https://test.pypi.org/project/spafw37/
5. **Increment**: Bump dev version in `setup.cfg`
6. **Commit**: Push version bump back to `main` with `[skip ci]` to prevent infinite loop

### Version Increment Logic

The script checks if the base version (X.Y.Z) has changed:
- **Same base**: Increment dev number (`1.0.0.dev0` → `1.0.0.dev1`)
- **New base**: Reset dev counter (`1.1.0.dev0` after manually changing from `1.0.0.devN`)

### Testing the Package

After publishing, you can test installation from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ spafw37
```

## Publishing to Production PyPI

When ready for a production release:

1. Update version in `setup.cfg` to remove `.devN` (e.g., `1.0.0`)
2. Create a GitHub Release with a tag (e.g., `v1.0.0`)
3. Set up a separate workflow for production PyPI (or manually publish)

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
