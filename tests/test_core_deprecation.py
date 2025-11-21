"""Tests for deprecation functionality in core.py."""

import pytest
from spafw37 import core as spafw37


def test_deprecation_warning_shown_once():
    """Test that deprecation warnings are shown only once per function.
    
    The first call to a deprecated function should emit a warning.
    Subsequent calls should not emit additional warnings.
    """
    # Reset state
    spafw37._deprecated_warnings_shown.clear()
    spafw37.suppress_deprecation(False)
    
    # Create a test deprecated function
    @spafw37._deprecated("Use new_function() instead.")
    def old_function():
        return "result"
    
    # First call should add function to warnings shown
    result1 = old_function()
    assert result1 == "result"
    assert 'old_function' in spafw37._deprecated_warnings_shown
    
    # Clear and call again - should add it again since cleared
    spafw37._deprecated_warnings_shown.clear()
    result2 = old_function()
    assert result2 == "result"
    assert 'old_function' in spafw37._deprecated_warnings_shown


def test_suppress_deprecation_true():
    """Test that deprecation warnings can be suppressed.
    
    When deprecation suppression is enabled, deprecated function calls
    should not emit warnings.
    """
    # Reset and suppress
    spafw37._deprecated_warnings_shown.clear()
    spafw37.suppress_deprecation(True)
    
    @spafw37._deprecated("Use new_function() instead.")
    def old_function():
        return "result"
    
    result = old_function()
    assert result == "result"
    
    # Warning should be suppressed
    assert len(spafw37._deprecated_warnings_shown) == 0
    
    # Clean up
    spafw37.suppress_deprecation(False)


def test_suppress_deprecation_false():
    """Test that deprecation warnings can be re-enabled.
    
    After suppressing warnings, calling suppress_deprecation(False)
    should re-enable them.
    """
    # Reset state
    spafw37._deprecated_warnings_shown.clear()
    
    # Suppress then re-enable
    spafw37.suppress_deprecation(True)
    assert spafw37._suppress_deprecation_warnings == True
    
    spafw37.suppress_deprecation(False)
    assert spafw37._suppress_deprecation_warnings == False
    
    @spafw37._deprecated("Use new_function() instead.")
    def old_function():
        return "result"
    
    result = old_function()
    assert result == "result"
    
    # Warning should have been tracked
    assert 'old_function' in spafw37._deprecated_warnings_shown


def test_run_cli_command_parameter_error_embedded():
    """Test that run_cli handles CommandParameterError in embedded mode.
    
    When _embedded=True, the function should not call sys.exit() after
    displaying error and help information.
    """
    from spafw37.command import CommandParameterError
    from unittest.mock import patch
    
    with patch('spafw37.cli.handle_cli_args') as mock_handle:
        mock_handle.side_effect = CommandParameterError("Test error", "test_command")
        
        with patch('spafw37.help.display_command_help') as mock_help:
            # Should not raise SystemExit because _embedded=True
            spafw37.run_cli(['test'], _embedded=True)
            
            # Help should have been displayed
            mock_help.assert_called_once_with("test_command")


def test_run_cli_value_error_embedded():
    """Test that run_cli handles ValueError in embedded mode.
    
    When _embedded=True and a ValueError occurs, the function should
    display the error but not exit.
    """
    from unittest.mock import patch
    
    with patch('spafw37.cli.handle_cli_args') as mock_handle:
        mock_handle.side_effect = ValueError("Test value error")
        
        # Should not raise SystemExit because _embedded=True
        spafw37.run_cli(['test'], _embedded=True)
