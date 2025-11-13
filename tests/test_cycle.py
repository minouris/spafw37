"""
Tests for the cycle execution system.

This module tests cycle registration, validation, param collection,
command queueing, execution, and nested cycle support.
"""

import pytest
from spafw37 import cycle
from spafw37.constants.command import (
    COMMAND_CYCLE,
    COMMAND_INVOCABLE,
    COMMAND_NAME,
    COMMAND_PHASE,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_ACTION,
    COMMAND_GOES_AFTER,
    COMMAND_REQUIRE_BEFORE,
)
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.phase import PHASE_DEFAULT


@pytest.fixture(autouse=True)
def reset_state():
    """Reset cycle module state before each test.
    
    This ensures that tests are isolated from each other and do not
    share state. Runs automatically before and after each test.
    """
    cycle.reset_cycle_state()
    yield
    cycle.reset_cycle_state()


class TestCommandNameExtraction:
    """Tests for extracting command names from definitions."""
    
    def test_get_command_name_from_string(self):
        """
        Test that command name is correctly extracted from string reference.
        String references should return the string itself as the command name.
        This is expected because string references are command names.
        """
        result = cycle._get_command_name('test-command')
        assert result == 'test-command'
    
    def test_get_command_name_from_dict(self):
        """
        Test that command name is correctly extracted from dict definition.
        Dict definitions should return the value of COMMAND_NAME key.
        This is expected because dicts contain full command definitions.
        """
        cmd_def = {COMMAND_NAME: 'test-command'}
        result = cycle._get_command_name(cmd_def)
        assert result == 'test-command'
    
    def test_get_command_name_from_empty_dict(self):
        """
        Test that empty string is returned when dict has no COMMAND_NAME.
        Missing COMMAND_NAME should return empty string as default.
        This is expected to handle malformed command definitions gracefully.
        """
        cmd_def = {}
        result = cycle._get_command_name(cmd_def)
        assert result == ''


class TestCycleDetection:
    """Tests for detecting cycle definitions in commands."""
    
    def test_get_cycle_from_command_with_cycle(self):
        """
        Test that cycle definition is correctly extracted from command.
        Commands with COMMAND_CYCLE should return the cycle definition.
        This is expected because commands can have attached cycles.
        """
        cycle_def = {CYCLE_NAME: 'test-cycle'}
        cmd_def = {COMMAND_CYCLE: cycle_def}
        result = cycle._get_cycle_from_command(cmd_def)
        assert result == cycle_def
    
    def test_get_cycle_from_command_without_cycle(self):
        """
        Test that None is returned when command has no cycle.
        Commands without COMMAND_CYCLE should return None.
        This is expected because not all commands have cycles.
        """
        cmd_def = {COMMAND_NAME: 'test-command'}
        result = cycle._get_cycle_from_command(cmd_def)
        assert result is None
    
    def test_is_cycle_command_with_cycle(self):
        """
        Test that command with cycle is correctly identified.
        Commands with COMMAND_CYCLE should return True from is_cycle_command.
        This is expected to distinguish cycle commands from regular commands.
        """
        cmd_def = {COMMAND_CYCLE: {CYCLE_NAME: 'test'}}
        result = cycle._is_cycle_command(cmd_def)
        assert result is True
    
    def test_is_cycle_command_without_cycle(self):
        """
        Test that command without cycle is correctly identified.
        Commands without COMMAND_CYCLE should return False from is_cycle_command.
        This is expected to distinguish regular commands from cycle commands.
        """
        cmd_def = {COMMAND_NAME: 'test-command'}
        result = cycle._is_cycle_command(cmd_def)
        assert result is False


