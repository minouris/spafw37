#!/usr/bin/env python3
"""Generate development release notes for GitHub releases."""

import json
import re
import subprocess
import sys
from pathlib import Path


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
        # Filter out empty strings and the current version's tag
        current_tag = f"v{version}"
        matching_tags = [t for t in tags if t.strip() and t != current_tag]
        return len(matching_tags) > 0
    except subprocess.CalledProcessError:
        return False


def get_previous_dev_tag(version):
    """Get the most recent dev tag for the same base version, excluding current version."""
    base_version = re.sub(r'\.dev\d+$', '', version)
    current_tag = f"v{version}"
    pattern = f"v{base_version}.dev"
    
    try:
        result = subprocess.run(
            ['git', 'tag', '-l', f'{pattern}*', '--sort=-version:refname'],
            capture_output=True,
            text=True,
            check=True
        )
        tags = [t.strip() for t in result.stdout.strip().split('\n') if t.strip()]
        # Filter out the current tag and get the most recent previous one
        previous_tags = [t for t in tags if t != current_tag]
        if previous_tags:
            return previous_tags[0]
    except subprocess.CalledProcessError:
        pass
    
    return None


def find_plan_files_since_tag(tag):
    """Find plan files that were merged since the given tag."""
    try:
        # Get list of files changed since the tag
        result = subprocess.run(
            ['git', 'diff', '--name-only', f'{tag}...HEAD', 'features/'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        # Filter for plan files (not templates)
        plan_files = [f for f in files if f.strip() and f.endswith('.md') 
                     and 'TEMPLATE' not in f.upper()]
        return plan_files
    except subprocess.CalledProcessError:
        return []


def get_changelog_from_plan_files(plan_files, version):
    """Extract CHANGES sections from plan files."""
    base_version = re.sub(r'\.dev\d+$', '', version)
    changes = []
    
    for plan_file in plan_files:
        try:
            with open(plan_file, 'r') as f:
                content = f.read()
            
            # Look for CHANGES section matching this version
            pattern = rf'## CHANGES.*?v{re.escape(base_version)}.*?\n(.*?)(?=\n##|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                change_content = match.group(1).strip()
                if change_content:
                    changes.append(change_content)
        except (FileNotFoundError, IOError):
            continue
    
    if changes:
        return '\n\n'.join(changes)
    return None


def get_full_changelog(version):
    """Get full changelog from CHANGELOG.md for this version."""
    base_version = re.sub(r'\.dev\d+$', '', version)
    
    try:
        with open('CHANGELOG.md', 'r') as f:
            content = f.read()
        
        # Find the section for this version
        pattern = rf'## \[{re.escape(base_version)}\].*?\n(.*?)(?=\n## \[|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            changelog_content = match.group(1).strip()
            # Extract just the Changes section (skip metadata)
            changes_match = re.search(r'### (Issues Closed|Additions|Changes).*', 
                                     changelog_content, re.DOTALL)
            if changes_match:
                return changes_match.group(0).strip()
            return changelog_content
        
        return None
    except (FileNotFoundError, IOError):
        return None


def get_changelog_for_version(version):
    """Get appropriate changelog content based on whether this is first dev or subsequent."""
    base_version = re.sub(r'\.dev\d+$', '', version)
    has_previous_dev = check_previous_dev_releases(version)
    
    if not has_previous_dev:
        # First dev release - get full changelog from CHANGELOG.md
        print(f"First dev release for v{base_version} - using full changelog", file=sys.stderr)
        changelog = get_full_changelog(version)
        if changelog:
            return changelog
        return f"Development version {version}"
    else:
        # Subsequent dev release - get changes from plan files merged since last dev tag
        previous_tag = get_previous_dev_tag(version)
        print(f"Subsequent dev release - checking changes since {previous_tag}", file=sys.stderr)
        
        plan_files = find_plan_files_since_tag(previous_tag)
        if plan_files:
            print(f"Found plan files: {', '.join(plan_files)}", file=sys.stderr)
            changelog = get_changelog_from_plan_files(plan_files, version)
            if changelog:
                return changelog
        
        # Fallback if no plan files found
        print("No plan files found since last release", file=sys.stderr)
        return f"Development build {version}\n\n(No changes documented)"


def get_changelog_for_issue(version):
    """Legacy function name - redirects to get_changelog_for_version."""
    return get_changelog_for_version(version)


def generate_release_notes(version):
    """Generate complete release notes for a development version."""
    changelog = get_changelog_for_version(version)
    
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
