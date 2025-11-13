"""Basic Output Example - Using spafw37.output() for application output.

This example shows:
- Normal output with spafw37.output()
- Verbose-only output
- Silent mode suppression
- Checking verbose/silent status
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

def demo_output():
    """Demonstrate different output modes."""
    # Always output (unless --silent is used)
    spafw37.output("=== Output Demo ===")
    spafw37.output()
    
    # Normal output
    spafw37.output("This is normal application output")
    spafw37.output("It appears in normal mode and verbose mode")
    spafw37.output("But is suppressed in silent mode (--silent)")
    spafw37.output()
    
    # Verbose-only output
    spafw37.output("Verbose output:", verbose=True)
    spafw37.output("  - Only appears with --verbose flag", verbose=True)
    spafw37.output("  - Useful for detailed diagnostic info", verbose=True)
    spafw37.output("  - Suppressed in normal and silent modes", verbose=True)
    spafw37.output()
    
    # Conditional output based on mode
    if spafw37.is_verbose():
        spafw37.output("Verbose mode detected!")
        spafw37.output("  Generating detailed report...")
        spafw37.output("  Processing statistics: 100 items")
        spafw37.output()
    
    if spafw37.is_silent():
        # This won't actually output anything because silent mode
        # suppresses all output, but you could do non-output work here
        pass
    else:
        spafw37.output("Not in silent mode - showing results")
    
    spafw37.output()
    spafw37.output("=== Demo Complete ===")


def process_data():
    """Simulate data processing with progress output."""
    spafw37.output("Starting data processing...")
    
    # Simulate processing multiple items
    items = ["file1.txt", "file2.txt", "file3.txt"]
    
    for index, item in enumerate(items, 1):
        # Normal progress output
        spafw37.output(f"Processing {index}/{len(items)}: {item}")
        
        # Verbose details
        spafw37.output(f"  Size: 1024 bytes", verbose=True)
        spafw37.output(f"  Hash: abc123def456", verbose=True)
    
    spafw37.output()
    spafw37.output("Processing complete!")
    
    # Final statistics - only in verbose mode
    if spafw37.is_verbose():
        spafw37.output()
        spafw37.output("Statistics:")
        spafw37.output(f"  Total items: {len(items)}")
        spafw37.output(f"  Success: {len(items)}")
        spafw37.output(f"  Failed: 0")


# Define commands
commands = [
    {
        COMMAND_NAME: 'demo',
        COMMAND_DESCRIPTION: 'Demonstrate output modes',
        COMMAND_ACTION: demo_output,
    },
    {
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Simulate data processing with output',
        COMMAND_ACTION: process_data,
    },
]

if __name__ == '__main__':
    spafw37.add_commands(commands)
    spafw37.output("Basic Output Example")
    spafw37.output("=" * 50)
    spafw37.output()
    spafw37.output("Try these commands:")
    spafw37.output("  python output_basic.py demo          # Normal output")
    spafw37.output("  python output_basic.py demo --verbose  # With details")
    spafw37.output("  python output_basic.py demo --silent   # Suppressed")
    spafw37.output()
    spafw37.output("  python output_basic.py process")
    spafw37.output("  python output_basic.py process --verbose")
    spafw37.output()
    spafw37.run_cli()
