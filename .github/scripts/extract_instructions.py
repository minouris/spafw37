#!/usr/bin/env python3
"""
Extract sections from instruction files and create context files.

This script processes instruction files in .github/instructions.bak/ and extracts
each level 2 heading section into separate files under .github/context/.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def normalize_filename(text: str) -> str:
    """
    Normalize text into a filename.
    
    Converts to lowercase, replaces spaces with dots, removes special chars.
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with dots
    text = text.replace(" ", ".")
    # Remove colons
    text = text.replace(":", "")
    # Replace forward slashes with hyphens
    text = text.replace("/", "-")
    # Remove parentheses
    text = text.replace("(", "").replace(")", "")
    # Remove other special characters but keep dots and hyphens
    text = re.sub(r'[^a-z0-9.\-]+', '.', text)
    # Remove multiple consecutive dots
    text = re.sub(r'\.+', '.', text)
    # Remove leading/trailing dots
    text = text.strip('.')
    return text


def extract_sections(content: str) -> List[Tuple[str, str, str]]:
    """
    Extract sections from markdown content.
    
    Returns list of (level1_heading, level2_heading, section_content) tuples.
    """
    sections = []
    lines = content.split('\n')
    
    current_h1 = None
    current_h2 = None
    current_content = []
    
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        
        # Check for level 1 heading (must be at start of line)
        if line.startswith('# ') and not line.startswith('## '):
            # Save previous section if exists
            if current_h1 and current_h2 and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    sections.append((current_h1, current_h2, content_text))
            
            current_h1 = line[2:].strip()
            current_h2 = None
            current_content = []
        
        # Check for level 2 heading
        elif line.startswith('## ') and not line.startswith('### '):
            # Save previous section if exists
            if current_h1 and current_h2 and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    sections.append((current_h1, current_h2, content_text))
            
            current_h2 = line[3:].strip()
            current_content = [line]  # Include the heading itself
        
        # Regular content line
        elif current_h2 is not None:
            current_content.append(line)
        
        line_index += 1
    
    # Save final section
    if current_h1 and current_h2 and current_content:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            sections.append((current_h1, current_h2, content_text))
    
    return sections


def process_instruction_file(source_path: Path, domain: str) -> int:
    """
    Process a single instruction file and create context files.
    
    Returns the number of files created.
    """
    print(f"\nProcessing: {source_path.name}")
    print(f"Domain: {domain}")
    
    content = source_path.read_text()
    sections = extract_sections(content)
    
    files_created = 0
    
    for level1_heading, level2_heading, section_content in sections:
        # Normalize filenames
        level1_normalized = normalize_filename(level1_heading)
        level2_normalized = normalize_filename(level2_heading)
        
        # Create target path
        target_dir = Path(f".github/context/{domain}/{level1_normalized}")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / f"{level2_normalized}.md"
        
        # Write content
        target_file.write_text(section_content)
        
        print(f"  ✓ {target_file}")
        files_created += 1
    
    return files_created


def main():
    """Main execution function."""
    # Define instruction files to process
    instruction_files = {
        "general": ".github/instructions.bak/general.instructions.md",
        "python": ".github/instructions.bak/python.instructions.md",
        "python37": ".github/instructions.bak/python37.instructions.md",
        "python-tests": ".github/instructions.bak/python-tests.instructions.md",
        "documentation": ".github/instructions.bak/documentation.instructions.md",
        "planning": ".github/instructions.bak/planning.instructions.md",
        "architecture": ".github/instructions.bak/architecture.instructions.md",
        "issue-workflow": ".github/instructions.bak/issue-workflow.instructions.md",
        "bash.commands": ".github/instructions.bak/bash.commands.instructions.md",
        "mermaid": ".github/instructions.bak/mermaid.instructions.md",
    }
    
    total_files = 0
    
    for domain, filepath in instruction_files.items():
        source_path = Path(filepath)
        
        if not source_path.exists():
            print(f"⚠️  File not found: {filepath}")
            continue
        
        try:
            files_created = process_instruction_file(source_path, domain)
            total_files += files_created
        except Exception as error:
            print(f"❌ Error processing {filepath}: {error}")
    
    print(f"\n{'='*80}")
    print(f"✅ Total files created: {total_files}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