class TestParamCollection:
    """Tests for collecting parameters from cycle commands."""
    
    def test_collect_params_from_single_command(self):
        """
        Test that params are collected from a single cycle command.
        A cycle with one command should collect all its required params.
        This is expected to enable upfront parameter validation.
        """
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_REQUIRED_PARAMS: ['param1', 'param2']
            }
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1']
        }
        
        result = cycle._collect_cycle_params_recursive(cycle_def, commands)
        assert result == {'param1', 'param2'}
    
    def test_collect_params_from_multiple_commands(self):
        """
        Test that params are collected from multiple cycle commands.
        A cycle with multiple commands should collect params from all.
        This is expected to merge params from all cycle commands.
        """
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_REQUIRED_PARAMS: ['param1']
            },
            'cmd2': {
                COMMAND_NAME: 'cmd2',
                COMMAND_REQUIRED_PARAMS: ['param2']
            }
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        result = cycle._collect_cycle_params_recursive(cycle_def, commands)
        assert result == {'param1', 'param2'}
    
    def test_collect_params_removes_duplicates(self):
        """
        Test that duplicate params across commands are deduplicated.
        Multiple commands with same param should only include it once.
        This is expected to avoid redundant parameter validation.
        """
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_REQUIRED_PARAMS: ['param1']
            },
            'cmd2': {
                COMMAND_NAME: 'cmd2',
                COMMAND_REQUIRED_PARAMS: ['param1', 'param2']
            }
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        result = cycle._collect_cycle_params_recursive(cycle_def, commands)
        assert result == {'param1', 'param2'}
    
    def test_collect_params_from_inline_command(self):
        """
        Test that params are collected from inline command definition.
        Inline command defs should have their params collected like refs.
        This is expected to support both reference and inline command styles.
        """
        commands = {}
        cycle_def = {
            CYCLE_COMMANDS: [
                {
                    COMMAND_NAME: 'inline-cmd',
                    COMMAND_REQUIRED_PARAMS: ['param1']
                }
            ]
        }
        
        result = cycle._collect_cycle_params_recursive(cycle_def, commands)
        assert result == {'param1'}
    
    def test_collect_params_fails_for_missing_command(self):
        """
        Test that collection fails when referenced command doesn't exist.
        String references to non-existent commands should raise error.
        This is expected to catch configuration errors early.
        """
        commands = {}
        cycle_def = {
            CYCLE_COMMANDS: ['nonexistent']
        }
        
        with pytest.raises(cycle.CycleValidationError) as exc_info:
            cycle._collect_cycle_params_recursive(cycle_def, commands)
        
        assert 'not found' in str(exc_info.value)
    
    def test_collect_params_from_nested_cycle(self):
        """
        Test that params are recursively collected from nested cycles.
        A cycle containing another cycle should collect all nested params.
        This is expected to support nested cycle param validation.
        """
        commands = {
            'inner-cmd': {
                COMMAND_NAME: 'inner-cmd',
                COMMAND_REQUIRED_PARAMS: ['inner-param']
            },
            'outer-cmd': {
                COMMAND_NAME: 'outer-cmd',
                COMMAND_REQUIRED_PARAMS: ['outer-param'],
                COMMAND_CYCLE: {
                    CYCLE_NAME: 'inner-cycle',
                    CYCLE_LOOP: lambda: False,
                    CYCLE_COMMANDS: ['inner-cmd']
                }
            }
        }
        cycle_def = {
            CYCLE_COMMANDS: ['outer-cmd']
        }
        
        result = cycle._collect_cycle_params_recursive(cycle_def, commands)
        assert result == {'outer-param', 'inner-param'}
    
    def test_collect_params_fails_on_deep_nesting(self):
        """
        Test that collection fails when nesting depth exceeds maximum.
        Deeply nested cycles beyond limit should raise validation error.
        This is expected to prevent infinite recursion and stack overflow.
        """
        # Create deeply nested cycle structure
        commands = {}
        for depth_index in range(10):
            cmd_name = 'cmd{}'.format(depth_index)
            commands[cmd_name] = {
                COMMAND_NAME: cmd_name,
                COMMAND_REQUIRED_PARAMS: ['param{}'.format(depth_index)]
            }
            
            if depth_index < 9:
                next_cmd = 'cmd{}'.format(depth_index + 1)
                commands[cmd_name][COMMAND_CYCLE] = {
                    CYCLE_NAME: 'cycle{}'.format(depth_index),
                    CYCLE_LOOP: lambda: False,
                    CYCLE_COMMANDS: [next_cmd]
                }
        
        cycle_def = {
            CYCLE_COMMANDS: ['cmd0']
        }
        
        with pytest.raises(cycle.CycleValidationError) as exc_info:
            cycle._collect_cycle_params_recursive(cycle_def, commands)
        
        assert 'nesting depth exceeds' in str(exc_info.value).lower()


