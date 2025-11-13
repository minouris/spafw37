"""Tests for inline object definitions in command and param fields.

This module tests the ability to define params and commands inline within
other object definitions, rather than only by name reference.
"""

import pytest
from spafw37 import command, param, config
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_GOES_BEFORE,
    COMMAND_GOES_AFTER,
    COMMAND_REQUIRE_BEFORE,
    COMMAND_NEXT_COMMANDS,
    COMMAND_TRIGGER_PARAM,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_TOGGLE,
    PARAM_ALIASES,
    PARAM_SWITCH_LIST,
)


def setup_function():
    """Reset module state before each test."""
    command._commands = {}
    command._finished_commands = []
    command._command_queue = []
    command._phases = {config.get_default_phase(): []}
    command._phases_completed = []
    command._current_phase = None
    param._params = {}
    param._param_aliases = {}
    param._xor_list = {}
    config._config = {}


# Tests for inline param definitions in COMMAND_REQUIRED_PARAMS


def test_inline_param_in_required_params():
    """Test inline parameter definition in COMMAND_REQUIRED_PARAMS.
    
    Should register the inline param and normalize to name reference.
    This enables defining params directly in command definitions.
    """
    executed = []
    
    cmd = {
        COMMAND_NAME: "test-cmd",
        COMMAND_ACTION: lambda: executed.append("test-cmd"),
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "inline-param",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                PARAM_ALIASES: ["--inline", "-i"]
            }
        ]
    }
    
    command.add_command(cmd)
    
    # Inline param should be registered
    assert "inline-param" in param._params
    assert param._params["inline-param"][PARAM_NAME] == "inline-param"
    
    # Field should be normalized to name reference
    assert cmd[COMMAND_REQUIRED_PARAMS] == ["inline-param"]
    
    # Aliases should be registered
    assert "--inline" in param._param_aliases
    assert param._param_aliases["--inline"] == "inline-param"


