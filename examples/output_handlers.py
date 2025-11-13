"""Advanced Output Handlers Example - Custom output routing.

This example shows:
- Default handler (console output)
- File handler (write to file)
- Dual handler (console + file)
- Timestamped handler (with timestamps)
- Testing handler (capture output)
"""

import os
import datetime
from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Global state for testing handler
captured_output = []


def default_handler_demo():
    """Demonstrate the default console handler."""
    spafw37.output("=== Default Handler Demo ===")
    spafw37.output("This uses the built-in print() function")
    spafw37.output("Output appears on console")
    spafw37.output()


def file_handler_demo():
    """Demonstrate writing output to a file."""
    output_file = 'output.txt'
    
    def file_handler(message):
        """Write output to file."""
        with open(output_file, 'a') as file_handle:
            file_handle.write(message + '\n')
    
    # Set the file handler
    spafw37.set_output_handler(file_handler)
    
    spafw37.output("=== File Handler Demo ===")
    spafw37.output("This output is being written to output.txt")
    spafw37.output("Check the file to see the results!")
    spafw37.output()
    spafw37.output(f"File location: {os.path.abspath(output_file)}")
    
    # Reset to default
    spafw37.set_output_handler()
    
    # This will appear on console
    print(f"\nOutput was written to: {os.path.abspath(output_file)}")
    print("Check the file to see the captured output\n")


def dual_handler_demo():
    """Demonstrate output to both console and file."""
    output_file = 'dual_output.txt'
    
    def dual_handler(message):
        """Output to both console and file."""
        # Console output
        print(message)
        
        # File output
        with open(output_file, 'a') as file_handle:
            file_handle.write(message + '\n')
    
    # Set the dual handler
    spafw37.set_output_handler(dual_handler)
    
    spafw37.output("=== Dual Handler Demo ===")
    spafw37.output("This message appears on BOTH:")
    spafw37.output("  1. Console (you see it here)")
    spafw37.output("  2. File (check dual_output.txt)")
    spafw37.output()
    spafw37.output("Useful for:")
    spafw37.output("  - Keeping permanent logs")
    spafw37.output("  - Debugging issues")
    spafw37.output("  - Audit trails")
    
    # Reset to default
    spafw37.set_output_handler()
    
    print(f"\nDual output saved to: {os.path.abspath(output_file)}\n")


def timestamped_handler_demo():
    """Demonstrate output with timestamps."""
    output_file = 'timestamped_output.txt'
    
    def timestamped_handler(message):
        """Add timestamp to each message."""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamped_message = f"[{timestamp}] {message}"
        
        # Output to console
        print(timestamped_message)
        
        # Also save to file
        with open(output_file, 'a') as file_handle:
            file_handle.write(timestamped_message + '\n')
    
    # Set the timestamped handler
    spafw37.set_output_handler(timestamped_handler)
    
    spafw37.output("=== Timestamped Handler Demo ===")
    spafw37.output("Each message is prefixed with a timestamp")
    spafw37.output()
    spafw37.output("Processing task 1...")
    spafw37.output("Processing task 2...")
    spafw37.output("Processing task 3...")
    spafw37.output()
    spafw37.output("All tasks complete!")
    
    # Reset to default
    spafw37.set_output_handler()
    
    print(f"\nTimestamped output saved to: {os.path.abspath(output_file)}\n")


