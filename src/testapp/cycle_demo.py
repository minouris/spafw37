"""
Cycle Demo Application

Demonstrates cycle functionality including:
- Basic cycle with init/loop/end functions
- Nested cycles
- Cycles in command sequences with dependencies
- Different cycle configuration styles
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_CYCLE,
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_GOES_AFTER,
)
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE_NUMBER,
)


# Shared state for demos
demo_state = {
    'files': [],
    'current_file_index': 0,
    'processed_count': 0,
    'batch_number': 0,
    'items_per_batch': 0,
    'current_batch_index': 0,
}


def _setup_demo():
    """Set up initial demo state."""
    print("\n" + "=" * 60)
    print("CYCLE DEMO APPLICATION")
    print("=" * 60)
    demo_state['files'] = []
    demo_state['current_file_index'] = 0
    demo_state['processed_count'] = 0


def _show_demo_results():
    """Display demo results."""
    print("\n" + "-" * 60)
    print("Demo Results:")
    print("  Files processed: {}".format(demo_state['processed_count']))
    print("=" * 60 + "\n")


# Example 1: Basic Cycle - Process Files
def _init_file_processing():
    """Initialize file processing cycle."""
    file_count = spafw37.get_config_value('file-count') or 5
    if isinstance(file_count, str):
        file_count = int(file_count)
    demo_state['files'] = ['file{}.txt'.format(i) for i in range(1, file_count + 1)]
    demo_state['current_file_index'] = 0
    print("\nInitializing file processing...")
    print("  Found {} files to process".format(len(demo_state['files'])))


def _has_more_files():
    """Check if there are more files to process."""
    return demo_state['current_file_index'] < len(demo_state['files'])


def _finalize_file_processing():
    """Finalize file processing cycle."""
    print("\nFile processing complete!")
    print("  Total files processed: {}".format(demo_state['processed_count']))


def _validate_file():
    """Validate current file."""
    current_file = demo_state['files'][demo_state['current_file_index']]
    print("  [1/3] Validating {}...".format(current_file))


def _transform_file():
    """Transform current file."""
    current_file = demo_state['files'][demo_state['current_file_index']]
    print("  [2/3] Transforming {}...".format(current_file))


def _save_file():
    """Save current file."""
    current_file = demo_state['files'][demo_state['current_file_index']]
    print("  [3/3] Saving {}...".format(current_file))
    demo_state['current_file_index'] += 1
    demo_state['processed_count'] += 1


# Example 2: Nested Cycles - Batch Processing
def _init_batch_processing():
    """Initialize batch processing."""
    demo_state['batch_number'] = 0
    demo_state['items_per_batch'] = 3
    print("\nInitializing batch processing...")


def _has_more_batches():
    """Check if there are more batches to process."""
    demo_state['batch_number'] += 1
    return demo_state['batch_number'] <= 2


def _finalize_batch_processing():
    """Finalize batch processing."""
    print("\nBatch processing complete!")
    print("  Total batches: {}".format(demo_state['batch_number']))


def _prepare_batch():
    """Prepare current batch."""
    print("\n--- Batch {} ---".format(demo_state['batch_number']))
    demo_state['current_batch_index'] = 0


def _init_item_processing():
    """Initialize item processing within batch."""
    print("  Processing items in batch {}...".format(demo_state['batch_number']))


def _has_more_items():
    """Check if there are more items in current batch."""
    return demo_state['current_batch_index'] < demo_state['items_per_batch']


def _finalize_item_processing():
    """Finalize item processing within batch."""
    print("  Batch {} complete: {} items processed".format(
        demo_state['batch_number'],
        demo_state['items_per_batch']
    ))


def _process_item():
    """Process single item in batch."""
    demo_state['current_batch_index'] += 1
    print("    Processing item {}".format(demo_state['current_batch_index']))


# Example 3: Cycle in Sequence with Dependencies
def _prepare_workspace():
    """Prepare workspace before processing."""
    print("\nPreparing workspace...")
    print("  Creating temporary directories")
    print("  Loading configuration")


def _cleanup_workspace():
    """Clean up workspace after processing."""
    print("\nCleaning up workspace...")
    print("  Removing temporary files")
    print("  Saving results")


# Define parameters
params = [
    {
        PARAM_NAME: 'file-count',
        PARAM_DESCRIPTION: 'Number of files to process',
        PARAM_ALIASES: ['--files', '-f'],
        PARAM_TYPE_NUMBER: True,
    }
]

# Define commands for basic file processing cycle
file_processing_commands = [
    {
        COMMAND_NAME: 'validate-file',
        COMMAND_DESCRIPTION: 'Validate file format and contents',
        COMMAND_ACTION: _validate_file,
    },
    {
        COMMAND_NAME: 'transform-file',
        COMMAND_DESCRIPTION: 'Transform file data',
        COMMAND_ACTION: _transform_file,
        COMMAND_GOES_AFTER: ['validate-file'],
    },
    {
        COMMAND_NAME: 'save-file',
        COMMAND_DESCRIPTION: 'Save processed file',
        COMMAND_ACTION: _save_file,
        COMMAND_GOES_AFTER: ['transform-file'],
    }
]

# Define commands for nested batch processing
item_processing_commands = [
    {
        COMMAND_NAME: 'process-item',
        COMMAND_DESCRIPTION: 'Process a single item',
        COMMAND_ACTION: _process_item,
    }
]

batch_commands = [
    {
        COMMAND_NAME: 'prepare-batch',
        COMMAND_DESCRIPTION: 'Prepare batch for processing',
        COMMAND_ACTION: _prepare_batch,
    },
    {
        COMMAND_NAME: 'process-items',
        COMMAND_DESCRIPTION: 'Process all items in batch',
        COMMAND_ACTION: lambda: None,  # Action is optional with cycle
        COMMAND_GOES_AFTER: ['prepare-batch'],
        COMMAND_CYCLE: {
            CYCLE_NAME: 'item-processing-cycle',
            CYCLE_INIT: _init_item_processing,
            CYCLE_LOOP: _has_more_items,
            CYCLE_END: _finalize_item_processing,
            CYCLE_COMMANDS: item_processing_commands,
        }
    }
]

# Define main commands with cycles
commands = [
    {
        COMMAND_NAME: 'setup',
        COMMAND_DESCRIPTION: 'Set up demo environment',
        COMMAND_ACTION: _setup_demo,
    },
    {
        COMMAND_NAME: 'process-files',
        COMMAND_DESCRIPTION: 'Process multiple files in a cycle',
        COMMAND_ACTION: lambda: None,  # Optional - cycle does the work
        COMMAND_REQUIRED_PARAMS: ['file-count'],
        COMMAND_GOES_AFTER: ['setup'],
        COMMAND_CYCLE: {
            CYCLE_NAME: 'file-processing-cycle',
            CYCLE_INIT: _init_file_processing,
            CYCLE_LOOP: _has_more_files,
            CYCLE_END: _finalize_file_processing,
            CYCLE_COMMANDS: file_processing_commands,
        }
    },
    {
        COMMAND_NAME: 'prepare-workspace',
        COMMAND_DESCRIPTION: 'Prepare workspace for batch processing',
        COMMAND_ACTION: _prepare_workspace,
        COMMAND_GOES_AFTER: ['setup'],
    },
    {
        COMMAND_NAME: 'process-batches',
        COMMAND_DESCRIPTION: 'Process multiple batches with nested cycles',
        COMMAND_ACTION: lambda: None,
        COMMAND_GOES_AFTER: ['prepare-workspace'],
        COMMAND_CYCLE: {
            CYCLE_NAME: 'batch-processing-cycle',
            CYCLE_INIT: _init_batch_processing,
            CYCLE_LOOP: _has_more_batches,
            CYCLE_END: _finalize_batch_processing,
            CYCLE_COMMANDS: batch_commands,
        }
    },
    {
        COMMAND_NAME: 'cleanup-workspace',
        COMMAND_DESCRIPTION: 'Clean up workspace after processing',
        COMMAND_ACTION: _cleanup_workspace,
        COMMAND_GOES_AFTER: ['process-batches'],
    },
    {
        COMMAND_NAME: 'show-results',
        COMMAND_DESCRIPTION: 'Display demo results',
        COMMAND_ACTION: _show_demo_results,
        COMMAND_GOES_AFTER: ['process-files', 'cleanup-workspace'],
    }
]


def main():
    """Run the cycle demo application."""
    # Register parameters and commands
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    
    # Run the CLI
    spafw37.run_cli()


if __name__ == '__main__':
    main()