class TestPhaseValidation:
    """Tests for validating phase consistency in cycles."""
    
    def test_validate_same_phase_passes(self):
        """
        Test that validation passes when all commands in same phase.
        Cycle commands in same phase as parent should pass validation.
        This is expected because cycles require phase consistency.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1', COMMAND_PHASE: 'setup'},
            'cmd2': {COMMAND_NAME: 'cmd2', COMMAND_PHASE: 'setup'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        # Should not raise
        cycle._validate_cycle_phase_consistency(
            cycle_def, commands, 'setup'
        )
    
    def test_validate_default_phase_passes(self):
        """
        Test that validation passes when commands use default phase.
        Commands without explicit phase should use default and pass.
        This is expected because default phase is valid for cycles.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'},
            'cmd2': {COMMAND_NAME: 'cmd2'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        # Should not raise
        cycle._validate_cycle_phase_consistency(
            cycle_def, commands, PHASE_DEFAULT
        )
    
    def test_validate_different_phase_fails(self):
        """
        Test that validation fails when command has different phase.
        Cycle commands in different phase from parent should fail.
        This is expected to enforce phase consistency within cycles.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1', COMMAND_PHASE: 'execution'},
        }
        cycle_def = {
            CYCLE_NAME: 'test-cycle',
            CYCLE_COMMANDS: ['cmd1']
        }
        
        with pytest.raises(cycle.CycleValidationError) as exc_info:
            cycle._validate_cycle_phase_consistency(
                cycle_def, commands, 'setup'
            )
        
        assert 'phase' in str(exc_info.value)


class TestCommandInvocability:
    """Tests for marking cycle commands as not invocable."""
    
    def test_mark_single_command_not_invocable(self):
        """
        Test that single cycle command is marked not invocable.
        Cycle commands should have COMMAND_INVOCABLE set to False.
        This is expected to prevent direct CLI invocation of cycle commands.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1']
        }
        
        cycle._mark_cycle_commands_not_invocable(cycle_def, commands)
        
        assert commands['cmd1'][COMMAND_INVOCABLE] is False
    
    def test_mark_multiple_commands_not_invocable(self):
        """
        Test that multiple cycle commands are marked not invocable.
        All commands in cycle should have COMMAND_INVOCABLE set to False.
        This is expected to prevent direct CLI invocation of any cycle command.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'},
            'cmd2': {COMMAND_NAME: 'cmd2'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        cycle._mark_cycle_commands_not_invocable(cycle_def, commands)
        
        assert commands['cmd1'][COMMAND_INVOCABLE] is False
        assert commands['cmd2'][COMMAND_INVOCABLE] is False
    
    def test_mark_nested_cycle_commands_not_invocable(self):
        """
        Test that nested cycle commands are recursively marked not invocable.
        Commands in nested cycles should also be marked not invocable.
        This is expected to prevent invocation at any nesting level.
        """
        commands = {
            'inner-cmd': {COMMAND_NAME: 'inner-cmd'},
            'outer-cmd': {
                COMMAND_NAME: 'outer-cmd',
                COMMAND_CYCLE: {
                    CYCLE_COMMANDS: ['inner-cmd']
                }
            }
        }
        cycle_def = {
            CYCLE_COMMANDS: ['outer-cmd']
        }
        
        cycle._mark_cycle_commands_not_invocable(cycle_def, commands)
        
        assert commands['outer-cmd'][COMMAND_INVOCABLE] is False
        assert commands['inner-cmd'][COMMAND_INVOCABLE] is False
    
    def test_is_command_invocable_returns_true_by_default(self):
        """
        Test that commands are invocable by default.
        Regular commands without COMMAND_INVOCABLE should return True.
        This is expected because most commands are directly invocable.
        """
        cmd_def = {COMMAND_NAME: 'test'}
        result = cycle.is_command_invocable(cmd_def)
        assert result is True
    
    def test_is_command_invocable_respects_false_flag(self):
        """
        Test that COMMAND_INVOCABLE=False is respected.
        Commands explicitly marked not invocable should return False.
        This is expected to honor the invocability flag.
        """
        cmd_def = {COMMAND_NAME: 'test', COMMAND_INVOCABLE: False}
        result = cycle.is_command_invocable(cmd_def)
        assert result is False


class TestCycleRegistration:
    """Tests for registering cycles with commands."""
    
    def test_register_cycle_merges_params(self):
        """
        Test that cycle registration merges params into parent command.
        Parent command should have all cycle command params after registration.
        This is expected to enable upfront parameter validation.
        """
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_REQUIRED_PARAMS: ['param1']
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_REQUIRED_PARAMS: ['parent-param'],
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        cycle.register_cycle(parent_cmd, commands)
        
        assert set(parent_cmd[COMMAND_REQUIRED_PARAMS]) == {
            'parent-param', 'param1'
        }
    
    def test_register_cycle_stores_cycle_definition(self):
        """
        Test that cycle registration stores cycle definition in module state.
        Registered cycles should be stored for later retrieval.
        This is expected to allow cycle lookup by command name.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'}
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        cycle.register_cycle(parent_cmd, commands)
        
        # Cycle definition should be stored on the command itself
        assert COMMAND_CYCLE in parent_cmd
        assert parent_cmd[COMMAND_CYCLE][CYCLE_NAME] == 'test-cycle'
    
    def test_register_cycle_marks_commands_not_invocable(self):
        """
        Test that cycle registration marks commands as not invocable.
        Cycle commands should not be directly invocable after registration.
        This is expected to prevent CLI invocation of cycle commands.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'}
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        cycle.register_cycle(parent_cmd, commands)
        
        assert commands['cmd1'][COMMAND_INVOCABLE] is False
    
    def test_register_cycle_fails_without_loop_function(self):
        """
        Test that cycle registration fails without loop function.
        Cycles must have CYCLE_LOOP function defined.
        This is expected because loop function is required for cycles.
        """
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_COMMANDS: []
            }
        }
        
        with pytest.raises(cycle.CycleValidationError) as exc_info:
            cycle.register_cycle(parent_cmd, commands)
        
        assert CYCLE_LOOP in str(exc_info.value)
    
    def test_register_cycle_fails_without_commands(self):
        """
        Test that cycle registration fails without commands.
        Cycles must have at least one command in CYCLE_COMMANDS.
        This is expected because empty cycles have no purpose.
        """
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False
            }
        }
        
        with pytest.raises(cycle.CycleValidationError) as exc_info:
            cycle.register_cycle(parent_cmd, commands)
        
        assert 'no commands' in str(exc_info.value)
    
    def test_register_cycle_validates_phase_consistency(self):
        """
        Test that cycle registration validates phase consistency.
        Registration should fail if cycle commands have different phases.
        This is expected to enforce phase consistency requirement.
        """
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_PHASE: 'execution'
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_PHASE: 'setup',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        with pytest.raises(cycle.CycleValidationError) as exc_info:
            cycle.register_cycle(parent_cmd, commands)
        
        assert 'phase' in str(exc_info.value)
    
    def test_register_cycle_skips_if_no_cycle(self):
        """
        Test that registration does nothing for commands without cycles.
        Commands without COMMAND_CYCLE should be unchanged by registration.
        This is expected to allow safe registration of any command.
        """
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_REQUIRED_PARAMS: ['param1']
        }
        
        cycle.register_cycle(parent_cmd, commands)
        
        # Should not modify command
        assert parent_cmd[COMMAND_REQUIRED_PARAMS] == ['param1']
        # Cycle should not be added if not present originally
        assert COMMAND_CYCLE not in parent_cmd


class TestCycleQueueBuilding:
    """Tests for building execution queues for cycles."""
    
    def test_build_queue_with_single_command(self):
        """
        Test that queue is built for single cycle command.
        A cycle with one command should create a queue with that command.
        This is expected to enable command execution from the queue.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1']
        }
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def[COMMAND_NAME])
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        result = cycle._build_cycle_queue(
            cycle_def, commands, mock_queue_add, mock_sort
        )
        
        assert result == ['cmd1']
    
    def test_build_queue_with_multiple_commands(self):
        """
        Test that queue is built for multiple cycle commands.
        A cycle with multiple commands should queue all of them.
        This is expected to execute all cycle commands in order.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'},
            'cmd2': {COMMAND_NAME: 'cmd2'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def[COMMAND_NAME])
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        result = cycle._build_cycle_queue(
            cycle_def, commands, mock_queue_add, mock_sort
        )
        
        assert result == ['cmd1', 'cmd2']
    
    def test_build_queue_uses_sort_function(self):
        """
        Test that queue building uses provided sort function.
        The sort function should be called to order commands correctly.
        This is expected to respect command dependencies and ordering.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'},
            'cmd2': {COMMAND_NAME: 'cmd2'}
        }
        cycle_def = {
            CYCLE_COMMANDS: ['cmd1', 'cmd2']
        }
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def[COMMAND_NAME])
        
        def mock_sort(queue, cmd_dict):
            # Reverse the queue to verify sort is called
            return list(reversed(queue))
        
        result = cycle._build_cycle_queue(
            cycle_def, commands, mock_queue_add, mock_sort
        )
        
        assert result == ['cmd2', 'cmd1']


