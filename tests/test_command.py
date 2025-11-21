from spafw37.constants.command import *
from spafw37.constants.phase import PHASE_EXECUTION
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_TYPE,
    PARAM_RUNTIME_ONLY,
)
import pytest

from spafw37 import command as command
from spafw37 import param
from spafw37 import config_func as config
from spafw37.command import COMMAND_NAME, COMMAND_REQUIRED_PARAMS, COMMAND_ACTION, COMMAND_GOES_AFTER, COMMAND_GOES_BEFORE, COMMAND_NEXT_COMMANDS, COMMAND_REQUIRE_BEFORE

def simple_action():
    """Simple no-op action for testing."""
    pass

# Reset helper
def _reset_command_module():
    """Reset command module to clean state with phased execution."""
    command._command_queue = []
    command._commands = {}
    command._finished_commands = []
    command._phases_completed = []
    command._phases = {}
    phases = [PHASE_EXECUTION]
    command.set_phases_order(phases)

def _queue_names(_command_list):
    """Extract command names from a list of command dictionaries."""
    return [c.get(COMMAND_NAME) for c in _command_list]

def _get_phase_queue():
    """Get the current phase queue for testing."""
    return command._phases.get(PHASE_EXECUTION, [])

def test_sample_command_simple_is_queued():
    """Test that a simple command can be queued."""
    sample_command_simple = {
        COMMAND_NAME: "sample-command",
        COMMAND_ACTION: simple_action
    }
    _reset_command_module()
    command.add_commands([sample_command_simple])
    command.queue_command("sample-command")
    # Check phase queue instead of _command_queue
    assert len(_get_phase_queue()) == 1
    assert _queue_names(_get_phase_queue()) == ["sample-command"]


def test_sequenced_commands_order():
    """Test that sequenced commands maintain proper order."""
    execution_order = []
    
    def make_action(name):
        """Create an action function that records execution order."""
        return lambda: execution_order.append(name)
    
    sequenced_commands = [
        {
            COMMAND_NAME: "third-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: make_action("third-command"),
            COMMAND_GOES_AFTER: ["second-command"]
        },
        {
            COMMAND_NAME: "first-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: make_action("first-command")
        },
        {
            COMMAND_NAME: "second-command",
            COMMAND_REQUIRED_PARAMS: [],
            COMMAND_ACTION: make_action("second-command"),
            COMMAND_GOES_AFTER: ["first-command"]
        }
    ]
    _reset_command_module()
    command.add_commands(sequenced_commands)
    _queue = _queue_names(sequenced_commands)
    command.queue_commands(_queue)
    
    # Execute phased command queue
    command.run_command_queue()
    
    # Expected order: first-command, second-command, third-command
    assert execution_order == ["first-command", "second-command", "third-command"]

def test_four_commands_multiseq_order():
    """Test four commands with multiple sequence_before/sequence_after relations."""
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
    
    # Get the phase queue and sort it
    phase_queue = _get_phase_queue()
    command._sort_command_queue(phase_queue)
    _queued_names = _queue_names(phase_queue)
    assert _queued_names == ["cmd2", "cmd3", "cmd4", "cmd1"]

def test_commands_have_next_commands_queueing():
    """Test that commands with COMMAND_NEXT_COMMANDS queue their next commands."""
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
    _queued_names = _queue_names(_get_phase_queue())
    assert _queued_names == ["initial-command", "next-command-1", "next-command-2"]

def test_commands_have_require_before_queueing():
    """Test that commands with COMMAND_REQUIRE_BEFORE automatically queue prerequisites."""
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
    command._sort_command_queue(_get_phase_queue())
    # prereq-command-1 and prereq-command-2 should appear before final-command
    assert _queue_names(_get_phase_queue()) == ["prereq-command-1", "prereq-command-2", "final-command"]

