import pytest
from spafw37 import help, param, command, config_func as config, cycle
import spafw37.config
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_HELP,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_ACTION,
    COMMAND_CYCLE,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_GROUP,
    PARAM_CONFIG_NAME,
)
from io import StringIO
import sys


def setup_function():
    """Reset module state between tests."""
    param._param_aliases.clear()
    param._params.clear()
    spafw37.config._config.clear()
    config._persistent_config.clear()
    command._commands.clear()
    command._finished_commands.clear()
    command._command_queue.clear()
    command._phases.clear()
    command._phases_completed.clear()
    # Initialize default phase
    from spafw37.constants.phase import PHASE_DEFAULT
    command._phases[PHASE_DEFAULT] = []
    command._phase_order = [PHASE_DEFAULT]


def test_display_all_help_with_commands(capsys):
    """Test display_all_help shows commands."""
    setup_function()
    
    def test_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "test-cmd",
        COMMAND_DESCRIPTION: "A test command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    help.display_all_help()
    
    captured = capsys.readouterr()
    assert "Available Commands:" in captured.out
    assert "test-cmd" in captured.out
    assert "A test command" in captured.out


def test_display_all_help_with_params(capsys):
    """Test display_all_help shows parameters."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: "test-param",
        PARAM_DESCRIPTION: "A test parameter",
        PARAM_ALIASES: ["--test", "-t"]
    })
    
    help.display_all_help()
    
    captured = capsys.readouterr()
    assert "Available Parameters:" in captured.out
    assert "test-param" in captured.out
    assert "A test parameter" in captured.out
    assert "--test, -t" in captured.out


def test_display_all_help_filters_command_params(capsys):
    """Test that parameters used by commands are not shown in general params."""
    setup_function()
    
    def test_action():
        pass
    
    param.add_param({
        PARAM_NAME: "cmd-param",
        PARAM_DESCRIPTION: "Command parameter",
        PARAM_ALIASES: ["--cmd-param"],
        PARAM_CONFIG_NAME: "cmd-param"
    })
    
    param.add_param({
        PARAM_NAME: "general-param",
        PARAM_DESCRIPTION: "General parameter",
        PARAM_ALIASES: ["--gen"],
        PARAM_CONFIG_NAME: "general-param"
    })
    
    command.add_command({
        COMMAND_NAME: "test-cmd",
        COMMAND_DESCRIPTION: "Test command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: ["cmd-param"]
    })
    
    help.display_all_help()
    
    captured = capsys.readouterr()
    # cmd-param should not appear in parameters section
    lines = captured.out.split('\n')
    param_section_started = False
    for line in lines:
        if "Available Parameters:" in line:
            param_section_started = True
        if param_section_started and "cmd-param" in line:
            pytest.fail("Command parameter should not appear in general parameters")
    
    # general-param should appear
    assert "general-param" in captured.out


def test_display_command_help_valid_command(capsys):
    """Test display_command_help for a valid command."""
    setup_function()
    
    def test_action():
        pass
    
    param.add_param({
        PARAM_NAME: "req-param",
        PARAM_DESCRIPTION: "Required parameter",
        PARAM_ALIASES: ["--req"],
        PARAM_CONFIG_NAME: "req-param"
    })
    
    command.add_command({
        COMMAND_NAME: "build",
        COMMAND_DESCRIPTION: "Build the project",
        COMMAND_HELP: "This command builds the entire project.\nUse with caution.",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: ["req-param"]
    })
    
    help.display_command_help("build")
    
    captured = capsys.readouterr()
    assert "Command: build" in captured.out
    assert "Build the project" in captured.out
    assert "This command builds the entire project" in captured.out
    assert "Parameters:" in captured.out
    assert "req-param" in captured.out


def test_display_command_help_unknown_command(capsys):
    """Test display_command_help with unknown command shows general help."""
    setup_function()
    
    help.display_command_help("unknown-cmd")
    
    captured = capsys.readouterr()
    assert "Unknown command: unknown-cmd" in captured.out
    assert "Usage:" in captured.out


def test_display_command_help_no_params(capsys):
    """Test display_command_help for command without required params."""
    setup_function()
    
    def test_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "simple",
        COMMAND_DESCRIPTION: "Simple command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    help.display_command_help("simple")
    
    captured = capsys.readouterr()
    assert "Command: simple" in captured.out
    assert "Simple command" in captured.out
    # Should not show parameters section
    assert "Parameters:" not in captured.out


def test_grouped_params(capsys):
    """Test that parameters are grouped by param-group."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: "input1",
        PARAM_DESCRIPTION: "Input file 1",
        PARAM_ALIASES: ["--input1"],
        PARAM_GROUP: "Input Options"
    })
    
    param.add_param({
        PARAM_NAME: "input2",
        PARAM_DESCRIPTION: "Input file 2",
        PARAM_ALIASES: ["--input2"],
        PARAM_GROUP: "Input Options"
    })
    
    param.add_param({
        PARAM_NAME: "output",
        PARAM_DESCRIPTION: "Output file",
        PARAM_ALIASES: ["--output"],
        PARAM_GROUP: "Output Options"
    })
    
    param.add_param({
        PARAM_NAME: "verbose",
        PARAM_DESCRIPTION: "Verbose mode",
        PARAM_ALIASES: ["--verbose"]
    })
    
    help.display_all_help()
    
    captured = capsys.readouterr()
    assert "Input Options:" in captured.out
    assert "Output Options:" in captured.out
    assert "input1" in captured.out
    assert "input2" in captured.out
    assert "output" in captured.out
    # Ungrouped param should appear first
    lines = captured.out.split('\n')
    verbose_line = -1
    input_options_line = -1
    for i, line in enumerate(lines):
        if "verbose" in line:
            verbose_line = i
        if "Input Options:" in line:
            input_options_line = i
    assert verbose_line < input_options_line, "Ungrouped params should appear before grouped params"


