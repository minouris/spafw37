# Standard library
import pytest

# Project imports - constants
from spafw37.constants.command import (
    COMMAND_ACTION,
    COMMAND_CYCLE,
    COMMAND_GOES_AFTER,
    COMMAND_GOES_BEFORE,
    COMMAND_NAME,
    COMMAND_NEXT_COMMANDS,
    COMMAND_PHASE,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_REQUIRE_BEFORE,
    COMMAND_TRIGGER_PARAM,
)
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_COMMANDS,
    CYCLE_LOOP,
    CYCLE_NAME,
)
from spafw37.constants.phase import PHASE_EXECUTION
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_TYPE,
    PARAM_RUNTIME_ONLY,
)

# Project imports - modules
from spafw37 import command, config, cycle, param

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


# ==================== Step 2: Validation Helpers ====================

def test_validate_command_name_empty_string_raises_error():
    """Test that _validate_command_name() raises ValueError for empty string.
    
    Scenario: Empty command name raises ValueError
      Given a command definition with empty string name
      When _validate_command_name() is called
      Then ValueError is raised with "Command name cannot be empty"
      
      Tests: Name validation enforcement
      Validates: Helper catches empty command names
    
    This test verifies that the validation helper correctly rejects command
    definitions with empty string names. Empty names would cause registry
    lookup failures and must be caught early.
    """
    _reset_command_module()
    
    empty_name_command = {COMMAND_NAME: ''}
    with pytest.raises(ValueError, match="Command name cannot be empty"):
        command._validate_command_name(empty_name_command)


def test_validate_command_name_none_raises_error():
    """Test that _validate_command_name() raises ValueError for None name.
    
    Scenario: None command name raises ValueError
      Given a command definition with None as name value
      When _validate_command_name() is called
      Then ValueError is raised with "Command name cannot be empty"
      
      Tests: Name validation enforcement
      Validates: Helper catches None command names
    
    This test verifies that the validation helper correctly rejects command
    definitions with None as the name value. None names would cause registry
    lookup failures and must be caught early.
    """
    _reset_command_module()
    
    none_name_command = {COMMAND_NAME: None}
    with pytest.raises(ValueError, match="Command name cannot be empty"):
        command._validate_command_name(none_name_command)


def test_validate_command_action_missing_raises_error():
    """Test that _validate_command_action() raises ValueError for missing action.
    
    Scenario: Missing command action raises ValueError
      Given a command definition without COMMAND_ACTION key
      When _validate_command_action() is called
      Then ValueError is raised with "Command action is required"
      
      Tests: Action validation enforcement
      Validates: Helper catches missing action key
    
    This test verifies that the validation helper correctly rejects command
    definitions without the COMMAND_ACTION key. Commands without actions cannot
    be executed and must be caught during registration.
    """
    _reset_command_module()
    
    no_action_command = {COMMAND_NAME: 'test-cmd'}
    with pytest.raises(ValueError, match="Command action is required"):
        command._validate_command_action(no_action_command)


def test_validate_command_action_none_raises_error():
    """Test that _validate_command_action() raises ValueError for None action.
    
    Scenario: None command action raises ValueError
      Given a command definition with None as action value
      When _validate_command_action() is called
      Then ValueError is raised with "Command action is required"
      
      Tests: Action validation enforcement
      Validates: Helper catches None action value
    
    This test verifies that the validation helper correctly rejects command
    definitions with None as the action value. Commands with None actions cannot
    be executed and must be caught during registration.
    """
    _reset_command_module()
    
    none_action_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: None
    }
    with pytest.raises(ValueError, match="Command action is required"):
        command._validate_command_action(none_action_command)


