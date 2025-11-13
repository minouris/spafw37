"""
Nested Cycles Example

Demonstrates how to nest cycles within cycles for multi-dimensional iteration.
This example processes a grid of data using an outer cycle for rows and an
inner cycle for columns.

Key concepts:
- Nested cycle patterns (outer and inner cycles)
- Runtime parameters for cycle state management
- Multi-level iteration coordination
- Maximum nesting depth (5 levels)
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_CYCLE,
    COMMAND_INVOCABLE,
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
    PARAM_TYPE,
    PARAM_TYPE_NUMBER,
    PARAM_RUNTIME_ONLY,
)


def setup():
    """Configure the application with nested cycles demonstration."""
    
    # Runtime parameters for outer cycle (rows)
    row_params = [
        {
            PARAM_NAME: 'rows',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_RUNTIME_ONLY: True,
        },
        {
            PARAM_NAME: 'current-row',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_RUNTIME_ONLY: True,
        },
    ]
    
    # Runtime parameters for inner cycle (columns)
    col_params = [
        {
            PARAM_NAME: 'cols',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_RUNTIME_ONLY: True,
        },
        {
            PARAM_NAME: 'current-col',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_RUNTIME_ONLY: True,
        },
    ]
    
    spafw37.add_params(row_params)
    spafw37.add_params(col_params)
    
    # Outer cycle functions (rows)
    def init_rows():
        """Initialize the outer cycle with number of rows."""
        rows = 3
        spafw37.set_config_value('rows', rows)
        spafw37.set_config_value('current-row', 0)
        print(f"Processing {rows} rows...")
    
    def has_more_rows():
        """Check if there are more rows to process."""
        current_row = spafw37.get_config_int('current-row')
        total_rows = spafw37.get_config_int('rows')
        return current_row < total_rows
    
    def finalize_rows():
        """Complete the outer cycle."""
        total_rows = spafw37.get_config_int('rows')
        print(f"\nCompleted processing {total_rows} rows")
    
    # Inner cycle functions (columns)
    def init_cols():
        """Initialize the inner cycle with number of columns."""
        cols = 4
        current_row = spafw37.get_config_int('current-row')
        spafw37.set_config_value('cols', cols)
        spafw37.set_config_value('current-col', 0)
        print(f"  Row {current_row}: Processing {cols} columns...")
    
    def has_more_cols():
        """Check if there are more columns to process."""
        current_col = spafw37.get_config_int('current-col')
        total_cols = spafw37.get_config_int('cols')
        return current_col < total_cols
    
    def finalize_cols():
        """Complete the inner cycle and advance to next row."""
        current_row = spafw37.get_config_int('current-row')
        total_cols = spafw37.get_config_int('cols')
        print(f"  Row {current_row}: Completed {total_cols} columns")
        
        # Advance to next row
        spafw37.set_config_value('current-row', current_row + 1)
    
    # Command: Process a single cell
    def process_cell():
        """Process a single cell in the grid."""
        row = spafw37.get_config_int('current-row')
        col = spafw37.get_config_int('current-col')
        
        # Simulate processing
        value = (row * 10) + col
        print(f"    Cell [{row},{col}] = {value}")
        
        # Advance to next column
        spafw37.set_config_value('current-col', col + 1)
    
    # Command: Process a row (placeholder action for cycle)
    def process_row():
        """Process a row - the cycle handles the actual work."""
        pass
    
    # Command: Process the grid (placeholder action for cycle)
    def process_grid():
        """Process the grid - the cycle handles the actual work."""
        pass
    
    # Define commands
    commands = [
        # Inner cycle command - process a column
        {
            COMMAND_NAME: 'process-cell',
            COMMAND_DESCRIPTION: 'Process a single cell',
            COMMAND_ACTION: process_cell,
            COMMAND_INVOCABLE: False,  # Only callable from cycle
        },
        # Middle cycle command - process a row (contains inner cycle)
        {
            COMMAND_NAME: 'process-row',
            COMMAND_DESCRIPTION: 'Process a single row',
            COMMAND_ACTION: process_row,
            COMMAND_INVOCABLE: False,  # Only callable from outer cycle
            COMMAND_CYCLE: {
                CYCLE_NAME: 'column-cycle',
                CYCLE_INIT: init_cols,
                CYCLE_LOOP: has_more_cols,
                CYCLE_END: finalize_cols,
                CYCLE_COMMANDS: ['process-cell'],
            }
        },
        # Outer cycle command - process the entire grid
        {
            COMMAND_NAME: 'process-grid',
            COMMAND_DESCRIPTION: 'Process a grid of data using nested cycles',
            COMMAND_ACTION: process_grid,
            COMMAND_CYCLE: {
                CYCLE_NAME: 'row-cycle',
                CYCLE_INIT: init_rows,
                CYCLE_LOOP: has_more_rows,
                CYCLE_END: finalize_rows,
                CYCLE_COMMANDS: ['process-row'],
            }
        },
    ]
    
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.run_cli()
