#!/usr/bin/env python3
"""
Version increment script for setup.cfg

Handles:
- Incrementing dev version (.dev0 -> .dev1 -> .dev2)
- Resetting dev counter when base version changes
- Updating setup.cfg in place
"""
import re
import sys
from pathlib import Path


def read_version(setup_cfg_path):
    """Read current version from setup.cfg."""
    content = setup_cfg_path.read_text()
    match = re.search(r'^version = (.+)$', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in setup.cfg")
    return match.group(1).strip()


def parse_version(version_string):
    """Parse version string into components.
    
    Returns:
        tuple: (base_version, dev_number) e.g., ("1.0.0", 0)
    """
    # Match pattern: X.Y.Z.devN
    match = re.match(r'^(\d+\.\d+\.\d+)\.dev(\d+)$', version_string)
    if not match:
        raise ValueError(f"Invalid version format: {version_string}")
    
    base_version = match.group(1)
    dev_number = int(match.group(2))
    return base_version, dev_number


def increment_version(current_version, new_base_version=None):
    """Increment version number.
    
    Args:
        current_version: Current version string (e.g., "1.0.0.dev0")
        new_base_version: Optional new base version. If provided and different
                         from current base, dev counter resets to 0.
    
    Returns:
        str: New version string
    """
    base_version, dev_number = parse_version(current_version)
    
    if new_base_version and new_base_version != base_version:
        # Base version changed, reset dev counter
        return f"{new_base_version}.dev0"
    else:
        # Same base version, increment dev counter
        new_dev_number = dev_number + 1
        return f"{base_version}.dev{new_dev_number}"


def update_setup_cfg(setup_cfg_path, new_version):
    """Update version in setup.cfg."""
    content = setup_cfg_path.read_text()
    new_content = re.sub(
        r'^version = .+$',
        f'version = {new_version}',
        content,
        flags=re.MULTILINE
    )
    setup_cfg_path.write_text(new_content)


def main():
    """Main entry point."""
    # Find setup.cfg (assume script is in .github/scripts/)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    setup_cfg = repo_root / 'setup.cfg'
    
    if not setup_cfg.exists():
        print(f"Error: setup.cfg not found at {setup_cfg}", file=sys.stderr)
        sys.exit(1)
    
    # Read current version
    current_version = read_version(setup_cfg)
    print(f"Current version: {current_version}")
    
    # Check for optional new base version argument
    new_base = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Increment version
    new_version = increment_version(current_version, new_base)
    print(f"New version: {new_version}")
    
    # Update setup.cfg
    update_setup_cfg(setup_cfg, new_version)
    print(f"✓ Updated {setup_cfg}")
    
    # Output for GitHub Actions
    print(f"new_version={new_version}")


if __name__ == '__main__':
    main()