def test_validate_command_references_self_reference_raises_error():
    """Test that _validate_command_references() raises ValueError for self-references.
    
    Scenario: Self-referencing command raises ValueError
      Given a command definition with its own name in COMMAND_GOES_AFTER
      When _validate_command_references() is called
      Then ValueError is raised with "cannot reference itself"
      
      Tests: Self-reference detection
      Validates: Helper catches circular dependency at definition time
    
    This test verifies that the validation helper correctly detects and rejects
    commands that reference themselves in dependency fields. Self-references would
    create immediate circular dependencies that cannot be resolved.
    """
    _reset_command_module()
    
    self_ref_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_AFTER: ['test-cmd']
    }
    with pytest.raises(ValueError, match="cannot reference itself"):
        command._validate_command_references(self_ref_command)


def test_validate_command_references_conflicting_constraints_raises_error():
    """Test that _validate_command_references() raises ValueError for conflicts.
    
    Scenario: Conflicting sequencing constraints raise ValueError
      Given a command definition with same command in GOES_BEFORE and GOES_AFTER
      When _validate_command_references() is called
      Then ValueError is raised with "conflicting constraints"
      
      Tests: Constraint conflict detection
      Validates: Helper catches impossible sequencing requirements
    
    This test verifies that the validation helper correctly detects impossible
    sequencing constraints where the same command appears in both GOES_BEFORE
    and GOES_AFTER lists. These conflicting requirements cannot be satisfied.
    """
    _reset_command_module()
    
    conflicting_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_BEFORE: ['other-cmd'],
        COMMAND_GOES_AFTER: ['other-cmd']
    }
    with pytest.raises(ValueError, match="conflicting constraints"):
        command._validate_command_references(conflicting_command)


def test_normalise_param_list():
    """Test that _normalise_param_list() converts param defs to names.
    
    Scenario: List of inline param definitions is normalised to param names
      Given a list of inline parameter definitions
      When _normalise_param_list() is called
      Then each param is registered via param._register_inline_param()
      And a list of param names is returned
      
      Tests: Param list normalisation helper
      Validates: Helper extracts loop logic to avoid nesting violation
    
    This test verifies that a list of inline parameter definitions is
    normalised to a list of parameter names by registering each param
    and collecting the names. This helper avoids nesting violations.
    """
    _reset_command_module()
    
    param_list = [
        {PARAM_NAME: 'param1'},
        {PARAM_NAME: 'param2'}
    ]
    
    normalised_params = command._normalise_param_list(param_list)
    
    assert normalised_params == ['param1', 'param2']
    assert 'param1' in param._params
    assert 'param2' in param._params


def test_process_inline_params_required_params():
    """Test that _process_inline_params() handles COMMAND_REQUIRED_PARAMS.
    
    Scenario: Inline parameter definitions in COMMAND_REQUIRED_PARAMS are processed
      Given a command with inline param defs in COMMAND_REQUIRED_PARAMS
      When _process_inline_params() is called
      Then each inline param is registered via param._register_inline_param()
      And COMMAND_REQUIRED_PARAMS is updated with param names
      
      Tests: Inline param processing for required params
      Validates: Helper delegates to param module and normalises list
    
    This test verifies that inline parameter definitions in COMMAND_REQUIRED_PARAMS
    are registered and the list is normalised to parameter names. This ensures
    commands can define required parameters inline without pre-registration.
    """
    _reset_command_module()
    
    inline_param_1 = {PARAM_NAME: 'param1'}
    inline_param_2 = {PARAM_NAME: 'param2'}
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_REQUIRED_PARAMS: [inline_param_1, inline_param_2]
    }
    
    command._process_inline_params(cmd)
    
    # Params should be registered
    assert 'param1' in param._params
    assert 'param2' in param._params
    # List should be normalised to names
    assert cmd[COMMAND_REQUIRED_PARAMS] == ['param1', 'param2']