class TestCycleExecution:
    """Tests for executing command cycles."""
    
    def test_execute_cycle_runs_init_function(self):
        """
        Test that cycle execution runs initialization function.
        CYCLE_INIT function should be called before loop starts.
        This is expected to allow setup before cycle commands run.
        """
        init_called = []
        
        def init_func():
            init_called.append(True)
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_INIT: init_func,
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: []
            }
        }
        
        def mock_run(cmd_def):
            pass
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            pass
        
        def mock_sort(queue, cmd_dict):
            return []
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert len(init_called) == 1
    
    def test_execute_cycle_runs_loop_until_false(self):
        """
        Test that cycle execution loops while condition returns True.
        CYCLE_LOOP should be called each iteration until it returns False.
        This is expected to control the number of cycle iterations.
        """
        iteration_count = [0]
        max_iterations = 3
        
        def loop_func():
            iteration_count[0] += 1
            return iteration_count[0] < max_iterations
        
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'}
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        run_count = [0]
        
        def mock_run(cmd_def):
            run_count[0] += 1
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def[COMMAND_NAME])
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        # Loop condition called 3 times, first 2 return True
        assert iteration_count[0] == 3
        # Commands run 2 times (when loop returns True)
        assert run_count[0] == 2
    
    def test_execute_cycle_runs_end_function(self):
        """
        Test that cycle execution runs finalization function.
        CYCLE_END function should be called after loop completes.
        This is expected to allow cleanup after all iterations.
        """
        end_called = []
        
        def end_func():
            end_called.append(True)
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_END: end_func,
                CYCLE_COMMANDS: []
            }
        }
        
        def mock_run(cmd_def):
            pass
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            pass
        
        def mock_sort(queue, cmd_dict):
            return []
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert len(end_called) == 1
    
    def test_execute_cycle_runs_commands_in_order(self):
        """
        Test that cycle execution runs commands in queue order.
        Commands should be executed in the order returned by queue builder.
        This is expected to respect command dependencies and ordering.
        """
        execution_order = []
        
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'},
            'cmd2': {COMMAND_NAME: 'cmd2'}
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: len(execution_order) == 0,
                CYCLE_COMMANDS: ['cmd1', 'cmd2']
            }
        }
        
        def mock_run(cmd_def):
            execution_order.append(cmd_def[COMMAND_NAME])
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def[COMMAND_NAME])
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert execution_order == ['cmd1', 'cmd2']
    
    def test_execute_cycle_handles_nested_cycles(self):
        """
        Test that cycle execution handles nested cycles correctly.
        A cycle command with its own cycle should execute recursively.
        This is expected to support nested cycle structures.
        """
        execution_order = []
        
        commands = {
            'inner-cmd': {
                COMMAND_NAME: 'inner-cmd',
                COMMAND_ACTION: lambda: execution_order.append('inner')
            },
            'outer-cmd': {
                COMMAND_NAME: 'outer-cmd',
                COMMAND_CYCLE: {
                    CYCLE_NAME: 'inner-cycle',
                    CYCLE_LOOP: lambda: len(execution_order) == 0,
                    CYCLE_COMMANDS: ['inner-cmd']
                }
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'outer-cycle',
                CYCLE_LOOP: lambda: len(execution_order) == 0,
                CYCLE_COMMANDS: ['outer-cmd']
            }
        }
        
        def mock_run(cmd_def):
            action = cmd_def.get(COMMAND_ACTION)
            if action:
                action()
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def[COMMAND_NAME])
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert 'inner' in execution_order
    
    def test_execute_cycle_tracks_active_cycle(self):
        """
        Test that cycle execution tracks currently active cycle.
        get_active_cycle should return current cycle name during execution.
        This is expected to support nested cycle tracking and debugging.
        """
        active_during_execution = []
        
        def loop_func():
            active_during_execution.append(cycle.get_active_cycle())
            return False
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_COMMANDS: []
            }
        }
        
        def mock_run(cmd_def):
            pass
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            pass
        
        def mock_sort(queue, cmd_dict):
            return []
        
        assert cycle.get_active_cycle() is None
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert active_during_execution[0] == 'test-cycle'
        assert cycle.get_active_cycle() is None
    
    def test_execute_cycle_skips_if_no_cycle(self):
        """
        Test that execution does nothing for commands without cycles.
        Commands without COMMAND_CYCLE should not trigger execution.
        This is expected to allow safe execution call on any command.
        """
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent'
        }
        
        run_called = []
        
        def mock_run(cmd_def):
            run_called.append(True)
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            pass
        
        def mock_sort(queue, cmd_dict):
            return []
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert len(run_called) == 0
    
    def test_execute_cycle_runs_loop_start_function(self):
        """
        Test that CYCLE_LOOP_START function runs after CYCLE_LOOP returns True.
        The loop start function should execute before commands each iteration.
        This is expected to support data preparation separated from loop condition.
        """
        loop_start_calls = []
        iteration_count = [0]
        
        def loop_func():
            iteration_count[0] += 1
            return iteration_count[0] <= 2
        
        def loop_start_func():
            loop_start_calls.append(iteration_count[0])
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_START: loop_start_func,
                CYCLE_COMMANDS: []
            }
        }
        
        def mock_run(cmd_def):
            pass
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            pass
        
        def mock_sort(queue, cmd_dict):
            return []
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert len(loop_start_calls) == 2
        assert loop_start_calls == [1, 2]