def test_mixed_inline_and_named_params_in_required_params():
    """Test mixing inline and named param references in COMMAND_REQUIRED_PARAMS.
    
    Should support both inline definitions and name references in same list.
    This provides flexibility in command definition.
    """
    # Pre-register a param
    param.add_param({
        PARAM_NAME: "named-param",
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    executed = []
    cmd = {
        COMMAND_NAME: "test-cmd",
        COMMAND_ACTION: lambda: executed.append("test-cmd"),
        COMMAND_REQUIRED_PARAMS: [
            "named-param",
            {
                PARAM_NAME: "inline-param",
                PARAM_TYPE: PARAM_TYPE_TEXT
            }
        ]
    }
    
    command.add_command(cmd)
    
    # Both params should be registered
    assert "named-param" in param._params
    assert "inline-param" in param._params
    
    # Field should be normalized to names only
    assert set(cmd[COMMAND_REQUIRED_PARAMS]) == {"named-param", "inline-param"}


# Tests for inline param definition in COMMAND_TRIGGER_PARAM


def test_inline_param_in_trigger_param():
    """Test inline parameter definition in COMMAND_TRIGGER_PARAM.
    
    Should register the inline param and normalize to name reference.
    This enables defining trigger params inline.
    """
    executed = []
    
    cmd = {
        COMMAND_NAME: "triggered-cmd",
        COMMAND_ACTION: lambda: executed.append("triggered-cmd"),
        COMMAND_TRIGGER_PARAM: {
            PARAM_NAME: "trigger-param",
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ["--trigger", "-t"]
        }
    }
    
    command.add_command(cmd)
    
    # Inline param should be registered
    assert "trigger-param" in param._params
    
    # Field should be normalized to name reference
    assert cmd[COMMAND_TRIGGER_PARAM] == "trigger-param"


# Tests for inline command definitions in dependency/sequencing fields


def test_inline_command_in_goes_before():
    """Test inline command definition in COMMAND_GOES_BEFORE.
    
    Should register the inline command and normalize to name reference.
    This enables defining prerequisite commands inline.
    """
    executed = []
    
    cmd1 = {
        COMMAND_NAME: "cmd1",
        COMMAND_ACTION: lambda: executed.append("cmd1"),
        COMMAND_GOES_BEFORE: [
            {
                COMMAND_NAME: "inline-cmd",
                COMMAND_ACTION: lambda: executed.append("inline-cmd")
            }
        ]
    }
    
    command.add_command(cmd1)
    
    # Inline command should be registered
    assert "inline-cmd" in command._commands
    
    # Field should be normalized to name reference
    assert cmd1[COMMAND_GOES_BEFORE] == ["inline-cmd"]


def test_inline_command_in_goes_after():
    """Test inline command definition in COMMAND_GOES_AFTER.
    
    Should register the inline command and normalize to name reference.
    This enables defining dependency commands inline.
    """
    executed = []
    
    cmd1 = {
        COMMAND_NAME: "cmd1",
        COMMAND_ACTION: lambda: executed.append("cmd1"),
        COMMAND_GOES_AFTER: [
            {
                COMMAND_NAME: "inline-cmd",
                COMMAND_ACTION: lambda: executed.append("inline-cmd")
            }
        ]
    }
    
    command.add_command(cmd1)
    
    # Inline command should be registered
    assert "inline-cmd" in command._commands
    
    # Field should be normalized to name reference
    assert cmd1[COMMAND_GOES_AFTER] == ["inline-cmd"]


def test_inline_command_in_require_before():
    """Test inline command definition in COMMAND_REQUIRE_BEFORE.
    
    Should register the inline command and normalize to name reference.
    This enables defining required prerequisite commands inline.
    """
    executed = []
    
    cmd1 = {
        COMMAND_NAME: "cmd1",
        COMMAND_ACTION: lambda: executed.append("cmd1"),
        COMMAND_REQUIRE_BEFORE: [
            {
                COMMAND_NAME: "inline-cmd",
                COMMAND_ACTION: lambda: executed.append("inline-cmd")
            }
        ]
    }
    
    command.add_command(cmd1)
    
    # Inline command should be registered
    assert "inline-cmd" in command._commands
    
    # Field should be normalized to name reference
    assert cmd1[COMMAND_REQUIRE_BEFORE] == ["inline-cmd"]


def test_inline_command_in_next_commands():
    """Test inline command definition in COMMAND_NEXT_COMMANDS.
    
    Should register the inline command and normalize to name reference.
    This enables defining follow-up commands inline.
    """
    executed = []
    
    cmd1 = {
        COMMAND_NAME: "cmd1",
        COMMAND_ACTION: lambda: executed.append("cmd1"),
        COMMAND_NEXT_COMMANDS: [
            {
                COMMAND_NAME: "inline-cmd",
                COMMAND_ACTION: lambda: executed.append("inline-cmd")
            }
        ]
    }
    
    command.add_command(cmd1)
    
    # Inline command should be registered
    assert "inline-cmd" in command._commands
    
    # Field should be normalized to name reference
    assert cmd1[COMMAND_NEXT_COMMANDS] == ["inline-cmd"]


def test_mixed_inline_and_named_commands():
    """Test mixing inline and named command references.
    
    Should support both inline definitions and name references in same list.
    This provides flexibility in command definition.
    """
    # Pre-register a command
    command.add_command({
        COMMAND_NAME: "named-cmd",
        COMMAND_ACTION: lambda: None
    })
    
    executed = []
    cmd = {
        COMMAND_NAME: "test-cmd",
        COMMAND_ACTION: lambda: executed.append("test-cmd"),
        COMMAND_GOES_BEFORE: [
            "named-cmd",
            {
                COMMAND_NAME: "inline-cmd",
                COMMAND_ACTION: lambda: executed.append("inline-cmd")
            }
        ]
    }
    
    command.add_command(cmd)
    
    # Both commands should be registered
    assert "named-cmd" in command._commands
    assert "inline-cmd" in command._commands
    
    # Field should be normalized to names only
    assert set(cmd[COMMAND_GOES_BEFORE]) == {"named-cmd", "inline-cmd"}


# Tests for inline param definitions in PARAM_SWITCH_LIST


def test_inline_param_in_switch_list():
    """Test inline parameter definition in PARAM_SWITCH_LIST.
    
    Should register the inline param and normalize to name reference.
    This enables defining mutually exclusive params inline.
    """
    test_param = {
        PARAM_NAME: "verbose",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ["--verbose", "-v"],
        PARAM_SWITCH_LIST: [
            {
                PARAM_NAME: "quiet",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,
                PARAM_ALIASES: ["--quiet", "-q"]
            }
        ]
    }
    
    param.add_param(test_param)
    
    # Inline param should be registered
    assert "quiet" in param._params
    
    # Field should be normalized to name reference
    assert test_param[PARAM_SWITCH_LIST] == ["quiet"]
    
    # XOR list should be set up
    assert "verbose" in param._xor_list
    assert "quiet" in param._xor_list["verbose"]


def test_mixed_inline_and_named_params_in_switch_list():
    """Test mixing inline and named param references in PARAM_SWITCH_LIST.
    
    Should support both inline definitions and name references in same list.
    This provides flexibility in parameter definition.
    """
    # Pre-register a param
    param.add_param({
        PARAM_NAME: "silent",
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    })
    
    test_param = {
        PARAM_NAME: "verbose",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: [
            "silent",
            {
                PARAM_NAME: "quiet",
                PARAM_TYPE: PARAM_TYPE_TOGGLE
            }
        ]
    }
    
    param.add_param(test_param)
    
    # Both params should be registered
    assert "silent" in param._params
    assert "quiet" in param._params
    
    # Field should be normalized to names only
    assert set(test_param[PARAM_SWITCH_LIST]) == {"silent", "quiet"}
    
    # XOR relationships should be bidirectional
    # verbose should exclude both silent and quiet
    assert param.has_xor_with("verbose", "silent")
    assert param.has_xor_with("verbose", "quiet")
    # silent should exclude verbose (bidirectional)
    assert param.has_xor_with("silent", "verbose")
    # quiet should exclude verbose (bidirectional)
    assert param.has_xor_with("quiet", "verbose")


# Edge cases and integration tests


def test_inline_definition_not_duplicated():
    """Test that inline definitions don't duplicate if already registered.
    
    Should not re-register if param/command already exists.
    This prevents overwriting existing definitions.
    """
    # Pre-register a param
    original_param = {
        PARAM_NAME: "my-param",
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ["--original"]
    }
    param.add_param(original_param)
    
    # Try to register same param inline
    cmd = {
        COMMAND_NAME: "test-cmd",
        COMMAND_ACTION: lambda: None,
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "my-param",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,  # Different type
                PARAM_ALIASES: ["--duplicate"]  # Different alias
            }
        ]
    }
    
    command.add_command(cmd)
    
    # Original param should be preserved (not overwritten)
    assert param._params["my-param"][PARAM_TYPE] == PARAM_TYPE_TEXT
    assert "--original" in param._param_aliases
    # New alias should NOT be added since param already existed
    assert "--duplicate" not in param._param_aliases


