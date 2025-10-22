from spafw37.config_consts import *
import pytest

from spafw37 import command as command
from spafw37.command import COMMAND_NAME, COMMAND_REQUIRED_PARAMS, COMMAND_ACTION, COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE, COMMAND_NEXT_COMMANDS, COMMAND_REQUIRE_BEFORE

def simple_action():
    pass

# Reset helper
def _reset_command_module():
    command._command_queue = []
    command._commands = {}
    command._required_params = []

def _queue_names(_command_list):
    return [c.get(COMMAND_NAME) for c in _command_list]

def test_sample_command_simple_is_queued():
    sample_command_simple = {
        COMMAND_NAME: "sample-command",
        COMMAND_REQUIRED_PARAMS: ["param1", "param2"],
        COMMAND_ACTION: simple_action
    }
    _reset_command_module()
    command.add_commands([sample_command_simple])
    command.queue_command("sample-command")
    assert len(command._command_queue) == 1
    assert _queue_names(command._command_queue) == ["sample-command"]

def test_sequenced_commands_order():
    sequenced_commands = [ # Order should be: first-command, second-command, third-command
        {
            COMMAND_NAME: "third-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["second-command"]
        },
        {
            COMMAND_NAME: "first-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "second-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["first-command"]
        }
    ]
    _reset_command_module()
    command.add_commands(sequenced_commands)
    _queue = _queue_names(sequenced_commands)
    command.queue_commands(_queue)
    # Expected order: first-command, second-command, third-command
    _queued = _queue_names(command._command_queue)
    assert _queued == ["first-command", "second-command", "third-command"]

def test_four_commands_multiseq_order():
    # Four commands with multiple sequence_before/sequence_after relations.
    # Desired order: cmd2 -> cmd3 -> cmd4 -> cmd1
    four_commands_multiseq = [
        {
            COMMAND_NAME: "cmd1",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["cmd2", "cmd3"],  # cmd1 must come after cmd2 and cmd3
        },
        {
            COMMAND_NAME: "cmd2",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
        },
        {
            COMMAND_NAME: "cmd3",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["cmd2"],  # cmd3 must come after cmd2
        },
        {
            COMMAND_NAME: "cmd4",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["cmd3"],   # cmd4 after cmd3
            COMMAND_GOES_BEFORE: ["cmd1"],  # and before cmd1
        },
    ]
    _reset_command_module()
    command.add_commands(four_commands_multiseq)
    # Desired order: cmd2 -> cmd3 -> cmd4 -> cmd1
    command.queue_commands(_queue_names(four_commands_multiseq))
    command._sort_command_queue()
    _queued_names = _queue_names(command._command_queue)
    assert _queued_names == ["cmd2", "cmd3", "cmd4", "cmd1"]

def test_commands_multiple_params_all_present():    
    commands_multiple_params = [ # All required params should be in _required_params
        {
            COMMAND_NAME: "first-command",
            COMMAND_REQUIRED_PARAMS: ["param1"],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "second-command",
            COMMAND_REQUIRED_PARAMS: ["param2"],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "third-command",
            COMMAND_REQUIRED_PARAMS: ["param3"],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["second-command"]
        }
    ]
    _reset_command_module()
    # Ensure required params are known before adding (simulate config)
    command._required_params = []
    _test_params = ["param1", "param2", "param3"]
    # Add the commands and ensure they are queued (all present)
    command.add_commands(commands_multiple_params)
    command.queue_commands(_queue_names(commands_multiple_params))
    for param in _test_params:
        assert param in command._required_params