def testing_handler_demo():
    """Demonstrate per-call output handler specification."""
    global captured_output
    
    print("=== Per-Call Handler Demo ===")
    print()
    print("Method 1: Global handler (affects all output calls)")
    print("-" * 50)
    
    captured_output = []  # Reset
    
    def capture_handler(message):
        """Capture output to a list."""
        captured_output.append(message)
    
    # Set the capture handler globally
    spafw37.set_output_handler(capture_handler)
    
    # Generate some output (captured, not displayed)
    spafw37.output("Message 1")
    spafw37.output("Message 2")
    spafw37.output("Message 3")
    
    # Reset to default
    spafw37.set_output_handler()
    
    # Show what was captured
    print(f"Captured {len(captured_output)} messages:")
    for index, message in enumerate(captured_output, 1):
        print(f"  {index}. {message}")
    print()
    
    print("Method 2: Per-call handler (route specific calls)")
    print("-" * 50)
    
    # Per-call handlers allow routing different messages to different destinations
    special_log = []
    
    spafw37.output("This uses default handler (appears on console)")
    spafw37.output("This is routed elsewhere", output_handler=special_log.append)
    spafw37.output("This also uses default handler (appears on console)")
    spafw37.output("This is also routed elsewhere", output_handler=special_log.append)
    
    print(f"\nSpecial log captured {len(special_log)} messages:")
    for index, message in enumerate(special_log, 1):
        print(f"  {index}. {message}")
    print()
    
    print("Useful for:")
    print("  - Routing different message types to different destinations")
    print("  - Selective file logging")
    print("  - Per-call output customization")
    print("  - Mixed output strategies in single command")
    print()


def comprehensive_demo():
    """Run all handler demos in sequence."""
    spafw37.output("=== Comprehensive Output Handler Demo ===")
    spafw37.output()
    
    # Clean up any existing output files
    for filename in ['output.txt', 'dual_output.txt', 'timestamped_output.txt']:
        if os.path.exists(filename):
            os.remove(filename)
    
    spafw37.output("Running demos...")
    spafw37.output()
    
    # Run each demo
    default_handler_demo()
    spafw37.output()
    
    file_handler_demo()
    
    dual_handler_demo()
    
    timestamped_handler_demo()
    
    testing_handler_demo()
    
    spafw37.output("=== All Demos Complete ===")
    spafw37.output()
    spafw37.output("Check these files:")
    spafw37.output("  - output.txt (file handler demo)")
    spafw37.output("  - dual_output.txt (dual handler demo)")
    spafw37.output("  - timestamped_output.txt (timestamped handler demo)")


# Define commands
commands = [
    {
        COMMAND_NAME: 'default',
        COMMAND_DESCRIPTION: 'Default console handler demo',
        COMMAND_ACTION: default_handler_demo,
    },
    {
        COMMAND_NAME: 'file',
        COMMAND_DESCRIPTION: 'File output handler demo',
        COMMAND_ACTION: file_handler_demo,
    },
    {
        COMMAND_NAME: 'dual',
        COMMAND_DESCRIPTION: 'Dual output (console + file) demo',
        COMMAND_ACTION: dual_handler_demo,
    },
    {
        COMMAND_NAME: 'timestamp',
        COMMAND_DESCRIPTION: 'Timestamped output handler demo',
        COMMAND_ACTION: timestamped_handler_demo,
    },
    {
        COMMAND_NAME: 'testing',
        COMMAND_DESCRIPTION: 'Per-call handler specification demo',
        COMMAND_ACTION: testing_handler_demo,
    },
    {
        COMMAND_NAME: 'all',
        COMMAND_DESCRIPTION: 'Run all handler demos',
        COMMAND_ACTION: comprehensive_demo,
    },
]

if __name__ == '__main__':
    spafw37.add_commands(commands)
    spafw37.output("Advanced Output Handlers Example")
    spafw37.output("=" * 60)
    spafw37.output()
    spafw37.output("Try these commands:")
    spafw37.output("  python output_handlers.py default     # Console output")
    spafw37.output("  python output_handlers.py file        # Write to file")
    spafw37.output("  python output_handlers.py dual        # Console + file")
    spafw37.output("  python output_handlers.py timestamp   # With timestamps")
    spafw37.output("  python output_handlers.py testing     # Per-call handlers")
    spafw37.output("  python output_handlers.py all         # Run all demos")
    spafw37.output()
    spafw37.run_cli()