def test_handle_help_with_arg_no_help(capsys):
    """Test handle_help_with_arg returns False when 'help' is not in args."""
    setup_function()
    
    result = help.handle_help_with_arg(["other-command"])
    assert result is False


def test_handle_help_with_arg_just_help(capsys):
    """Test handle_help_with_arg displays general help for 'help'."""
    setup_function()
    
    result = help.handle_help_with_arg(["help"])
    assert result is True
    
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_handle_help_with_arg_help_command(capsys):
    """Test handle_help_with_arg displays command help for 'help <command>'."""
    setup_function()
    
    def test_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "build",
        COMMAND_DESCRIPTION: "Build the project",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    result = help.handle_help_with_arg(["help", "build"])
    assert result is True
    
    captured = capsys.readouterr()
    assert "Command: build" in captured.out


def test_get_param_by_bind_name():
    """Test _get_param_by_bind_name finds param by bind_to value."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: "test-param",
        PARAM_CONFIG_NAME: "test_bind",
        PARAM_ALIASES: ["--test"]
    })
    
    result = help._get_param_by_bind_name("test_bind")
    assert result is not None
    assert result[PARAM_NAME] == "test-param"


def test_get_param_by_bind_name_not_found():
    """Test _get_param_by_bind_name returns None for unknown bind name."""
    setup_function()
    
    result = help._get_param_by_bind_name("unknown")
    assert result is None


def test_get_param_by_bind_name_uses_name_as_default():
    """Test _get_param_by_bind_name uses name when bind_to is not specified."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: "simple",
        PARAM_ALIASES: ["--simple"]
    })
    
    result = help._get_param_by_bind_name("simple")
    assert result is not None
    assert result[PARAM_NAME] == "simple"


def test_format_param_table_row():
    """Test _format_param_table_row formats parameter correctly."""
    setup_function()
    
    test_param = {
        PARAM_NAME: "test-param",
        PARAM_DESCRIPTION: "Test description",
        PARAM_ALIASES: ["--test", "-t"]
    }
    
    result = help._format_param_table_row(test_param)
    assert "--test, -t" in result
    assert "test-param" in result
    assert "Test description" in result


def test_show_help_command(capsys):
    """Test show_help_command displays general help."""
    setup_function()
    
    help.show_help_command()
    
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_has_app_commands_queued_with_app_command():
    """Test has_app_commands_queued returns True when app command is queued."""
    setup_function()
    
    def test_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "app-cmd",
        COMMAND_DESCRIPTION: "App command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    command.queue_command("app-cmd")
    assert command.has_app_commands_queued() is True


def test_has_app_commands_queued_with_framework_command():
    """Test has_app_commands_queued returns False when only framework command is queued."""
    setup_function()
    from spafw37.constants.command import COMMAND_FRAMEWORK
    
    def test_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "framework-cmd",
        COMMAND_DESCRIPTION: "Framework command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_FRAMEWORK: True
    })
    
    command.queue_command("framework-cmd")
    assert command.has_app_commands_queued() is False


def test_has_app_commands_queued_no_commands():
    """Test has_app_commands_queued returns False when no commands are queued."""
    setup_function()
    assert command.has_app_commands_queued() is False