def test_commands_have_next_commands_queueing():
    commands_have_next_commands = [
        {
            COMMAND_NAME: "initial-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_NEXT_COMMANDS: ["next-command-1", "next-command-2"] # These will be queued after this command is run, and will be considered to automatically be part of the sequence_after for the first command
        },
        {
            COMMAND_NAME: "next-command-1",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "next-command-2",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]
    _reset_command_module()
    command.add_commands(commands_have_next_commands)
    command.queue_commands(_queue_names(commands_have_next_commands))
    # initial-command should be followed by next-command-1 and next-command-2
    _queued_names = _queue_names(command._command_queue)
    assert _queued_names == ["initial-command", "next-command-1", "next-command-2"]

def test_commands_have_require_before_queueing():
    commands_have_require_before = [
        {
            COMMAND_NAME: "final-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_REQUIRE_BEFORE: ["prereq-command-1", "prereq-command-2"] # These will be automatically queued before this command if not already present. This command will consider these to be part of its sequence_after
        },
        {
            COMMAND_NAME: "prereq-command-1",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "prereq-command-2",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]   
    _reset_command_module()
    command.add_commands(commands_have_require_before)
    command.queue_commands(_queue_names(commands_have_require_before))
    # prereq-command-1 and prereq-command-2 should appear before final-command
    assert _queue_names(command._command_queue) == ["prereq-command-1", "prereq-command-2", "final-command"]

def test_commands_have_require_before_and_next_commands():
    commands_have_require_before_and_next_commands = [
        {
            COMMAND_NAME: "middle-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_REQUIRE_BEFORE: ["prereq-command"],
            COMMAND_NEXT_COMMANDS: ["next-command"]
        },
        {
            COMMAND_NAME: "prereq-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "next-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]  
    _reset_command_module()
    command.add_commands(commands_have_require_before_and_next_commands)
    command.queue_commands(['middle-command'])
    # Desired: prereq-command -> middle-command -> next-command
    assert _queue_names(command._command_queue) == ["prereq-command", "middle-command", "next-command"]

def test_commands_have_require_before_and_sequence():
    commands_have_require_before_and_sequence = [
        {
            COMMAND_NAME: "end-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_REQUIRE_BEFORE: ["middle-command"],
            COMMAND_GOES_AFTER: ["middle-command"]
        },
        {
            COMMAND_NAME: "start-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_NEXT_COMMANDS: ["end-command"]
        },
        {
            COMMAND_NAME: "middle-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]
    _reset_command_module()
    command.add_commands(commands_have_require_before_and_sequence)
    command.queue_commands(['start-command'])  # Queue start-command to trigger dependencies
    # Desired order: start-command -> middle-command -> end-command
    assert _queue_names(command._command_queue) == ["start-command", "middle-command", "end-command"]

def test_circular_dependency_detection():
    """Test that circular dependencies are detected and handled"""
    circular_commands = [
        {
            COMMAND_NAME: "cmd1",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["cmd2"]
        },
        {
            COMMAND_NAME: "cmd2", 
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["cmd3"]
        },
        {
            COMMAND_NAME: "cmd3",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["cmd1"]  # Creates circular dependency
        }
    ]
    _reset_command_module()
    command.add_commands(circular_commands)
    
    with pytest.raises(ValueError, match="circular dependency"):
        command.queue_commands(_queue_names(circular_commands))

def test_missing_command_reference():
    """Test handling of references to non-existent commands"""
    commands_with_missing_ref = [
        {
            COMMAND_NAME: "existing-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["non-existent-command"]
        }
    ]
    _reset_command_module()
    command.add_commands(commands_with_missing_ref)
    
    with pytest.raises(KeyError, match="Command 'non-existent-command' not found in registry."):
        command.queue_commands(["existing-command"])

def test_conflicting_sequence_constraints():
    """Test handling of impossible sequence constraints"""
    conflicting_commands = [
        {
            COMMAND_NAME: "cmd1",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_BEFORE: ["cmd2"],
            COMMAND_GOES_AFTER: ["cmd2"]  # Cannot be both before AND after cmd2
        },
        {
            COMMAND_NAME: "cmd2",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]
    _reset_command_module()
    
    with pytest.raises(ValueError, match="conflicting constraints"):
        command.add_commands(conflicting_commands)

def test_empty_command_name():
    """Test handling of commands with empty or None names"""
    invalid_commands = [
        {
            COMMAND_NAME: "",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]
    _reset_command_module()
    
    with pytest.raises(ValueError, match="Command name cannot be empty"):
        command.add_commands(invalid_commands)

def test_missing_action_function():
    """Test handling of commands without action functions"""
    invalid_commands = [
        {
            COMMAND_NAME: "no-action-command",
            COMMAND_REQUIRED_PARAMS: []
            # Missing COMMAND_ACTION
        }
    ]
    _reset_command_module()
    
    with pytest.raises(ValueError, match="Command action is required"):
        command.add_commands(invalid_commands)

def test_duplicate_command_names():
    """Test handling of duplicate command names"""
    duplicate_commands = [
        {
            COMMAND_NAME: "duplicate-name",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        },
        {
            COMMAND_NAME: "duplicate-name",
            COMMAND_REQUIRED_PARAMS: ["param1"],
            COMMAND_ACTION: simple_action
        }
    ]
    _reset_command_module()
    
    with pytest.raises(ValueError, match="Duplicate command name"):
        command.add_commands(duplicate_commands)

def test_complex_dependency_chain():
    """Test a complex dependency chain with multiple levels"""
    complex_commands = [
        {
            COMMAND_NAME: "level4",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["level3a", "level3b"]
        },
        {
            COMMAND_NAME: "level3a",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["level2"]
        },
        {
            COMMAND_NAME: "level3b",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["level2"]
        },
        {
            COMMAND_NAME: "level2",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["level1"]
        },
        {
            COMMAND_NAME: "level1",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action
        }
    ]
    _reset_command_module()
    command.add_commands(complex_commands)
    command.queue_commands(_queue_names(complex_commands))
    
    _queued_names = _queue_names(command._command_queue)
    # level1 must come first, level2 after level1, level3a/3b after level2, level4 last
    assert _queued_names[0] == "level1"
    assert _queued_names[1] == "level2"
    assert set(_queued_names[2:4]) == {"level3a", "level3b"}
    assert _queued_names[4] == "level4"

def test_require_before_nonexistent_command():
    """Test COMMAND_REQUIRE_BEFORE with non-existent command"""
    commands_require_missing = [
        {
            COMMAND_NAME: "dependent-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_REQUIRE_BEFORE: ["missing-prereq"]
        }
    ]
    _reset_command_module()
    command.add_commands(commands_require_missing)
    
    with pytest.raises(KeyError, match="missing-prereq"):
        command.queue_commands(["dependent-command"])

def test_next_commands_nonexistent():
    """Test COMMAND_NEXT_COMMANDS with non-existent command"""
    commands_next_missing = [
        {
            COMMAND_NAME: "parent-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_NEXT_COMMANDS: ["missing-next"]
        }
    ]
    _reset_command_module()
    command.add_commands(commands_next_missing)
    
    with pytest.raises(KeyError, match="missing-next"):
        command.queue_commands(["parent-command"])

def test_queue_nonexistent_command():
    """Test queuing a command that doesn't exist"""
    _reset_command_module()
    command.add_commands([])
    
    with pytest.raises(KeyError, match="nonexistent-command"):
        command.queue_command("nonexistent-command")

def test_self_referencing_command():
    """Test command that references itself"""
    self_ref_commands = [
        {
            COMMAND_NAME: "self-ref",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["self-ref"]
        }
    ]
    _reset_command_module()
    
    with pytest.raises(ValueError, match="cannot reference itself"):
        command.add_commands(self_ref_commands)

def test_empty_queue_operations():
    """Test operations on empty command queue"""
    _reset_command_module()
    
    # Should handle empty queue gracefully
    command._sort_command_queue()
    assert len(command._command_queue) == 0
    
    # Should handle empty command list
    command.add_commands([])
    assert len(command._commands) == 0