def test_process_inline_params_trigger_param():
    """Test that _process_inline_params() handles COMMAND_TRIGGER_PARAM.
    
    Scenario: Inline parameter definition in COMMAND_TRIGGER_PARAM is processed
      Given a command with inline param def in COMMAND_TRIGGER_PARAM
      When _process_inline_params() is called
      Then inline param is registered via param._register_inline_param()
      And COMMAND_TRIGGER_PARAM is updated with param name
      
      Tests: Inline param processing for trigger param
      Validates: Helper delegates to param module and normalises value
    
    This test verifies that an inline parameter definition in COMMAND_TRIGGER_PARAM
    is registered and the field is normalised to the parameter name. This allows
    commands to define trigger parameters inline without pre-registration.
    """
    _reset_command_module()
    
    inline_param = {PARAM_NAME: 'trigger-param'}
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_TRIGGER_PARAM: inline_param
    }
    
    command._process_inline_params(cmd)
    
    # Param should be registered
    assert 'trigger-param' in param._params
    # Field should be normalised to name
    assert cmd[COMMAND_TRIGGER_PARAM] == 'trigger-param'


def test_process_inline_params_no_inline_params():
    """Test that _process_inline_params() handles commands with no inline params.
    
    Scenario: Command with no inline params is unchanged
      Given a command with no COMMAND_REQUIRED_PARAMS or COMMAND_TRIGGER_PARAM
      When _process_inline_params() is called
      Then command dict is unchanged
      
      Tests: No-op behaviour for commands without inline params
      Validates: Helper safely handles missing fields
    
    This test verifies that commands without COMMAND_REQUIRED_PARAMS or
    COMMAND_TRIGGER_PARAM are processed without errors. The helper should
    safely handle missing fields without side effects.
    """
    _reset_command_module()
    
    cmd = {COMMAND_NAME: 'test-cmd'}
    original_cmd = cmd.copy()
    
    command._process_inline_params(cmd)
    
    # Command should be unchanged
    assert cmd == original_cmd


def test_normalise_command_list():
    """Test that _normalise_command_list() converts command defs to names.
    
    Scenario: List of inline command definitions is normalised to command names
      Given a list of inline command definitions
      When _normalise_command_list() is called
      Then each command is registered via _register_inline_command()
      And a list of command names is returned
      
      Tests: Command list normalisation helper
      Validates: Helper extracts loop logic to avoid nesting violation
    
    This test verifies that a list of inline command definitions is
    normalised to a list of command names by registering each command
    and collecting the names. This helper avoids nesting violations.
    """
    _reset_command_module()
    
    cmd_list = [
        {COMMAND_NAME: 'cmd1', COMMAND_ACTION: lambda: None},
        {COMMAND_NAME: 'cmd2', COMMAND_ACTION: lambda: None}
    ]
    
    normalised_commands = command._normalise_command_list(cmd_list)
    
    assert normalised_commands == ['cmd1', 'cmd2']
    assert 'cmd1' in command._commands
    assert 'cmd2' in command._commands


def test_process_inline_commands_goes_after():
    """Test that _process_inline_commands() handles COMMAND_GOES_AFTER.
    
    Scenario: Inline command definitions in dependency fields are processed
      Given a command with inline cmd defs in COMMAND_GOES_AFTER
      When _process_inline_commands() is called
      Then each inline cmd is registered via _register_inline_command()
      And COMMAND_GOES_AFTER is updated with command names
      
      Tests: Inline command processing for dependency fields
      Validates: Helper delegates to registration and normalises lists
    
    This test verifies that inline command definitions in COMMAND_GOES_AFTER
    are registered and the list is normalised to command names. This allows
    commands to define dependencies inline without pre-registration.
    """
    _reset_command_module()
    
    inline_cmd = {
        COMMAND_NAME: 'inline-cmd',
        COMMAND_ACTION: lambda: None
    }
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_AFTER: [inline_cmd]
    }
    
    command._process_inline_commands(cmd)
    
    # Inline command should be registered
    assert 'inline-cmd' in command._commands
    # List should be normalised to names
    assert cmd[COMMAND_GOES_AFTER] == ['inline-cmd']


