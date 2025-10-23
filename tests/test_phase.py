from spafw37 import command as command, param
from spafw37 import config
from spafw37.config import set_config_value
from spafw37.config_consts import (
    COMMAND_GOES_BEFORE,
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_PHASE,
    COMMAND_TRIGGER_PARAM,
    PARAM_BIND_TO,
    PARAM_NAME,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_NEVER,
    PARAM_REQUIRED,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PHASE_DEFAULT,
    PHASE_EXECUTION,
    PHASE_SETUP,
    PHASE_TEARDOWN
)
import pytest
from tests.test_command import _queue_names, _reset_command_module 

def test_set_phase_order():
    """Test setting the phase order"""
    phases = [
        "phase-setup",
        "phase-execution",
        "phase-teardown"
    ]
    command._phase_order = []
    command._phases = {}
    command.set_phases_order(phases)
    assert command._phase_order == phases
    for _phase in phases:
        assert command._phases[_phase] == []

def test_command_default_phase():
    """Test that commands default to the default phase if none is specified"""
    _reset_command_module()
    default_phase = PHASE_DEFAULT
    sample_command = {
        COMMAND_NAME: "phase-default-command",
        COMMAND_ACTION: lambda: None
    }
    command.add_commands([sample_command])
    assert command._commands["phase-default-command"][COMMAND_PHASE] == default_phase

def test_command_specified_phase():
    """Test that commands can specify a phase"""
    _reset_command_module()
    specified_phase = PHASE_TEARDOWN
    sample_command = {
        COMMAND_NAME: "phase-specified-command",
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: specified_phase
    }
    command.add_commands([sample_command])
    assert command._commands["phase-specified-command"][COMMAND_PHASE] == specified_phase

def test_queued_command_added_to_correct_phase():
    """Test that queued commands are added to the correct phase queue"""
    _reset_command_module()
    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    command.set_phases_order(phases)
    _command_name = "phase-queue-command"
    sample_command = {
        COMMAND_NAME: _command_name,
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: PHASE_EXECUTION
    }
    command.add_commands([sample_command])
    command.queue_command(_command_name)
    assert command._commands[_command_name] in command._phases[PHASE_EXECUTION]

# Test that error is raised if adding to a completed phase
def test_adding_command_to_completed_phase_raises():
    _reset_command_module()
    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    command.set_phases_order(phases)
    _command_name = "completed-phase-command"
    sample_command = {
        COMMAND_NAME: _command_name,
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: PHASE_SETUP
    }
    command.add_commands([sample_command])
    command._phases_completed.append(PHASE_SETUP)
    with pytest.raises(ValueError) as excinfo:
        command.queue_command(_command_name)
    assert "Cannot add command" in str(excinfo.value)

# test that error is raised if adding to an unrecognized phase
def test_adding_command_to_unrecognized_phase_raises():
    _reset_command_module()
    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    command.set_phases_order(phases)
    _command_name = "unrecognized-phase-command"
    sample_command = {
        COMMAND_NAME: _command_name,
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: "phase-nonexistent"
    }
    command.add_commands([sample_command])
    with pytest.raises(KeyError) as excinfo:
        command.queue_command(_command_name)
    assert "Phase 'phase-nonexistent' not recognized." in str(excinfo.value)