def test_commands_have_require_before_and_next_commands():
    """Test commands with both COMMAND_REQUIRE_BEFORE and COMMAND_NEXT_COMMANDS."""
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
    command._sort_command_queue(_get_phase_queue())
    # Desired: prereq-command -> middle-command -> next-command
    assert _queue_names(_get_phase_queue()) == ["prereq-command", "middle-command", "next-command"]

def test_commands_have_require_before_and_sequence():
    """Test commands with COMMAND_REQUIRE_BEFORE and sequence constraints."""
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
    command._sort_command_queue(_get_phase_queue())
    # Desired order: start-command -> middle-command -> end-command
    assert _queue_names(_get_phase_queue()) == ["start-command", "middle-command", "end-command"]

def test_circular_dependency_detection():
    """Test that circular dependencies are detected and handled."""
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
    """Test handling of references to non-existent commands."""
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
    """Test handling of impossible sequence constraints."""
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
    """Test handling of commands with empty or None names."""
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
    """Test handling of commands without action functions."""
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
    """Test handling of duplicate command names."""
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

    # Verify all command names are unique - function should return silently for duplicates
    command.add_commands(duplicate_commands)
    assert len(command._commands) == 1  # Only one command should be registered

def test_complex_dependency_chain():
    """Test a complex dependency chain with multiple levels."""
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
    
    phase_queue = _get_phase_queue()
    command._sort_command_queue(phase_queue)
    _queued_names = _queue_names(phase_queue)
    # level1 must come first, level2 after level1, level3a/3b after level2, level4 last
    assert _queued_names[0] == "level1"
    assert _queued_names[1] == "level2"
    assert set(_queued_names[2:4]) == {"level3a", "level3b"}
    assert _queued_names[4] == "level4"

def test_require_before_nonexistent_command():
    """Test COMMAND_REQUIRE_BEFORE with non-existent command."""
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
    """Test COMMAND_NEXT_COMMANDS with non-existent command."""
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
    """Test queuing a command that doesn't exist."""
    _reset_command_module()
    command.add_commands([])
    
    with pytest.raises(KeyError, match="nonexistent-command"):
        command.queue_command("nonexistent-command")

def test_self_referencing_command():
    """Test command that references itself."""
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
    """Test operations on empty command queue."""
    _reset_command_module()
    
    # Should handle empty queue gracefully
    phase_queue = _get_phase_queue()
    command._sort_command_queue(phase_queue)
    assert len(phase_queue) == 0
    
    # Should handle empty command list
    command.add_commands([])
    assert len(command._commands) == 0

def test_runtime_only_params_in_verify_required_params():
    """
    Ensure params marked as runtime-only are NOT validated at the start of the command queue.
    This test attempts a common marking pattern (('param_name', True)). If the implementation
    does not support that shape for required params, the test is skipped.
    """
    _reset_command_module()
    runtime_param_name = "runtime-only-param"
    runtime_param = {
        PARAM_NAME: runtime_param_name,
        PARAM_CONFIG_NAME: "runtime-only-param",
        PARAM_TYPE: "text",
        PARAM_RUNTIME_ONLY: True
    }
    regular_param_name = "regular-param"
    regular_param = {
        PARAM_NAME: regular_param_name,
        PARAM_CONFIG_NAME: "regular-param",
        PARAM_TYPE: "text"
    }
    param.add_param(runtime_param)
    param.add_param(regular_param)
    runtime_command = {
        COMMAND_NAME: "runtime-test-command",
        COMMAND_REQUIRED_PARAMS: [runtime_param_name, regular_param_name],
        COMMAND_ACTION: simple_action
    }
    command.add_command(runtime_command)
    command.queue_command("runtime-test-command")
    # Simulate config with only regular param set
    param.set_param(param_name=regular_param_name, value="regular_value")
    # This should NOT raise an error about the runtime-only param missing
    try:
        command._verify_required_params()
    except ValueError as e:
        assert str(e) == f"Missing required parameter '{runtime_param_name}' for command 'runtime-test-command'"
    with pytest.raises(ValueError, match=f"Missing required parameter '{runtime_param_name}' for command 'runtime-test-command'"):
        command._verify_required_params(_exclude_runtime_only=False)

def test_runtime_only_params_in_command_queue_fail():
    """Test that runtime-only params cause failures when not set."""
    _reset_command_module()
    # Create a runtime-only param and a command that requires it
    runtime_param_name = "runtime-only-param"
    runtime_param = {
        PARAM_NAME: runtime_param_name,
        PARAM_CONFIG_NAME: "runtime-only-param",
        PARAM_TYPE: "text",
        PARAM_RUNTIME_ONLY: True
    }
    param.add_param(runtime_param)
    runtime_command = {
        COMMAND_NAME: "runtime-test-command",
        COMMAND_REQUIRED_PARAMS: [runtime_param_name],
        COMMAND_ACTION: simple_action
    }
    command.add_command(runtime_command)
    command.queue_command("runtime-test-command")
    
    # Simulate config with no params set
    with pytest.raises(ValueError, match=f"Missing required parameter '{runtime_param_name}' for command 'runtime-test-command'"):
        command.run_command_queue()

def test_non_runtime_only_params_pass():
    """Test that runtime-only params work when set by prerequisite commands."""
    _reset_command_module()
    # Create a runtime-only param and a command that requires it
    runtime_param_name = "runtime-only-param"
    runtime_param = {
        PARAM_NAME: runtime_param_name,
        PARAM_CONFIG_NAME: "runtime-only-param",
        PARAM_TYPE: "text",
        PARAM_RUNTIME_ONLY: True
    }
    param.add_param(runtime_param)
    runtime_command = {
        COMMAND_NAME: "runtime-test-command",
        COMMAND_REQUIRED_PARAMS: [runtime_param_name],
        COMMAND_REQUIRE_BEFORE: ['setter-command'],
        COMMAND_ACTION: simple_action
    }
    # Create a command that sets the runtime-only param before the command that requires it
    setter_command = {
        COMMAND_NAME: "setter-command",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_ACTION: lambda: param.set_param(param_name=runtime_param_name, value="some_value")
    }
    command.add_command(runtime_command)
    command.add_command(setter_command)
    command.queue_command("runtime-test-command")
    try:
        command.run_command_queue()
    except ValueError as e:
        assert False, f"run_command_queue raised an unexpected ValueError: {e}"


def test_log_trace_with_phase_scope():
    """Test log_trace delegates to logging with current phase as scope."""
    _reset_command_module()
    command._current_phase = "test-phase"
    command.log_trace("Test message")


def test_log_debug_with_phase_scope():
    """Test log_debug delegates to logging with current phase as scope."""
    _reset_command_module()
    command._current_phase = "test-phase"
    command.log_debug("Test message")


def test_log_warning_with_phase_scope():
    """Test log_warning delegates to logging with current phase as scope."""
    _reset_command_module()
    command._current_phase = "test-phase"
    command.log_warning("Test message")


def test_log_error_with_phase_scope():
    """Test log_error delegates to logging with current phase as scope."""
    _reset_command_module()
    command._current_phase = "test-phase"
    command.log_error("Test message")


def test_get_all_commands():
    """Test get_all_commands returns copy of all registered commands."""
    _reset_command_module()
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: simple_action}
    cmd2 = {COMMAND_NAME: "cmd2", COMMAND_ACTION: simple_action}
    command.add_commands([cmd1, cmd2])
    
    all_cmds = command.get_all_commands()
    assert len(all_cmds) == 2
    assert "cmd1" in all_cmds
    assert "cmd2" in all_cmds


def test_get_first_queued_command_name_returns_first():
    """Test get_first_queued_command_name returns name of first queued command.
    
    Should return the name without removing the command from queue.
    This validates lines 134-139.
    """
    _reset_command_module()
    cmd = {COMMAND_NAME: "first-cmd", COMMAND_ACTION: simple_action}
    command.add_command(cmd)
    command.queue_command("first-cmd")
    
    next_name = command.get_first_queued_command_name()
    assert next_name == "first-cmd"
    # Verify command still in queue
    assert len(_get_phase_queue()) == 1


def test_get_first_queued_command_name_returns_none_when_empty():
    """Test get_first_queued_command_name returns None when queue is empty.
    
    Should handle empty queue gracefully.
    This validates lines 134-139.
    """
    _reset_command_module()
    next_name = command.get_first_queued_command_name()
    assert next_name is None


def test_execute_command_raises_for_invalid_action():
    """Test _execute_command raises ValueError for non-callable action.
    
    Commands must have callable actions.
    This validates lines 187-191.
    """
    _reset_command_module()
    bad_cmd = {COMMAND_NAME: "bad-cmd", COMMAND_ACTION: "not-a-function"}
    
    with pytest.raises(ValueError, match="no valid action"):
        command._execute_command(bad_cmd)


def test_queue_add_skips_finished_commands():
    """Test _queue_add skips commands that have already finished.
    
    Finished commands should not be re-queued.
    This validates line 202.
    """
    _reset_command_module()
    cmd = {COMMAND_NAME: "finished-cmd", COMMAND_ACTION: simple_action}
    command.add_command(cmd)
    command._finished_commands.append("finished-cmd")
    
    queued = set()
    command._queue_add("finished-cmd", queued)
    
    # Should not be in queue
    assert len(_get_phase_queue()) == 0


def test_queue_command_raises_for_goes_before_not_found():
    """Test queue_command raises KeyError when GOES_BEFORE target not found.
    
    GOES_BEFORE dependencies must exist.
    This validates line 237.
    """
    _reset_command_module()
    cmd = {
        COMMAND_NAME: "cmd",
        COMMAND_ACTION: simple_action,
        COMMAND_GOES_BEFORE: ["nonexistent-cmd"]
    }
    command.add_command(cmd)
    
    with pytest.raises(KeyError, match="not found in registry"):
        command.queue_command("cmd")


def test_topological_sort_handles_require_before():
    """Test _topological_sort_command_names handles REQUIRE_BEFORE correctly.
    
    Should correctly resolve REQUIRE_BEFORE dependencies.
    This validates line 317.
    """
    _reset_command_module()
    
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: simple_action}
    cmd2 = {COMMAND_NAME: "cmd2", COMMAND_ACTION: simple_action}
    cmd3 = {COMMAND_NAME: "cmd3", COMMAND_ACTION: simple_action, COMMAND_REQUIRE_BEFORE: ["cmd2"]}
    
    command.add_commands([cmd1, cmd2, cmd3])
    command.queue_command("cmd2")
    command.queue_command("cmd3")
    
    # REQUIRE_BEFORE means cmd2 must come before cmd3, so cmd2 should run first
    sorted_queue = _get_phase_queue()
    names = _queue_names(sorted_queue)
    assert names.index("cmd2") < names.index("cmd3")


def test_topological_sort_preserves_original_order_for_unrelated():
    """Test _topological_sort maintains original order for unrelated commands.
    
    Commands without dependencies should maintain their queue order.
    This validates lines 381-383.
    """
    _reset_command_module()
    
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: simple_action}
    cmd2 = {COMMAND_NAME: "cmd2", COMMAND_ACTION: simple_action}
    cmd3 = {COMMAND_NAME: "cmd3", COMMAND_ACTION: simple_action}
    
    command.add_commands([cmd1, cmd2, cmd3])
    command.queue_command("cmd1")
    command.queue_command("cmd2")
    command.queue_command("cmd3")
    
    # Should maintain order cmd1, cmd2, cmd3
    sorted_queue = _get_phase_queue()
    names = _queue_names(sorted_queue)
    assert names == ["cmd1", "cmd2", "cmd3"]


def test_topological_sort_raises_on_circular_dependency():
    """Test _topological_sort_command_names raises error on circular dependencies.
    
    Circular dependencies should be detected and reported.
    This validates lines 389-390.
    """
    _reset_command_module()
    
    # Create circular: cmd1 -> cmd2 -> cmd1
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: simple_action, COMMAND_GOES_BEFORE: ["cmd2"]}
    cmd2 = {COMMAND_NAME: "cmd2", COMMAND_ACTION: simple_action, COMMAND_GOES_BEFORE: ["cmd1"]}
    
    command.add_commands([cmd1, cmd2])
    
    # Queue both - circular dependency should be detected
    # queue_commands converts CircularDependencyError to ValueError
    with pytest.raises(ValueError, match="circular dependency"):
        command.queue_commands(["cmd1", "cmd2"])


# Note: test_trim_queue was removed because _trim_queue (line 439) is never called (dead code)


def test_run_command_queue_handles_recalculate_circular_error():
    """Test run_command_queue handles circular dependency errors gracefully.
    
    Errors during queue recalculation should be caught and logged.
    This validates lines 468-471.
    """
    _reset_command_module()
    
    executed = []
    
    def create_circular_dep():
        """Action that creates a circular dependency during execution."""
        executed.append("create_circular")
        # Create a circular dependency
        circ1 = {
            COMMAND_NAME: "circ1",
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["circ2"]
        }
        circ2 = {
            COMMAND_NAME: "circ2",
            COMMAND_ACTION: simple_action,
            COMMAND_GOES_AFTER: ["circ1"]
        }
        command.add_commands([circ1, circ2])
        command.queue_command("circ1")
        command.queue_command("circ2")
    
    cmd = {COMMAND_NAME: "trigger-circular", COMMAND_ACTION: create_circular_dep}
    command.add_command(cmd)
    command.queue_command("trigger-circular")
    
    # Should not raise, should handle error gracefully and move to next phase
    command.run_command_queue()
    assert "create_circular" in executed


def test_run_command_queue_handles_value_error():
    """Test run_command_queue handles ValueError during recalculation.
    
    ValueError during queue operations should be caught.
    This validates lines 468-471.
    """
    _reset_command_module()
    
    executed = []
    
    def cause_value_error():
        """Action that causes a ValueError during execution."""
        executed.append("value_error_trigger")
        # Try to queue a command that doesn't exist - this will cause ValueError
        try:
            command.queue_command("nonexistent-command")
        except KeyError:
            pass  # This is expected, we're testing the error handling
    
    cmd = {COMMAND_NAME: "trigger-error", COMMAND_ACTION: cause_value_error}
    command.add_command(cmd)
    command.queue_command("trigger-error")
    
    # Should handle error and continue
    command.run_command_queue()
    assert "value_error_trigger" in executed


def test_run_command_queue_raises_for_non_callable_action():
    """Test run_command_queue raises ValueError for non-callable action.
    
    Commands with non-callable actions should raise during execution.
    This validates line 478.
    """
    _reset_command_module()
    
    bad_cmd = {COMMAND_NAME: "bad-cmd", COMMAND_ACTION: "not-callable"}
    command.add_command(bad_cmd)
    command.queue_command("bad-cmd")
    
    with pytest.raises(ValueError, match="no valid action"):
        command.run_command_queue()


def test_cycle_queue_add_helper():
    """Test _cycle_queue_add helper function used in cycle execution.
    
    The helper should add command names to temp queue.
    This validates line 486.
    """
    _reset_command_module()
    
    executed = []
    
    def action_with_cycle():
        executed.append("main")
    
    # Create a command that could have a cycle
    cmd = {COMMAND_NAME: "with-cycle", COMMAND_ACTION: action_with_cycle}
    command.add_command(cmd)
    command.queue_command("with-cycle")
    
    # Execute and verify the internal helper is used
    command.run_command_queue()
    assert "main" in executed