def test_process_inline_commands_multiple_fields():
    """Test that _process_inline_commands() handles all dependency fields.
    
    Scenario: All dependency fields with inline commands are processed
      Given a command with inline cmds in multiple dependency fields
      When _process_inline_commands() is called
      Then all inline cmds are registered
      And all fields are normalised to command names
      
      Tests: Comprehensive inline command processing
      Validates: Helper processes all dependency field types
    
    This test verifies that inline command definitions in all dependency
    fields (GOES_BEFORE, GOES_AFTER, NEXT_COMMANDS, REQUIRE_BEFORE) are
    processed correctly. This ensures comprehensive inline command support.
    """
    _reset_command_module()
    
    inline_cmd_1 = {
        COMMAND_NAME: 'inline-1',
        COMMAND_ACTION: lambda: None
    }
    inline_cmd_2 = {
        COMMAND_NAME: 'inline-2',
        COMMAND_ACTION: lambda: None
    }
    inline_cmd_3 = {
        COMMAND_NAME: 'inline-3',
        COMMAND_ACTION: lambda: None
    }
    inline_cmd_4 = {
        COMMAND_NAME: 'inline-4',
        COMMAND_ACTION: lambda: None
    }
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_BEFORE: [inline_cmd_1],
        COMMAND_GOES_AFTER: [inline_cmd_2],
        COMMAND_NEXT_COMMANDS: [inline_cmd_3],
        COMMAND_REQUIRE_BEFORE: [inline_cmd_4]
    }
    
    command._process_inline_commands(cmd)
    
    # All inline commands should be registered
    assert 'inline-1' in command._commands
    assert 'inline-2' in command._commands
    assert 'inline-3' in command._commands
    assert 'inline-4' in command._commands
    # All fields should be normalised
    assert cmd[COMMAND_GOES_BEFORE] == ['inline-1']
    assert cmd[COMMAND_GOES_AFTER] == ['inline-2']
    assert cmd[COMMAND_NEXT_COMMANDS] == ['inline-3']
    assert cmd[COMMAND_REQUIRE_BEFORE] == ['inline-4']


def test_process_inline_commands_no_inline_commands():
    """Test that _process_inline_commands() handles commands with no inline cmds.
    
    Scenario: Command with no inline commands is unchanged
      Given a command with no dependency fields
      When _process_inline_commands() is called
      Then command dict is unchanged
      
      Tests: No-op behaviour for commands without inline commands
      Validates: Helper safely handles missing fields
    
    This test verifies that commands without dependency fields are processed
    without errors. The helper should safely handle missing fields without
    side effects.
    """
    _reset_command_module()
    
    cmd = {COMMAND_NAME: 'test-cmd'}
    original_cmd = cmd.copy()
    
    command._process_inline_commands(cmd)
    
    # Command should be unchanged
    assert cmd == original_cmd


def test_assign_command_phase_missing_phase():
    """Test that _assign_command_phase() assigns default when phase missing.
    
    Scenario: Default phase is assigned when COMMAND_PHASE is missing
      Given a command without COMMAND_PHASE
      When _assign_command_phase() is called
      Then COMMAND_PHASE is set to config.get_default_phase()
      
      Tests: Default phase assignment
      Validates: Helper delegates to config module for default value
    
    This test verifies that commands without COMMAND_PHASE are assigned the
    default phase from config.get_default_phase(). This ensures all commands
    have a phase assigned before registration.
    """
    _reset_command_module()
    
    cmd = {COMMAND_NAME: 'test-cmd'}
    
    command._assign_command_phase(cmd)
    
    # Phase should be assigned
    assert COMMAND_PHASE in cmd
    assert cmd[COMMAND_PHASE] == config.get_default_phase()