# test that triggered commands are added to the correct phase, by setting the trigger param using config.set_config_value
def test_triggered_command_added_to_correct_phase():
    _reset_command_module()
    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    _trigger_param_name = "trigger-param"
    _trigger_param = {
        PARAM_NAME: _trigger_param_name,
        PARAM_BIND_TO: _trigger_param_name,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    param.add_params([_trigger_param])
    command.set_phases_order(phases)
    trigger_param_name = _trigger_param_name
    triggered_command_name = "triggered-phase-command"
    triggered_command = {
        COMMAND_NAME: triggered_command_name,
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: PHASE_TEARDOWN,
        COMMAND_TRIGGER_PARAM: _trigger_param_name
    }
    command.add_commands([triggered_command])
    # Set the trigger param to cause the command to be queued
    set_config_value(_trigger_param, True)
    command._recalculate_queue()
    assert command._commands[triggered_command_name] in command._phases[PHASE_TEARDOWN]

def test_sort_command_queue_by_phase():
    """Test that the command queue is sorted by phase order"""
    _reset_command_module()
    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    command.set_phases_order(phases)
    four_commands_multiseq = [
        {
            COMMAND_NAME: "cmd1",
            COMMAND_ACTION: lambda: None,
            COMMAND_PHASE: PHASE_TEARDOWN
        },
        {
            COMMAND_NAME: "cmd2",
            COMMAND_ACTION: lambda: None,
            COMMAND_PHASE: PHASE_SETUP
        },
        {
            COMMAND_NAME: "cmd3",
            COMMAND_ACTION: lambda: None,
            COMMAND_PHASE: PHASE_EXECUTION
        },
        {
            COMMAND_NAME: "cmd4",
            COMMAND_ACTION: lambda: None,
            COMMAND_PHASE: PHASE_EXECUTION
        }
    ]
    # Add commands to the module
    command.add_commands(four_commands_multiseq)
    command.queue_commands(_queue_names(four_commands_multiseq))
    command._recalculate_queue()
    assert command._commands["cmd1"] in command._phases[PHASE_TEARDOWN]
    assert command._commands["cmd2"] in command._phases[PHASE_SETUP]
    assert command._commands["cmd3"] in command._phases[PHASE_EXECUTION]
    assert command._commands["cmd4"] in command._phases[PHASE_EXECUTION]

def test_phased_goes_before_seperate_phases(): # Test that commands can have COMMAND_GOES_BEFORE commands for earlier phases
    _reset_command_module()    
    
    execution_order = []

    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    command.set_phases_order(phases)
    cmd_before_exec = {
        COMMAND_NAME: "cmd-before-exec",
        COMMAND_ACTION:  lambda: execution_order.append("cmd-before-exec"),
        COMMAND_GOES_BEFORE: ["cmd-exec"],
        COMMAND_PHASE: PHASE_SETUP
    }
    cmd_before_exec2 = {
        COMMAND_NAME: "cmd-before-exec-2",
        COMMAND_ACTION: lambda: execution_order.append("cmd-before-exec-2"),
        COMMAND_GOES_BEFORE: ["cmd-exec"],
        COMMAND_PHASE: PHASE_EXECUTION
    }
    cmd_exec = {
        COMMAND_NAME: "cmd-exec",
        COMMAND_ACTION: lambda: execution_order.append("cmd-exec"),
        COMMAND_PHASE: PHASE_EXECUTION
    }
    command.add_commands([cmd_before_exec, cmd_before_exec2, cmd_exec])
    command.queue_commands(["cmd-exec", "cmd-before-exec", "cmd-before-exec-2"])
    command.run_phased_command_queue()
    # Verify execution order
    assert execution_order == ["cmd-before-exec", "cmd-before-exec-2", "cmd-exec"]
    # Verify all commands executed
    assert len(execution_order) == 3
    # Verify cmd-before-exec-2 executed before cmd-exec
    assert execution_order.index("cmd-before-exec-2") < execution_order.index("cmd-exec")

def test_commands_execute_in_correct_phases():
    """Test that commands execute in the correct phases"""
    _reset_command_module()
    phases = [
        PHASE_SETUP,
        PHASE_EXECUTION,
        PHASE_TEARDOWN
    ]
    command.set_phases_order(phases)
    cmd_setup = {
        COMMAND_NAME: "cmd-setup",
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: PHASE_SETUP
    }
    cmd_exec = {
        COMMAND_NAME: "cmd-exec",
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: PHASE_EXECUTION
    }
    cmd_teardown = {
        COMMAND_NAME: "cmd-teardown",
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: PHASE_TEARDOWN
    }
    command.add_commands([cmd_setup, cmd_exec, cmd_teardown])
    command.queue_commands(["cmd-teardown", "cmd-setup", "cmd-exec"])
    command.run_phased_command_queue()
    assert command._phases_completed == [PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN]