"""Tests for file.py module."""

import os
import pytest
from unittest.mock import mock_open, patch, MagicMock

from spafw37 import file as spafw37_file


def test_validate_file_for_reading_nonexistent_file_raises_error():
    """Test that nonexistent files raise FileNotFoundError.
    
    When a file does not exist, validation should raise FileNotFoundError
    to provide early error detection before attempting file operations.
    """
    nonexistent_path = '/tmp/does_not_exist_test_file.txt'
    with pytest.raises(FileNotFoundError, match="File not found:"):
        spafw37_file._validate_file_for_reading(nonexistent_path)


def test_validate_file_for_reading_directory_raises_error(tmp_path):
    """Test that directories are rejected.
    
    When given a directory path, validation should raise ValueError
    indicating the path is not a file.
    """
    directory_path = tmp_path / "test_dir"
    directory_path.mkdir()
    
    with pytest.raises(ValueError, match="Path is not a file"):
        spafw37_file._validate_file_for_reading(str(directory_path))


def test_validate_file_for_reading_unreadable_file_raises_error(tmp_path):
    """Test that unreadable files raise PermissionError.
    
    When a file exists but cannot be read, validation should raise
    PermissionError with appropriate message.
    """
    unreadable_file = tmp_path / "unreadable.txt"
    unreadable_file.write_text("content")
    unreadable_file.chmod(0o000)
    
    try:
        with pytest.raises(PermissionError, match="Permission denied reading file"):
            spafw37_file._validate_file_for_reading(str(unreadable_file))
    finally:
        # Clean up: restore permissions so pytest can delete it
        unreadable_file.chmod(0o644)


def test_validate_file_for_reading_binary_file_raises_error(tmp_path):
    """Test that binary files are rejected.
    
    When a file contains null bytes (binary content), validation should
    raise ValueError indicating the file appears to be binary.
    """
    binary_file = tmp_path / "binary.bin"
    binary_file.write_bytes(b'\x00\x01\x02\x03')
    
    with pytest.raises(ValueError, match="File appears to be binary"):
        spafw37_file._validate_file_for_reading(str(binary_file))


def test_read_file_raw_file_not_found():
    """Test that FileNotFoundError is raised for nonexistent files.
    
    When attempting to read a file that does not exist, the function
    should raise FileNotFoundError with appropriate message.
    """
    with pytest.raises(FileNotFoundError, match="File not found:"):
        spafw37_file._read_file_raw('/tmp/nonexistent_file_xyz.txt')


def test_read_file_raw_permission_denied(tmp_path):
    """Test that PermissionError is raised for unreadable files.
    
    When attempting to read a file without read permissions, the function
    should raise PermissionError with appropriate message.
    """
    unreadable_file = tmp_path / "unreadable.txt"
    unreadable_file.write_text("content")
    unreadable_file.chmod(0o000)
    
    try:
        with pytest.raises(PermissionError, match="Permission denied reading"):
            spafw37_file._read_file_raw(str(unreadable_file))
    finally:
        unreadable_file.chmod(0o644)


def test_read_file_raw_unicode_decode_error(tmp_path):
    """Test that ValueError is raised for files with invalid encoding.
    
    When a file contains invalid UTF-8 sequences, the function should
    raise ValueError indicating invalid text encoding.
    """
    invalid_utf8_file = tmp_path / "invalid.txt"
    # Write invalid UTF-8 sequence (but not binary - no null bytes)
    invalid_utf8_file.write_bytes(b'\xff\xfe')
    
    with pytest.raises(ValueError, match="File contains invalid text encoding"):
        spafw37_file._read_file_raw(str(invalid_utf8_file))