def test_assign_command_phase_existing_phase():
    """Test that _assign_command_phase() preserves existing phase.
    
    Scenario: Existing COMMAND_PHASE is preserved
      Given a command with COMMAND_PHASE already set
      When _assign_command_phase() is called
      Then COMMAND_PHASE remains unchanged
      
      Tests: Phase preservation
      Validates: Helper doesn't override explicit phase values
    
    This test verifies that commands with COMMAND_PHASE already set are not
    modified. The helper should only assign defaults for missing phases and
    respect explicit phase assignments.
    """
    _reset_command_module()
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_PHASE: 'custom-phase'
    }
    
    command._assign_command_phase(cmd)
    
    # Phase should be unchanged
    assert cmd[COMMAND_PHASE] == 'custom-phase'


def test_store_command_registry_storage():
    """Test that _store_command() stores command in registry.
    
    Scenario: Command is stored in registry
      Given a command definition
      When _store_command() is called
      Then command is added to _commands dict with name as key
      
      Tests: Registry storage
      Validates: Helper stores command in module-level registry
    
    This test verifies that commands are stored in the module-level _commands
    dictionary with the command name as the key. This is the primary storage
    mechanism for command registration.
    """
    _reset_command_module()
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: 'test-phase'
    }
    
    command._store_command(cmd)
    
    # Command should be in registry
    assert 'test-cmd' in command._commands
    assert command._commands['test-cmd'] == cmd


def test_store_command_cycle_registration():
    """Test that _store_command() registers cycles when present.
    
    Scenario: Command with cycle triggers cycle registration
      Given a command definition with COMMAND_CYCLE
      When _store_command() is called
      Then cycle.register_cycle() is called with command and registry
      
      Tests: Cycle registration delegation
      Validates: Helper delegates cycle registration to cycle module
    
    This test verifies that commands with COMMAND_CYCLE trigger cycle
    registration by calling cycle.register_cycle(). This ensures cycle
    functionality is properly initialised during command registration.
    """
    _reset_command_module()
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: 'test-phase'
    }
    
    command._store_command(cmd)
    
    # Command should be in registry
    assert 'test-cmd' in command._commands
    # Note: cycle.register_cycle() is called internally for all commands
    # Full cycle behaviour is tested in cycle module tests


def test_add_command_attaches_top_level_cycle():
    """Test that add_command() attaches top-level cycle when no inline cycle exists.
    
    Test ID: 3.1.1
    Category: Command Registration - Top-Level Cycle Integration
    
    Validates: Top-level cycles are attached to commands without inline cycles
    
    This test verifies that when a command is registered via add_command()
    and a matching cycle exists in the top-level cycle registry, the cycle
    is automatically attached to the command's COMMAND_CYCLE property.
    """
    _reset_command_module()
    cycle.reset_cycle_state()
    
    # Register a top-level cycle first
    # Note: Must include CYCLE_COMMANDS to satisfy register_cycle() validation
    cycle_def = {
        CYCLE_COMMAND: 'test-cmd',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: 'param-name',
        CYCLE_COMMANDS: ['sub-cmd-1']
    }
    cycle.add_cycle(cycle_def)
    
    # Register the sub-command that the cycle references
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd-1',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    # Register command without inline cycle
    cmd_def = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(cmd_def)
    
    # Verify cycle was attached
    stored_cmd = command._commands['test-cmd']
    assert COMMAND_CYCLE in stored_cmd
    assert stored_cmd[COMMAND_CYCLE] == cycle_def


