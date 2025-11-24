#!/usr/bin/env python3
"""
Generate changelog entry from issue plan CHANGES sections.

This script:
1. Reads current version from setup.cfg (or uses --version arg)
2. Finds all plan files for that version (or specific --issues)
3. Extracts CHANGES sections
4. Combines them into a single changelog entry
5. Updates CHANGELOG.md (or outputs to stdout with --output)

Usage:
  # Generate for current version and update CHANGELOG.md
  generate_changelog.py
  
  # Generate for specific issues (no CHANGELOG.md update)
  generate_changelog.py --issues 26,27,33 --output -
  
  # Generate for specific version
  generate_changelog.py --version 1.2.0 --output changelog_entry.md
"""

import argparse
import re
import sys
from pathlib import Path


def get_current_version(repo_root):
    """Extract version from setup.cfg."""
    setup_cfg = repo_root / "setup.cfg"
    if not setup_cfg.exists():
        print(f"Error: setup.cfg not found at {setup_cfg}", file=sys.stderr)
        sys.exit(1)
    
    content = setup_cfg.read_text()
    match = re.search(r'^version\s*=\s*(.+)$', content, re.MULTILINE)
    if not match:
        print("Error: Could not find version in setup.cfg", file=sys.stderr)
        sys.exit(1)
    
    version = match.group(1).strip()
    # Strip .devN suffix to get target release version
    version = re.sub(r'\.dev\d+$', '', version)
    return version


def find_plan_files_for_version(repo_root, version):
    """Find all plan files targeting the specified version."""
    features_dir = repo_root / "features"
    if not features_dir.exists():
        return []
    
    plan_files = []
    for plan_file in features_dir.glob("issue-*.md"):
        if plan_file.stem in ["ISSUE-PLAN-TEMPLATE", "CHANGES-TEMPLATE"]:
            continue
        
        # Check if plan file targets this version (in filename or content)
        if version in plan_file.stem:
            plan_files.append(plan_file)
        else:
            # Check CHANGES section header for version
            content = plan_file.read_text()
            changes_header_match = re.search(
                rf'^## CHANGES for v{re.escape(version)}',
                content,
                re.MULTILINE
            )
            if changes_header_match:
                plan_files.append(plan_file)
    
    return sorted(plan_files)


def find_plan_files_for_issues(repo_root, issue_numbers):
    """Find plan files for specific issue numbers."""
    features_dir = repo_root / "features"
    if not features_dir.exists():
        return []
    
    plan_files = []
    for issue_num in issue_numbers:
        # Find files matching issue-XX-*.md pattern
        matching_files = list(features_dir.glob(f"issue-{issue_num}-*.md"))
        plan_files.extend(matching_files)
    
    return sorted(plan_files)


def extract_changes_section(plan_file):
    """Extract CHANGES section from a plan file."""
    content = plan_file.read_text()
    
    # Find CHANGES section - match to end of file
    changes_match = re.search(
        r'^## CHANGES for v[\d.]+.*?$\s*\n(.*)',
        content,
        re.MULTILINE | re.DOTALL
    )
    
    if not changes_match:
        return None
    
    changes_content = changes_match.group(1).strip()
    
    # Extract issue number and title from first line
    issue_match = re.search(r'^Issue #(\d+):\s*(.+)$', changes_content, re.MULTILINE)
    if not issue_match:
        return None
    
    issue_num = issue_match.group(1)
    issue_title = issue_match.group(2).strip()
    
    # Extract each section
    sections = {
        'issue_num': issue_num,
        'issue_title': issue_title,
        'issues_closed': [],
        'additions': [],
        'removals': [],
        'changes': [],
        'migration': [],
        'documentation': [],
        'testing': []
    }
    
    # Extract Issues Closed
    issues_match = re.search(
        r'^### Issues Closed\s*\n(.*?)(?=^###|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if issues_match:
        for line in issues_match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                sections['issues_closed'].append(line[1:].strip())
    
    # Extract Additions
    additions_match = re.search(
        r'^### Additions\s*\n(.*?)(?=^###|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if additions_match:
        for line in additions_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and line != "None.":
                if line.startswith('-') or line.startswith('*'):
                    sections['additions'].append(line[1:].strip())
                elif not line.startswith('#'):
                    sections['additions'].append(line)
    
    # Extract Removals
    removals_match = re.search(
        r'^### Removals\s*\n(.*?)(?=^###|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if removals_match:
        for line in removals_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and line != "None.":
                if line.startswith('-') or line.startswith('*'):
                    sections['removals'].append(line[1:].strip())
                elif not line.startswith('#'):
                    sections['removals'].append(line)
    
    # Extract Changes
    changes_match = re.search(
        r'^### Changes\s*\n(.*?)(?=^###|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if changes_match:
        for line in changes_match.group(1).strip().split('\n'):
            line = line.strip()
            if line and line != "None.":
                if line.startswith('-') or line.startswith('*'):
                    sections['changes'].append(line[1:].strip())
                elif not line.startswith('#'):
                    sections['changes'].append(line)
    
    # Extract Migration
    migration_match = re.search(
        r'^### Migration\s*\n(.*?)(?=^###|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if migration_match:
        migration_text = migration_match.group(1).strip()
        if migration_text and "No migration required" not in migration_text:
            for line in migration_text.split('\n'):
                line = line.strip()
                if line:
                    if line.startswith('-') or line.startswith('*'):
                        sections['migration'].append(line[1:].strip())
                    elif not line.startswith('#'):
                        sections['migration'].append(line)
    
    # Extract Documentation
    doc_match = re.search(
        r'^### Documentation\s*\n(.*?)(?=^###|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if doc_match:
        for line in doc_match.group(1).strip().split('\n'):
            line = line.strip()
            if line:
                if line.startswith('-') or line.startswith('*'):
                    sections['documentation'].append(line[1:].strip())
                elif not line.startswith('#'):
                    sections['documentation'].append(line)
    
    # Extract Testing (just keep the whole section)
    testing_match = re.search(
        r'^### Testing\s*\n(.*?)(?=^---|\Z)',
        changes_content,
        re.MULTILINE | re.DOTALL
    )
    if testing_match:
        testing_text = testing_match.group(1).strip()
        sections['testing'] = [testing_text]
    
    return sections


def combine_changes(changes_list, version):
    """Combine multiple CHANGES sections into a single changelog entry."""
    if not changes_list:
        return ""
    
    # Helper to filter out stat lines (e.g., "11 parameter examples changed")
    def is_stat_line(text):
        """Check if a line is a statistics summary line."""
        text_lower = text.lower()
        # Match patterns like "X examples changed", "Y tests pass", etc.
        stat_patterns = [
            'examples changed',
            'example changed',
            'changed to',  # Avoid "changed to param API" etc.
        ]
        # If line starts with a number, it's likely a stat
        stripped = text.strip()
        if stripped and stripped[0].isdigit():
            return any(pattern in text_lower for pattern in stat_patterns)
        return False
    
    # Collect all issues
    all_issues = []
    for changes in changes_list:
        all_issues.append(f"#{changes['issue_num']}: {changes['issue_title']}")
    
    # Build changelog entry
    lines = [
        f"## [{version}] - {import_date()}",
        "",
        "### Issues Closed",
        ""
    ]
    
    for issue in all_issues:
        lines.append(f"- {issue}")
    lines.append("")
    
    # Helper to add section organized by issue
    def add_section_by_issue(section_name, key, empty_msg="None."):
        lines.append(f"### {section_name}")
        lines.append("")
        
        has_content = False
        for changes in changes_list:
            items = changes[key]
            if items:
                has_content = True
                # Add issue header
                lines.append(f"**Issue #{changes['issue_num']}:**")
                lines.append("")
                for item in items:
                    # Skip stat lines for documentation
                    if key == 'documentation' and is_stat_line(item):
                        continue
                    lines.append(f"- {item}")
                lines.append("")
        
        if not has_content:
            lines.append(f"{empty_msg}")
            lines.append("")
    
    # Additions
    add_section_by_issue("Additions", "additions")
    
    # Removals
    add_section_by_issue("Removals", "removals")
    
    # Changes
    add_section_by_issue("Changes", "changes")
    
    # Migration
    add_section_by_issue("Migration", "migration", "No migration required.")
    
    # Documentation (filter stat lines)
    doc_has_content = any(changes['documentation'] for changes in changes_list)
    if doc_has_content:
        add_section_by_issue("Documentation", "documentation")
    
    return "\n".join(lines)


def import_date():
    """Get current date in YYYY-MM-DD format."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def update_changelog(repo_root, new_entry, version):
    """Update CHANGELOG.md with new entry."""
    changelog_file = repo_root / "CHANGELOG.md"
    
    if not changelog_file.exists():
        # Create new changelog
        content = "# Changelog\n\n" + new_entry
    else:
        existing_content = changelog_file.read_text()
        
        # Check if this version already exists
        version_pattern = rf'^## \[{re.escape(version)}\]'
        if re.search(version_pattern, existing_content, re.MULTILINE):
            # Replace existing entry
            new_content = re.sub(
                rf'^## \[{re.escape(version)}\].*?(?=^## \[|\Z)',
                new_entry + "\n",
                existing_content,
                flags=re.MULTILINE | re.DOTALL
            )
            content = new_content
        else:
            # Insert after "# Changelog" header
            if existing_content.startswith("# Changelog"):
                lines = existing_content.split('\n', 2)
                if len(lines) >= 2:
                    content = lines[0] + '\n\n' + new_entry + '\n' + (lines[2] if len(lines) > 2 else '')
                else:
                    content = lines[0] + '\n\n' + new_entry
            else:
                content = "# Changelog\n\n" + new_entry + "\n\n" + existing_content
    
    changelog_file.write_text(content)
    print(f"Updated CHANGELOG.md with version {version}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate changelog from issue plan CHANGES sections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for current version and update CHANGELOG.md
  %(prog)s
  
  # Generate for specific issues (output to stdout)
  %(prog)s --issues 26,27,33 --output -
  
  # Generate for specific version to file
  %(prog)s --version 1.2.0 --output changelog_entry.md
        """
    )
    parser.add_argument(
        '--version',
        help='Target version (default: read from setup.cfg)'
    )
    parser.add_argument(
        '--issues',
        help='Comma-separated issue numbers (e.g., 26,27,33)'
    )
    parser.add_argument(
        '--output',
        help='Output file (- for stdout, default: update CHANGELOG.md)',
        default='CHANGELOG.md'
    )
    
    args = parser.parse_args()
    repo_root = Path(__file__).parent.parent.parent
    
    # Determine version
    if args.version:
        version = args.version
    elif args.issues:
        # When targeting specific issues, use "X.Y.Z" as placeholder
        version = "X.Y.Z"
    else:
        version = get_current_version(repo_root)
        print(f"Current development version: {version}", file=sys.stderr)
    
    # Find plan files
    if args.issues:
        issue_numbers = [int(n.strip()) for n in args.issues.split(',')]
        plan_files = find_plan_files_for_issues(repo_root, issue_numbers)
        print(f"Finding plan files for issues: {issue_numbers}", file=sys.stderr)
    else:
        plan_files = find_plan_files_for_version(repo_root, version)
        print(f"Finding plan files for version: {version}", file=sys.stderr)
    
    if not plan_files:
        if args.issues:
            print(f"No plan files found for issues: {args.issues}", file=sys.stderr)
        else:
            print(f"No plan files found for version {version}", file=sys.stderr)
        print("Skipping changelog generation", file=sys.stderr)
        sys.exit(0)
    
    print(f"Found {len(plan_files)} plan file(s):", file=sys.stderr)
    for pf in plan_files:
        print(f"  - {pf.name}", file=sys.stderr)
    
    # Extract CHANGES sections
    all_changes = []
    for plan_file in plan_files:
        changes = extract_changes_section(plan_file)
        if changes:
            all_changes.append(changes)
            print(f"  ✓ Extracted CHANGES from {plan_file.name}", file=sys.stderr)
        else:
            print(f"  ⚠ No CHANGES section found in {plan_file.name}", file=sys.stderr)
    
    if not all_changes:
        print("No CHANGES sections found in any plan files", file=sys.stderr)
        print("Skipping changelog generation", file=sys.stderr)
        sys.exit(0)
    
    # Combine and generate changelog entry
    changelog_entry = combine_changes(all_changes, version)
    
    # Output
    if args.output == '-':
        # Output to stdout (no separator needed)
        print(changelog_entry)
    elif args.output == 'CHANGELOG.md':
        # Update CHANGELOG.md
        update_changelog(repo_root, changelog_entry, version)
        print("✓ Changelog generation complete", file=sys.stderr)
    else:
        # Write to specified file
        output_file = Path(args.output)
        output_file.write_text(changelog_entry)
        print(f"✓ Wrote changelog to {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