def test_has_app_commands_queued_mixed_commands():
    """Test has_app_commands_queued returns True when app and framework commands are queued."""
    setup_function()
    from spafw37.constants.command import COMMAND_FRAMEWORK
    
    def test_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "framework-cmd",
        COMMAND_DESCRIPTION: "Framework command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_FRAMEWORK: True
    })
    
    command.add_command({
        COMMAND_NAME: "app-cmd",
        COMMAND_DESCRIPTION: "App command",
        COMMAND_ACTION: test_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    command.queue_command("framework-cmd")
    command.queue_command("app-cmd")
    assert command.has_app_commands_queued() is True


def test_command_parameter_error_has_command_name():
    """Test CommandParameterError stores command name."""
    from spafw37.command import CommandParameterError
    
    error = CommandParameterError("Test error", command_name="test-cmd")
    assert error.command_name == "test-cmd"
    assert str(error) == "Test error"


def test_command_parameter_error_is_value_error():
    """Test CommandParameterError is a subclass of ValueError."""
    from spafw37.command import CommandParameterError
    
    error = CommandParameterError("Test error")
    assert isinstance(error, ValueError)


def test_get_command_params_missing_command():
    """Test _get_command_params returns empty list for missing command.
    
    When requesting parameters for a command that doesn't exist, the function
    should return an empty list. This validates error handling (lines 50-52).
    """
    result = help._get_command_params('nonexistent-command')
    assert result == []


def test_display_command_help_with_cycle_commands(capsys):
    """Test display_command_help shows cycle commands section.
    
    When a command has cycle commands, the help display should include a
    "Cycle Commands" section listing the commands in the cycle. This validates
    the cycle command display functionality (lines 218-225).
    """
    from spafw37.constants.cycle import CYCLE_NAME, CYCLE_LOOP, CYCLE_COMMANDS
    from spafw37.constants.command import COMMAND_DESCRIPTION
    
    def loop_func():
        return False
    
    # Create sub-commands first
    sub_cmd_1 = {
        COMMAND_NAME: 'sub-cmd-1',
        COMMAND_ACTION: lambda: None,
        COMMAND_DESCRIPTION: 'First sub command'
    }
    
    sub_cmd_2 = {
        COMMAND_NAME: 'sub-cmd-2',
        COMMAND_ACTION: lambda: None,
        COMMAND_DESCRIPTION: 'Second sub command'
    }
    
    # Register sub-commands before parent cycle
    command.add_commands([sub_cmd_1, sub_cmd_2])
    
    # Create a command with a cycle that references the sub-commands
    cycle_cmd = {
        COMMAND_NAME: 'cycle-parent',
        COMMAND_ACTION: lambda: None,
        COMMAND_DESCRIPTION: 'Parent command with cycle',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'test-cycle',
            CYCLE_LOOP: loop_func,
            CYCLE_COMMANDS: ['sub-cmd-1', 'sub-cmd-2']
        }
    }
    
    command.add_command(cycle_cmd)
    
    help.display_command_help('cycle-parent')
    
    captured = capsys.readouterr()
    assert 'Cycle Commands:' in captured.out
    assert 'sub-cmd-1' in captured.out
    assert 'sub-cmd-2' in captured.out
    assert 'First sub command' in captured.out
    assert 'Second sub command' in captured.out


def test_display_command_help_with_nested_cycle_commands(capsys):
    """Test display_command_help shows nested cycle commands with indentation.
    
    When a command has nested cycles (cycle within a cycle), the help display
    should show nested cycle commands with proper indentation. This validates
    the recursive cycle command display (lines 236-249).
    """
    from spafw37.constants.cycle import CYCLE_NAME, CYCLE_LOOP, CYCLE_COMMANDS
    from spafw37.constants.command import COMMAND_DESCRIPTION
    
    def loop_func():
        return False
    
    # Register commands from innermost to outermost
    inner_cmd = {
        COMMAND_NAME: 'inner-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_DESCRIPTION: 'Innermost command'
    }
    
    command.add_command(inner_cmd)
    
    # Create middle cycle that references inner command
    mid_cycle_cmd = {
        COMMAND_NAME: 'mid-cycle',
        COMMAND_ACTION: lambda: None,
        COMMAND_DESCRIPTION: 'Middle cycle command',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'mid-cycle-def',
            CYCLE_LOOP: loop_func,
            CYCLE_COMMANDS: ['inner-cmd']
        }
    }
    
    command.add_command(mid_cycle_cmd)
    
    # Create parent cycle that references middle cycle
    parent_cmd = {
        COMMAND_NAME: 'parent-cycle',
        COMMAND_ACTION: lambda: None,
        COMMAND_DESCRIPTION: 'Parent with nested cycles',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'parent-cycle-def',
            CYCLE_LOOP: loop_func,
            CYCLE_COMMANDS: ['mid-cycle']
        }
    }
    
    command.add_command(parent_cmd)
    
    help.display_command_help('parent-cycle')
    
    captured = capsys.readouterr()
    assert 'Cycle Commands:' in captured.out
    assert 'mid-cycle' in captured.out
    assert 'Middle cycle command' in captured.out
    assert 'inner-cmd' in captured.out
    assert 'Innermost command' in captured.out