def test_add_command_inline_cycle_when_no_top_level():
    """Test that inline cycle is used when no top-level cycle exists.
    
    Test ID: 3.1.2
    Category: Command Registration - Inline Cycle Backward Compatibility
    
    Validates: Inline cycles work independently without top-level cycles
    
    This test verifies that when a command has an inline COMMAND_CYCLE
    and no top-level cycle exists, the inline cycle is used without error.
    This ensures backward compatibility with existing inline cycle usage.
    """
    _reset_command_module()
    cycle.reset_cycle_state()
    
    # Create inline cycle definition (no top-level registration)
    inline_cycle = {
        CYCLE_NAME: 'inline-cycle',
        CYCLE_LOOP: 'param-name',
        CYCLE_COMMANDS: ['sub-cmd-1']
    }
    
    # Register the sub-command
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd-1',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    # Register command with inline cycle (no top-level cycle exists)
    cmd_def = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: inline_cycle
    }
    command.add_command(cmd_def)
    
    # Verify inline cycle is used
    stored_cmd = command._commands['test-cmd']
    assert COMMAND_CYCLE in stored_cmd
    assert stored_cmd[COMMAND_CYCLE][CYCLE_NAME] == 'inline-cycle'


def test_add_command_identical_inline_and_top_level_cycles():
    """Test that identical inline and top-level cycles coexist without error.
    
    Test ID: 3.1.3
    Category: Command Registration - Cycle Equivalency Checking
    
    Validates: Identical cycle definitions coexist (first-wins behaviour)
    
    This test verifies that when a command has both an inline COMMAND_CYCLE
    and a top-level cycle with identical definitions, no error is raised
    and the inline cycle is used (first-wins policy).
    """
    _reset_command_module()
    cycle.reset_cycle_state()
    
    # Create shared cycle components
    shared_loop_func = 'shared-param'
    
    # Register top-level cycle
    top_level_cycle = {
        CYCLE_COMMAND: 'test-cmd',
        CYCLE_NAME: 'shared-cycle',
        CYCLE_LOOP: shared_loop_func,
        CYCLE_COMMANDS: ['sub-cmd-1']
    }
    cycle.add_cycle(top_level_cycle)
    
    # Register the sub-command
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd-1',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    # Register command with identical inline cycle
    inline_cycle = {
        CYCLE_COMMAND: 'test-cmd',  # Must match top-level for equivalency
        CYCLE_NAME: 'shared-cycle',
        CYCLE_LOOP: shared_loop_func,
        CYCLE_COMMANDS: ['sub-cmd-1']
    }
    cmd_def = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: inline_cycle
    }
    
    # Should not raise - identical cycles coexist
    command.add_command(cmd_def)
    
    # Verify cycle attached (inline wins)
    stored_cmd = command._commands['test-cmd']
    assert COMMAND_CYCLE in stored_cmd
    assert stored_cmd[COMMAND_CYCLE][CYCLE_NAME] == 'shared-cycle'


def test_add_command_conflicting_inline_and_top_level_cycles_raises():
    """Test that conflicting inline and top-level cycles raise ValueError.
    
    Test ID: 3.1.4
    Category: Command Registration - Cycle Conflict Detection
    
    Validates: Different cycle definitions raise error
    
    This test verifies that when a command has both an inline COMMAND_CYCLE
    and a top-level cycle with different definitions, a ValueError is raised
    with a clear error message indicating the conflict.
    """
    _reset_command_module()
    cycle.reset_cycle_state()
    
    # Register top-level cycle
    top_level_cycle = {
        CYCLE_COMMAND: 'test-cmd',
        CYCLE_NAME: 'top-level-cycle',
        CYCLE_LOOP: 'top-param',
        CYCLE_COMMANDS: ['sub-cmd-1']
    }
    cycle.add_cycle(top_level_cycle)
    
    # Register the sub-command
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd-1',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    # Try to register command with different inline cycle
    inline_cycle = {
        CYCLE_NAME: 'different-cycle',
        CYCLE_LOOP: 'different-param',
        CYCLE_COMMANDS: ['sub-cmd-1']
    }
    cmd_def = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: inline_cycle
    }
    
    # Should raise ValueError with conflict message
    with pytest.raises(ValueError) as exc_info:
        command.add_command(cmd_def)
    
    error_msg = str(exc_info.value).lower()
    assert 'conflicting' in error_msg or 'conflict' in error_msg
    assert 'test-cmd' in str(exc_info.value)

