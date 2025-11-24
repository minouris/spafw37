#!/usr/bin/env python3
"""Generate development release notes for GitHub releases."""

import re
import subprocess
import sys
from pathlib import Path


def find_pr_number():
    """Find the PR number associated with the current commit."""
    try:
        # Check git log for merge commit
        result = subprocess.run(
            ['git', 'log', '--merges', '--oneline', '--grep=Merge pull request', '-1'],
            capture_output=True,
            text=True,
            check=True
        )
        match = re.search(r'#(\d+)', result.stdout)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        pass
    
    return None


def check_previous_dev_releases(version):
    """Check if there are previous dev releases for the same base version."""
    # If version has no .dev suffix, it's a prod release
    # Prod releases should always get full changelog
    if not re.search(r'\.dev\d+$', version):
        return False
    
    # Strip .devN suffix to get base version
    base_version = re.sub(r'\.dev\d+$', '', version)
    pattern = f"v{base_version}.dev"
    
    try:
        # List all tags matching the pattern
        result = subprocess.run(
            ['git', 'tag', '-l', f'{pattern}*'],
            capture_output=True,
            text=True,
            check=True
        )
        tags = result.stdout.strip().split('\n')
        # Filter out empty strings and count
        matching_tags = [t for t in tags if t.strip()]
        return len(matching_tags) > 0
    except subprocess.CalledProcessError:
        return False


def extract_issue_from_pr(pr_number):
    """Extract issue number from PR title or description."""
    try:
        result = subprocess.run(
            ['gh', 'pr', 'view', pr_number, '--json', 'title,body'],
            capture_output=True,
            text=True,
            check=True
        )
        import json
        pr_data = json.loads(result.stdout)
        
        # Look for issue references in title or body
        text = f"{pr_data.get('title', '')} {pr_data.get('body', '')}"
        # Match patterns like "Issue #26", "#26", "issue-26"
        match = re.search(r'(?:issue[- ]?#?|#)(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        pass
    
    return None


def get_changelog_for_version(version):
    """Use generate_changelog.py to get full changelog for a version."""
    base_version = re.sub(r'\.dev\d+$', '', version)
    
    try:
        result = subprocess.run(
            ['python3', '.github/scripts/generate_changelog.py', 
             '--version', base_version, '--output', '-'],
            capture_output=True,
            text=True,
            check=True,
            cwd='.'
        )
        # Extract just the changes content (skip the header and date line)
        output = result.stdout
        lines = output.split('\n')
        changelog_lines = []
        skip_header = True
        
        for line in lines:
            if skip_header:
                if line.startswith('## ['):
                    skip_header = False
                continue
            if line.strip():
                changelog_lines.append(line)
        
        if changelog_lines:
            content = '\n'.join(changelog_lines)
            # Extract main content sections
            match = re.search(r'### (Issues Closed|Additions)\s*\n(.*)', content, re.DOTALL)
            if match:
                return match.group(0).strip()
            return content.strip()
        
        return f"Development version {version}"
    except subprocess.CalledProcessError:
        return f"Development version {version}\n\n(No changelog available)"


def get_changelog_for_issue(issue_number):
    """Use generate_changelog.py to get changelog for specific issue."""
    try:
        result = subprocess.run(
            ['python3', '.github/scripts/generate_changelog.py', 
             '--issues', issue_number, '--output', '-'],
            capture_output=True,
            text=True,
            check=True,
            cwd='.'
        )
        # Extract just the changes content (skip the header and date line)
        output = result.stdout
        # Find content after the version header line
        lines = output.split('\n')
        # Skip diagnostic output and find the changelog content
        in_changelog = False
        changelog_lines = []
        for line in lines:
            if line.startswith('## [') or line.startswith('======'):
                in_changelog = True
                continue
            if in_changelog and line.strip():
                changelog_lines.append(line)
        
        if changelog_lines:
            # Skip the version/date line and Issues Closed section for conciseness
            content = '\n'.join(changelog_lines)
            # Extract just the main content sections
            match = re.search(r'### Additions\s*\n(.*)', content, re.DOTALL)
            if match:
                return match.group(0).strip()
            return content.strip()
        
        return f"Changes for issue #{issue_number}"
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr if e.stderr else "Unknown error"
        return f"Changes for issue #{issue_number}\n\n(No changelog available)"


def generate_release_notes(version):
    """Generate complete release notes for a development version."""
    # Check if there are previous dev releases for this version
    has_previous_dev = check_previous_dev_releases(version)
    base_version = re.sub(r'\.dev\d+$', '', version)
    
    if not has_previous_dev:
        # First dev release for this version - aggregate all changes
        print(f"First dev release for v{base_version} - generating full changelog", file=sys.stderr)
        changelog = get_changelog_for_version(version)
    else:
        # Subsequent dev release - only show changes from current PR
        pr_number = find_pr_number()
        
        if pr_number:
            issue_number = extract_issue_from_pr(pr_number)
            if issue_number:
                print(f"Found PR #{pr_number} for issue #{issue_number}", file=sys.stderr)
                changelog = get_changelog_for_issue(issue_number)
            else:
                print(f"Found PR #{pr_number} but no associated issue", file=sys.stderr)
                changelog = f"Changes in PR #{pr_number}\n\nNo associated issue found."
        else:
            print("No PR detected", file=sys.stderr)
            changelog = f"Development build {version}"
    
    # Generate release notes with installation instructions
    notes = f"""## Development Release

This is an automated development release published to TestPyPI.

### Installation

Install this development version from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ spafw37=={version}
```

Or to upgrade an existing installation:

```bash
pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ spafw37=={version}
```

**Note:** The `--extra-index-url` flag ensures dependencies are installed from the main PyPI repository.

### Changes

{changelog}

---

📦 **Package:** [spafw37 on TestPyPI](https://test.pypi.org/project/spafw37/{version}/)
"""
    
    return notes


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: generate_dev_release_notes.py <version>", file=sys.stderr)
        sys.exit(1)
    
    version = sys.argv[1]
    notes = generate_release_notes(version)
    print(notes)