def test_deeply_nested_inline_definitions():
    """Test that inline definitions work with complex nesting.
    
    Should handle inline params in trigger, required params, and switch lists.
    This tests comprehensive inline definition support.
    """
    cmd = {
        COMMAND_NAME: "complex-cmd",
        COMMAND_ACTION: lambda: None,
        COMMAND_TRIGGER_PARAM: {
            PARAM_NAME: "trigger",
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: [
                {
                    PARAM_NAME: "no-trigger",
                    PARAM_TYPE: PARAM_TYPE_TOGGLE
                }
            ]
        },
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "required-1",
                PARAM_TYPE: PARAM_TYPE_TEXT
            },
            {
                PARAM_NAME: "required-2",
                PARAM_TYPE: PARAM_TYPE_TEXT
            }
        ]
    }
    
    command.add_command(cmd)
    
    # All inline params should be registered
    assert "trigger" in param._params
    assert "no-trigger" in param._params
    assert "required-1" in param._params
    assert "required-2" in param._params
    
    # Fields should be normalized
    assert cmd[COMMAND_TRIGGER_PARAM] == "trigger"
    assert set(cmd[COMMAND_REQUIRED_PARAMS]) == {"required-1", "required-2"}


def test_inline_command_execution_integration():
    """Test that inline commands execute correctly.
    
    Should queue and execute inline commands with proper dependencies.
    This validates full integration of inline command definitions.
    """
    executed = []
    
    # Use REQUIRE_BEFORE so the inline command is auto-queued
    cmd1 = {
        COMMAND_NAME: "cmd1",
        COMMAND_ACTION: lambda: executed.append("cmd1"),
        COMMAND_REQUIRE_BEFORE: [
            {
                COMMAND_NAME: "inline-cmd",
                COMMAND_ACTION: lambda: executed.append("inline-cmd")
            }
        ]
    }
    
    command.add_command(cmd1)
    
    # Verify inline command was registered
    assert "inline-cmd" in command._commands
    assert "cmd1" in command._commands
    
    # Check if inline command has action
    inline_cmd_def = command._commands["inline-cmd"]
    print(f"Inline command: {inline_cmd_def}")
    print(f"Has ACTION: {COMMAND_ACTION in inline_cmd_def}")
    print(f"Action callable: {callable(inline_cmd_def.get(COMMAND_ACTION))}")
    
    # Queue and run - inline-cmd should be auto-queued due to REQUIRE_BEFORE
    command.queue_command("cmd1")
    
    # Check what's in the queue before running
    queue_names = [c.get(COMMAND_NAME) for c in command._command_queue]
    print(f"Queue before run: {queue_names}")
    
    command.run_command_queue()
    
    print(f"Executed: {executed}")
    
    # Both commands should have executed
    assert "cmd1" in executed
    assert "inline-cmd" in executed
    # inline-cmd should execute before cmd1 (REQUIRE_BEFORE semantics)
    assert executed.index("inline-cmd") < executed.index("cmd1")