class TestCycleCommandRetrieval:
    """Tests for retrieving cycle command lists."""
    
    def test_get_cycle_commands_returns_command_list(self):
        """
        Test that get_cycle_commands returns list of command names.
        Registered cycles should return their command list by parent name.
        This is expected to support help display and introspection.
        """
        commands = {
            'cmd1': {COMMAND_NAME: 'cmd1'},
            'cmd2': {COMMAND_NAME: 'cmd2'}
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: ['cmd1', 'cmd2']
            }
        }
        
        cycle.register_cycle(parent_cmd, commands)
        
        result = cycle.get_cycle_commands(parent_cmd)
        assert result == ['cmd1', 'cmd2']
    
    def test_get_cycle_commands_returns_empty_for_nonexistent(self):
        """
        Test that get_cycle_commands returns empty list for unknown command.
        Commands without registered cycles should return empty list.
        This is expected to handle queries for non-cycle commands gracefully.
        """
        result = cycle.get_cycle_commands('nonexistent')
        assert result == []
    
    def test_get_cycle_commands_handles_inline_definitions(self):
        """
        Test that get_cycle_commands extracts names from inline commands.
        Inline command definitions should have their names extracted.
        This is expected to support both reference and inline command styles.
        """
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: lambda: False,
                CYCLE_COMMANDS: [
                    {COMMAND_NAME: 'inline-cmd'}
                ]
            }
        }
        
        cycle.register_cycle(parent_cmd, commands)
        
        result = cycle.get_cycle_commands(parent_cmd)
        assert result == ['inline-cmd']
    
    def test_validate_phase_with_missing_command_reference(self):
        """Test phase validation skips missing command references.
        
        When validating phase consistency, if a command reference (string)
        doesn't exist in commands_dict, validation should skip it rather than
        fail. This covers the continue statement on line 165.
        """
        from spafw37.constants.command import COMMAND_PHASE
        from spafw37.constants.phase import PHASE_SETUP
        
        cycle_def = {
            CYCLE_NAME: 'test-cycle',
            CYCLE_COMMANDS: ['nonexistent-command']
        }
        commands = {}
        
        # Should not raise an error despite missing command
        cycle._validate_cycle_phase_consistency(cycle_def, commands, PHASE_SETUP)
    
    def test_mark_not_invocable_skips_missing_command_reference(self):
        """Test marking commands not invocable skips missing references.
        
        When marking cycle commands as not invocable, if a command reference
        (string) doesn't exist in commands_dict, it should be skipped. This
        covers the continue statement on line 199.
        """
        cycle_def = {
            CYCLE_NAME: 'test-cycle',
            CYCLE_LOOP: lambda: False,
            CYCLE_COMMANDS: ['nonexistent-command']
        }
        commands = {}
        
        # Should not raise an error despite missing command
        cycle._mark_cycle_commands_not_invocable(cycle_def, commands)
    
    def test_execute_cycle_iteration_fails_for_missing_command(self):
        """Test cycle iteration raises error when command not found.
        
        During cycle execution, if a command name in the queue doesn't exist
        in commands_dict, a CycleExecutionError should be raised. This covers
        the error path on line 320.
        """
        command_names = ['nonexistent-command']
        commands = {}
        
        def mock_run_command(cmd_def, commands_dict):
            pass
        
        def mock_queue_add(cmd_def, queue_list, commands_dict):
            pass
        
        def mock_sort_queue(queue_list, commands_dict):
            return queue_list
        
        # Should raise CycleExecutionError for missing command
        try:
            cycle._execute_cycle_iteration(
                command_names, commands, mock_run_command,
                mock_queue_add, mock_sort_queue
            )
            assert False, "Should have raised CycleExecutionError"
        except cycle.CycleExecutionError as error:
            assert 'Command not found' in str(error)
            assert 'nonexistent-command' in str(error)