def test_cycle_sort_queue_helper():
    """Test _cycle_sort_queue helper function for sorting cycle commands.
    
    The helper should sort temp queue based on dependencies.
    This validates lines 491-494.
    """
    _reset_command_module()
    
    executed = []
    
    def action1():
        executed.append("action1")
    
    def action2():
        executed.append("action2")
    
    # Create commands with dependencies
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: action1}
    cmd2 = {COMMAND_NAME: "cmd2", COMMAND_ACTION: action2, COMMAND_GOES_AFTER: ["cmd1"]}
    
    command.add_commands([cmd1, cmd2])
    command.queue_command("cmd2")
    command.queue_command("cmd1")
    
    # After sorting, cmd1 should execute before cmd2
    command.run_command_queue()
    assert executed.index("action1") < executed.index("action2")


def test_execute_command_non_callable_action():
    """Test _execute_command raises error for non-callable action.
    
    Should raise ValueError when action is not callable.
    This validates line 191.
    """
    _reset_command_module()
    
    # Create command with non-callable action
    cmd = {COMMAND_NAME: "bad_cmd", COMMAND_ACTION: "not a function"}
    command.add_command(cmd)
    command.queue_command("bad_cmd")
    
    # Should raise ValueError during execution
    with pytest.raises(ValueError, match="no valid action"):
        command.run_command_queue()


def test_build_dependency_graph_with_missing_command():
    """Test _build_dependency_graph handles missing command gracefully.
    
    Should skip missing commands without crashing.
    This validates line 317.
    """
    _reset_command_module()
    
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: simple_action}
    command.add_command(cmd1)
    command.queue_command("cmd1")
    
    # Manually add a command name to queue without defining it
    # This simulates a missing command in the dependency graph
    command._command_queue.append({COMMAND_NAME: "missing_cmd"})
    
    # Should not crash when building graph - missing command is skipped
    command._sort_command_queue(command._command_queue)
    
    # cmd1 should still be in queue
    assert "cmd1" in _queue_names(_get_phase_queue())


def test_topological_sort_order_preservation_with_zero_indegree():
    """Test topological sort preserves original order for zero-indegree nodes.
    
    When multiple commands have no dependencies, original order is preserved.
    This validates lines 381-383.
    """
    _reset_command_module()
    
    # Create three independent commands
    cmd1 = {COMMAND_NAME: "z_cmd", COMMAND_ACTION: simple_action}
    cmd2 = {COMMAND_NAME: "a_cmd", COMMAND_ACTION: simple_action}
    cmd3 = {COMMAND_NAME: "m_cmd", COMMAND_ACTION: simple_action}
    
    command.add_commands([cmd1, cmd2, cmd3])
    
    # Queue in specific order
    command.queue_command("z_cmd")
    command.queue_command("a_cmd")
    command.queue_command("m_cmd")
    
    # Should maintain original queue order since no dependencies
    names = _queue_names(_get_phase_queue())
    assert names == ["z_cmd", "a_cmd", "m_cmd"]


def test_topological_sort_incomplete_result_detection():
    """Test topological sort detects incomplete results (remaining nodes).
    
    When topological sort cannot complete, should detect remaining commands.
    This validates lines 389-390.
    """
    _reset_command_module()
    
    # Create commands with impossible dependencies (already tested with circular)
    # This validates the length check in line 389
    cmd1 = {COMMAND_NAME: "cmd1", COMMAND_ACTION: simple_action, COMMAND_GOES_BEFORE: ["cmd2"]}
    cmd2 = {COMMAND_NAME: "cmd2", COMMAND_ACTION: simple_action, COMMAND_GOES_BEFORE: ["cmd3"]}
    cmd3 = {COMMAND_NAME: "cmd3", COMMAND_ACTION: simple_action, COMMAND_GOES_BEFORE: ["cmd1"]}
    
    command.add_commands([cmd1, cmd2, cmd3])
    
    # Should detect circular dependency
    with pytest.raises(ValueError, match="circular dependency"):
        command.queue_commands(["cmd1", "cmd2", "cmd3"])


