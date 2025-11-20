"""File I/O utilities for spafw37 framework.

This module provides file validation and reading utilities used by
parameter file inputs, configuration file loading, and other file operations.
No domain logic - pure I/O helpers only.
"""

import os


def _validate_file_for_reading(file_path):
    """Validate that a file exists, is readable, and is not binary.
    
    This helper function consolidates file validation logic used across
    parameter file inputs, configuration file loading, and other file
    operations. It expands user paths (~) and performs validation.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Expanded absolute file path
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file cannot be read
        ValueError: If file appears to be binary or path is not a file
    """
    expanded_path = os.path.expanduser(file_path)
    
    # Only perform filesystem checks if path actually exists
    # This allows mocked opens in tests to work naturally
    if os.path.exists(expanded_path):
        # Check if it's a file (not a directory)
        if not os.path.isfile(expanded_path):
            raise ValueError(f"Path is not a file: {expanded_path}")
        
        # Check if file is readable
        if not os.access(expanded_path, os.R_OK):
            raise PermissionError(f"Permission denied reading file: {expanded_path}")
        
        # Check if file appears to be binary by reading first few bytes
        try:
            with open(expanded_path, 'rb') as file_handle:
                initial_bytes = file_handle.read(8192)  # Read first 8KB
                # Check for null bytes which indicate binary content
                # Handle case where mock_open returns string instead of bytes
                if isinstance(initial_bytes, bytes) and b'\x00' in initial_bytes:
                    raise ValueError(f"File appears to be binary: {expanded_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {expanded_path}")
        except (IOError, OSError, UnicodeDecodeError) as io_error:
            # Let the actual open() in the calling code handle these
            # UnicodeDecodeError should propagate naturally from the actual read
            pass
    
    return expanded_path


def _read_file_raw(path):
    """Read a file and return its raw contents as a string.

    This helper validates the file and returns its contents.
    Raises clear exceptions on common IO errors.
    
    Args:
        path: File path (supports ~ expansion and @ prefix)
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file isn't readable
        ValueError: If file is binary
    """
    # Strip @ prefix if present (used for CLI @file syntax)
    clean_path = path[1:] if path.startswith('@') else path
    validated_path = _validate_file_for_reading(clean_path)
    try:
        with open(validated_path, 'r') as file_handle:
            return file_handle.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Parameter file not found: {validated_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied reading parameter file: {validated_path}")
    except UnicodeDecodeError:
        raise ValueError(f"File contains invalid text encoding: {validated_path}")
