"""
Tests for the cycle execution system.

This module tests cycle registration, validation, param collection,
command queueing, execution, and nested cycle support.
"""

import pytest
from spafw37 import command, cycle
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
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
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


def test_add_cycle_module_level_storage_initialised():
    """Test that module-level _cycles storage is initialised.
    
    Scenario: Module-level _cycles dict exists
      Given the cycle module is imported
      When the module is loaded
      Then _cycles dict should exist at module level
      And _cycles dict should be empty initially
    
    This test verifies that the _cycles dictionary exists at module level
    and is initially empty when the module is first imported.
    This behaviour is expected because cycles are registered dynamically at runtime.
    """
    assert hasattr(cycle, '_cycles')
    assert isinstance(cycle._cycles, dict)
    assert len(cycle._cycles) == 0


def test_extract_command_name_from_string():
    """Test that _extract_command_name returns string unchanged.
    
    Scenario: Extract command name from string
      Given a command name as string
      When _extract_command_name is called
      Then it should return the string unchanged
    
    This test verifies that when a command name is provided as a string,
    the function returns it unchanged.
    This behaviour is expected for command name references.
    """
    result = cycle._extract_command_name('my-command')
    
    assert result == 'my-command'


def test_extract_command_name_from_dict():
    """Test that _extract_command_name extracts name from inline definition.
    
    Scenario: Extract command name from inline definition
      Given an inline command definition dict with COMMAND_NAME
      When _extract_command_name is called
      Then it should return the COMMAND_NAME value
    
    This test verifies that when an inline command definition (dict) is provided,
    the function extracts and returns the COMMAND_NAME field.
    This behaviour is expected for inline command definitions.
    """
    inline_command = {
        COMMAND_NAME: 'inline-cmd',
        COMMAND_ACTION: lambda: None
    }
    
    result = cycle._extract_command_name(inline_command)
    
    assert result == 'inline-cmd'


def test_extract_command_name_validates_dict_has_command_name():
    """Test that _extract_command_name validates COMMAND_NAME in dict.
    
    Scenario: Inline definition missing COMMAND_NAME
      Given an inline command definition dict without COMMAND_NAME
      When _extract_command_name is called
      Then ValueError should be raised
      And error message should indicate missing COMMAND_NAME
    
    This test verifies that when an inline command definition (dict) is missing
    the required COMMAND_NAME field, a ValueError is raised.
    This behaviour is expected to catch malformed inline definitions.
    """
    invalid_inline_command = {
        COMMAND_ACTION: lambda: None
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._extract_command_name(invalid_inline_command)
    
    assert 'COMMAND_NAME' in str(exc_info.value)


def test_validate_cycle_required_fields_accepts_valid_cycle():
    """Test that _validate_cycle_required_fields accepts a valid cycle.
    
    Scenario: Valid cycle passes validation
      Given a cycle definition with all required fields
      When _validate_cycle_required_fields is called
      Then no exception should be raised
    
    This test verifies that when a cycle definition contains all required fields,
    the validation function does not raise any exceptions.
    This behaviour is expected because valid cycles should pass validation.
    """
    valid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle._validate_cycle_required_fields(valid_cycle)


def test_validate_cycle_required_fields_rejects_missing_cycle_command():
    """Test that _validate_cycle_required_fields rejects missing CYCLE_COMMAND.
    
    Scenario: Missing CYCLE_COMMAND field rejected
      Given a cycle definition without CYCLE_COMMAND
      When _validate_cycle_required_fields is called
      Then ValueError should be raised
      And error message should mention CYCLE_COMMAND
    
    This test verifies that when a cycle definition is missing the CYCLE_COMMAND
    field, the validation function raises a ValueError with an appropriate message.
    This behaviour is expected because CYCLE_COMMAND is a required field.
    """
    invalid_cycle = {
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._validate_cycle_required_fields(invalid_cycle)
    
    assert 'CYCLE_COMMAND' in str(exc_info.value)


def test_validate_cycle_required_fields_rejects_missing_cycle_name():
    """Test that _validate_cycle_required_fields rejects missing CYCLE_NAME.
    
    Scenario: Missing CYCLE_NAME field rejected
      Given a cycle definition without CYCLE_NAME
      When _validate_cycle_required_fields is called
      Then ValueError should be raised
      And error message should mention CYCLE_NAME
    
    This test verifies that when a cycle definition is missing the CYCLE_NAME
    field, the validation function raises a ValueError with an appropriate message.
    This behaviour is expected because CYCLE_NAME is a required field.
    """
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._validate_cycle_required_fields(invalid_cycle)
    
    assert 'CYCLE_NAME' in str(exc_info.value)


def test_validate_cycle_required_fields_rejects_missing_cycle_loop():
    """Test that _validate_cycle_required_fields rejects missing CYCLE_LOOP.
    
    Scenario: Missing CYCLE_LOOP field rejected
      Given a cycle definition without CYCLE_LOOP
      When _validate_cycle_required_fields is called
      Then ValueError should be raised
      And error message should mention CYCLE_LOOP
    
    This test verifies that when a cycle definition is missing the CYCLE_LOOP
    field, the validation function raises a ValueError with an appropriate message.
    This behaviour is expected because CYCLE_LOOP is a required field.
    """
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle'
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._validate_cycle_required_fields(invalid_cycle)
    
    assert 'CYCLE_LOOP' in str(exc_info.value)


def test_cycles_are_equivalent_returns_true_for_identical_cycles():
    """Test that _cycles_are_equivalent returns True for identical cycles.
    
    Scenario: Identical cycles are equivalent
      Given two cycle definitions with identical properties
      When _cycles_are_equivalent is called
      Then it should return True
    
    This test verifies that when two cycle definitions have exactly the same
    properties and values, the equivalency function returns True.
    This behaviour is expected for detecting duplicate registrations.
    """
    loop_func = lambda: True
    init_func = lambda: None
    
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_func,
        CYCLE_INIT: init_func
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_func,
        CYCLE_INIT: init_func
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is True


def test_cycles_are_equivalent_returns_false_for_different_required_fields():
    """Test that _cycles_are_equivalent returns False for different required fields.
    
    Scenario: Cycles with different required fields are not equivalent
      Given two cycle definitions with different CYCLE_NAME
      When _cycles_are_equivalent is called
      Then it should return False
    
    This test verifies that when two cycle definitions differ in a required field
    like CYCLE_NAME, the equivalency function returns False.
    This behaviour is expected to detect conflicting cycle definitions.
    """
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'cycle-one',
        CYCLE_LOOP: lambda: True
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'cycle-two',
        CYCLE_LOOP: lambda: True
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is False


def test_cycles_are_equivalent_returns_false_for_different_optional_fields():
    """Test that _cycles_are_equivalent returns False for different optional fields.
    
    Scenario: Cycles with different optional fields are not equivalent
      Given two cycles, one with CYCLE_INIT and one without
      When _cycles_are_equivalent is called
      Then it should return False
    
    This test verifies that when two cycle definitions differ in optional fields,
    the equivalency function returns False.
    This behaviour is expected because all properties must match for equivalency.
    """
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_INIT: lambda: None
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is False


def test_cycles_are_equivalent_compares_function_references():
    """Test that _cycles_are_equivalent compares function object identity.
    
    Scenario: Cycles with different function objects are not equivalent
      Given two cycles with different CYCLE_LOOP function objects
      When _cycles_are_equivalent is called
      Then it should return False
    
    This test verifies that when two cycle definitions have different function
    objects (even if they do the same thing), equivalency returns False.
    This behaviour is expected because function identity matters for cycles.
    """
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is False


def test_cycle_commands_match_with_same_string():
    """Test that two string command references with same name match.
    
    Scenario: Two string command references with same name match
      Given two CYCLE_COMMAND values both as string 'my-command'
      When _cycle_commands_match is called
      Then it should return True
    
    This test verifies that the helper correctly identifies two string command
    references as matching when they have the same name.
    
    This behaviour is expected to ensure string-to-string comparison works.
    """
    commands_match = cycle._cycle_commands_match('my-command', 'my-command')
    
    assert commands_match is True


def test_cycle_commands_match_with_string_and_dict_same_command():
    """Test that string and dict command references with same name match.
    
    Scenario: String and dict command references with same name match
      Given CYCLE_COMMAND as string 'my-command'
      And CYCLE_COMMAND as dict {COMMAND_NAME: 'my-command'}
      When _cycle_commands_match is called
      Then it should return True
    
    This test verifies that the helper normalises both string and dict formats
    and correctly identifies them as matching when they reference the same command.
    
    This behaviour is expected to support semantic equivalence across formats.
    """
    string_ref = 'my-command'
    dict_ref = {COMMAND_NAME: 'my-command'}
    
    commands_match = cycle._cycle_commands_match(string_ref, dict_ref)
    
    assert commands_match is True


def test_cycle_commands_match_with_different_commands():
    """Test that command references with different names do not match.
    
    Scenario: Command references with different names do not match
      Given CYCLE_COMMAND as string 'command-one'
      And CYCLE_COMMAND as dict {COMMAND_NAME: 'command-two'}
      When _cycle_commands_match is called
      Then it should return False
    
    This test verifies that the helper correctly identifies command references
    as non-matching when they refer to different command names.
    
    This behaviour is expected to prevent false positives in equivalence checking.
    """
    string_ref = 'command-one'
    dict_ref = {COMMAND_NAME: 'command-two'}
    
    commands_match = cycle._cycle_commands_match(string_ref, dict_ref)
    
    assert commands_match is False


def test_cycles_are_equivalent_normalizes_string_vs_dict_same_command():
    """Test that string and dict CYCLE_COMMAND with same name are equivalent.
    
    Scenario: String and dict CYCLE_COMMAND with same command name are equivalent
      Given a cycle with CYCLE_COMMAND as string 'my-command'
      And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
      And both cycles have identical CYCLE_NAME and CYCLE_LOOP
      When _cycles_are_equivalent is called with both cycles
      Then it should return True
    
    This test verifies that _cycles_are_equivalent normalises CYCLE_COMMAND values
    before comparison, recognising a string reference and inline dict definition as
    equivalent when they reference the same command name.
    
    This behaviour is expected because the framework should support semantic
    equivalence regardless of CYCLE_COMMAND format.
    """
    loop_function = lambda: True
    
    cycle_with_string = {
        CYCLE_COMMAND: 'my-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle_with_dict = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle_with_string, cycle_with_dict)
    
    assert are_equivalent is True


def test_cycles_are_equivalent_normalizes_dict_vs_string_same_command():
    """Test that dict and string CYCLE_COMMAND with same name are equivalent.
    
    Scenario: Dict and string CYCLE_COMMAND with same command name are equivalent (order reversed)
      Given a cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
      And another cycle with CYCLE_COMMAND as string 'my-command'
      And both cycles have identical CYCLE_NAME and CYCLE_LOOP
      When _cycles_are_equivalent is called with both cycles
      Then it should return True
    
    This test verifies that the normalisation is symmetric - it works correctly
    regardless of which cycle has the string format and which has the dict format.
    
    This behaviour is expected because equality should be commutative.
    """
    loop_function = lambda: True
    
    cycle_with_dict = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle_with_string = {
        CYCLE_COMMAND: 'my-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle_with_dict, cycle_with_string)
    
    assert are_equivalent is True


def test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands():
    """Test that string and dict CYCLE_COMMAND with different names are not equivalent.
    
    Scenario: String and dict CYCLE_COMMAND with different command names are not equivalent
      Given a cycle with CYCLE_COMMAND as string 'command-one'
      And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'command-two'}
      And both cycles have identical CYCLE_NAME and CYCLE_LOOP
      When _cycles_are_equivalent is called with both cycles
      Then it should return False
    
    This test verifies that normalisation still correctly identifies cycles with
    different command names as non-equivalent, even when comparing mixed formats.
    
    This behaviour is expected because semantically different cycles should not
    be treated as equivalent.
    """
    loop_function = lambda: True
    
    cycle_with_string = {
        CYCLE_COMMAND: 'command-one',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle_with_dict = {
        CYCLE_COMMAND: {COMMAND_NAME: 'command-two'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle_with_string, cycle_with_dict)
    
    assert are_equivalent is False


def test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command():
    """Test that two dict CYCLE_COMMAND values with same name are equivalent.
    
    Scenario: Two dict CYCLE_COMMAND values with same command name are equivalent (regression)
      Given a cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
      And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
      And both cycles have identical CYCLE_NAME and CYCLE_LOOP
      When _cycles_are_equivalent is called with both cycles
      Then it should return True
    
    This test verifies that dict-to-dict comparison continues to work correctly
    after adding normalisation logic.
    
    This behaviour is expected as a regression test to confirm existing functionality
    is preserved.
    """
    loop_function = lambda: True
    
    cycle1 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle2 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle1, cycle2)
    
    assert are_equivalent is True


def test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands():
    """Test that two dict CYCLE_COMMAND values with different names are not equivalent.
    
    Scenario: Two dict CYCLE_COMMAND values with different command names are not equivalent (regression)
      Given a cycle with CYCLE_COMMAND as inline dict {'command-name': 'command-one'}
      And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'command-two'}
      And both cycles have identical CYCLE_NAME and CYCLE_LOOP
      When _cycles_are_equivalent is called with both cycles
      Then it should return False
    
    This test verifies that dict-to-dict comparison correctly detects different
    command names after adding normalisation logic.
    
    This behaviour is expected as a regression test to confirm existing functionality
    is preserved.
    """
    loop_function = lambda: True
    
    cycle1 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'command-one'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle2 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'command-two'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle1, cycle2)
    
    assert are_equivalent is False


def test_add_cycle_registers_single_cycle():
    """Test that add_cycle() registers a single cycle definition.
    
    Scenario: Register single cycle via add_cycle()
      Given a valid cycle definition with CYCLE_COMMAND and CYCLE_NAME
      When add_cycle() is called with the cycle dict
      Then the cycle should be stored in _cycles indexed by command name
      And no exceptions should be raised
    
    This test verifies that when a valid cycle definition is passed to add_cycle(),
    it is stored in the _cycles dictionary indexed by the command name.
    This behaviour is expected because cycles must be associated with specific commands.
    """
    test_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle.add_cycle(test_cycle)
    
    assert 'test-command' in cycle._cycles
    assert cycle._cycles['test-command'] == test_cycle


def test_add_cycle_with_inline_cycle_command_definition():
    """Test that add_cycle() handles inline CYCLE_COMMAND definitions.
    
    This test verifies that when CYCLE_COMMAND is provided as a dict
    (inline command definition) rather than a string, the command is
    registered and the cycle is stored correctly.
    This behaviour is expected to allow defining commands and cycles together.
    """
    # Register sub-command first
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    test_cycle = {
        CYCLE_COMMAND: {
            COMMAND_NAME: 'inline-parent',
            COMMAND_ACTION: lambda: None
        },
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_COMMANDS: ['sub-cmd']
    }
    
    cycle.add_cycle(test_cycle)
    
    # Cycle should be stored indexed by extracted command name
    assert 'inline-parent' in cycle._cycles
    assert cycle._cycles['inline-parent'] == test_cycle
    
    # Command should be registered
    assert 'inline-parent' in command._commands


def test_add_cycle_with_inline_cycle_command_extracts_name():
    """Test that add_cycle() extracts command name from inline CYCLE_COMMAND.
    
    This test verifies that when CYCLE_COMMAND is an inline definition (dict),
    the command name is correctly extracted from the COMMAND_NAME field
    and used to index the cycle in storage.
    This behaviour is expected for proper cycle-command association.
    """
    # Register sub-command first
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    inline_command_def = {
        COMMAND_NAME: 'extracted-name',
        COMMAND_ACTION: lambda: None
    }
    
    test_cycle = {
        CYCLE_COMMAND: inline_command_def,
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_COMMANDS: ['sub-cmd']
    }
    
    cycle.add_cycle(test_cycle)
    
    # Should be indexed by extracted name, not inline dict object
    assert 'extracted-name' in cycle._cycles
    stored_cycle = cycle._cycles['extracted-name']
    assert stored_cycle[CYCLE_COMMAND] is inline_command_def


def test_add_cycle_with_inline_cycle_command_attaches_cycle_to_command():
    """Test that add_cycle() attaches cycle to inline command definition.
    
    This test verifies that when CYCLE_COMMAND is an inline definition (dict),
    the registered command has the cycle attached via COMMAND_CYCLE property.
    This ensures the cycle will execute when the command runs.
    This behaviour is expected for integrated cycle-command registration.
    """
    # Register sub-command first (required by cycle validation)
    sub_cmd = {
        COMMAND_NAME: 'sub-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(sub_cmd)
    
    inline_command_def = {
        COMMAND_NAME: 'inline-with-cycle',
        COMMAND_ACTION: lambda: None
    }
    
    test_cycle = {
        CYCLE_COMMAND: inline_command_def,
        CYCLE_NAME: 'attached-cycle',
        CYCLE_LOOP: lambda: False,
        CYCLE_COMMANDS: ['sub-cmd']
    }
    
    cycle.add_cycle(test_cycle)
    
    # Command should be registered with cycle attached
    registered_cmd = command._commands['inline-with-cycle']
    assert COMMAND_CYCLE in registered_cmd
    assert registered_cmd[COMMAND_CYCLE] == test_cycle


def test_add_cycle_validates_required_cycle_command_field():
    """Test that add_cycle() validates CYCLE_COMMAND field is present.
    
    This test verifies that when a cycle definition is missing the required
    CYCLE_COMMAND field, a ValueError is raised with an appropriate error message.
    This behaviour is expected because cycles must be associated with a command.
    """
    invalid_cycle = {
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(invalid_cycle)
    
    assert 'CYCLE_COMMAND' in str(exc_info.value)


def test_add_cycle_validates_required_cycle_name_field():
    """Test that add_cycle() validates CYCLE_NAME field is present.
    
    This test verifies that when a cycle definition is missing the required
    CYCLE_NAME field, a ValueError is raised with an appropriate error message.
    This behaviour is expected because cycles need independent identifiers.
    """
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(invalid_cycle)
    
    assert 'CYCLE_NAME' in str(exc_info.value)


def test_add_cycle_validates_required_cycle_loop_field():
    """Test that add_cycle() validates CYCLE_LOOP field is present.
    
    This test verifies that when a cycle definition is missing the required
    CYCLE_LOOP field, a ValueError is raised with an appropriate error message.
    This behaviour is expected because cycles must define loop behaviour.
    """
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle'
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(invalid_cycle)
    
    assert 'CYCLE_LOOP' in str(exc_info.value)


def test_add_cycle_equivalency_checking_identical_cycles_skip():
    """Test that registering an identical cycle definition is silently skipped.
    
    This test verifies that when add_cycle() is called twice with the exact same
    cycle definition for a command, the second registration is silently skipped.
    This behaviour is expected to allow modular code where the same cycle definition
    might appear in multiple places without causing errors.
    """
    test_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_INIT: lambda: None
    }
    
    cycle.add_cycle(test_cycle)
    original_cycle = cycle._cycles['test-command']
    
    # Register same cycle again
    cycle.add_cycle(test_cycle)
    
    # Verify original cycle unchanged
    assert cycle._cycles['test-command'] is original_cycle


def test_add_cycle_equivalency_checking_different_cycles_raise_error():
    """Test that registering a different cycle definition raises ValueError.
    
    This test verifies that when add_cycle() is called with a different cycle
    definition for a command that already has a cycle, a ValueError is raised.
    This behaviour is expected to prevent conflicting cycle configurations.
    """
    first_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'first-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    second_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'second-cycle',
        CYCLE_LOOP: lambda: False
    }
    
    cycle.add_cycle(first_cycle)
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(second_cycle)
    
    assert 'conflicting' in str(exc_info.value).lower()
    assert 'test-command' in str(exc_info.value)
    
    # Verify original cycle unchanged
    assert cycle._cycles['test-command'] == first_cycle


def test_add_cycles_registers_multiple_cycles():
    """Test that add_cycles() registers multiple cycle definitions.
    
    This test verifies that when a list of cycle definitions is passed to
    add_cycles(), all cycles are registered and stored in the _cycles dictionary.
    This behaviour is expected to provide consistent bulk registration API.
    """
    cycles_list = [
        {
            CYCLE_COMMAND: 'command-one',
            CYCLE_NAME: 'cycle-one',
            CYCLE_LOOP: lambda: True
        },
        {
            CYCLE_COMMAND: 'command-two',
            CYCLE_NAME: 'cycle-two',
            CYCLE_LOOP: lambda: False
        }
    ]
    
    cycle.add_cycles(cycles_list)
    
    assert 'command-one' in cycle._cycles
    assert 'command-two' in cycle._cycles
    assert cycle._cycles['command-one'][CYCLE_NAME] == 'cycle-one'
    assert cycle._cycles['command-two'][CYCLE_NAME] == 'cycle-two'


def test_add_cycles_with_mixed_inline_and_string_cycle_commands():
    """Test that add_cycles() handles mixed inline and string CYCLE_COMMAND.
    
    This test verifies that when a list contains some cycles with inline
    CYCLE_COMMAND definitions (dicts) and others with string references,
    all cycles are registered correctly.
    This behaviour is expected to provide maximum flexibility.
    """
    # Register sub-commands first
    for cmd_name in ['sub-cmd-1', 'sub-cmd-2']:
        command.add_command({
            COMMAND_NAME: cmd_name,
            COMMAND_ACTION: lambda: None
        })
    
    cycles_list = [
        {
            CYCLE_COMMAND: {
                COMMAND_NAME: 'inline-cmd',
                COMMAND_ACTION: lambda: None
            },
            CYCLE_NAME: 'inline-cycle',
            CYCLE_LOOP: lambda: True,
            CYCLE_COMMANDS: ['sub-cmd-1']
        },
        {
            CYCLE_COMMAND: 'string-ref-cmd',
            CYCLE_NAME: 'string-cycle',
            CYCLE_LOOP: lambda: False,
            CYCLE_COMMANDS: ['sub-cmd-2']
        }
    ]
    
    cycle.add_cycles(cycles_list)
    
    # Both should be registered
    assert 'inline-cmd' in cycle._cycles
    assert 'string-ref-cmd' in cycle._cycles


def test_get_cycle_retrieves_registered_cycle():
    """Test that get_cycle() retrieves a registered cycle by command name.
    
    This test verifies that after registering a cycle, it can be retrieved
    using get_cycle() with the command name as the key.
    This behaviour is expected to provide public API access to registered cycles.
    """
    test_cycle = {
        CYCLE_COMMAND: 'my-command',
        CYCLE_NAME: 'my-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_INIT: lambda: None
    }
    
    cycle.add_cycle(test_cycle)
    retrieved_cycle = cycle.get_cycle('my-command')
    
    assert retrieved_cycle is not None
    assert retrieved_cycle == test_cycle
    assert retrieved_cycle[CYCLE_NAME] == 'my-cycle'


def test_get_cycle_returns_none_for_unregistered_command():
    """Test that get_cycle() returns None for an unregistered command.
    
    This test verifies that when get_cycle() is called with a command name
    that has no registered cycle, None is returned without raising an exception.
    This behaviour is expected to allow safe checking for cycle existence.
    """
    result = cycle.get_cycle('unknown-command')
    
    assert result is None


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


class TestCycleLoopEnd:
    """Tests for CYCLE_LOOP_END functionality."""
    
    def test_cycle_loop_end_called(self):
        """
        Test that CYCLE_LOOP_END function is called at end of each iteration.
        The function should run after all cycle commands execute.
        This validates the basic functionality of the new lifecycle hook.
        """
        call_log = []
        iteration_count = [0]
        
        def loop_func():
            iteration_count[0] += 1
            return iteration_count[0] <= 2
        
        def loop_end_func():
            call_log.append('loop_end')
        
        def command_action():
            call_log.append('command')
        
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_ACTION: command_action
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_END: loop_end_func,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        def mock_run(cmd_def):
            action = cmd_def.get(COMMAND_ACTION)
            if action:
                action()
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def.get(COMMAND_NAME))
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        # Should have: command, loop_end, command, loop_end
        assert call_log == ['command', 'loop_end', 'command', 'loop_end']
    
    def test_cycle_loop_end_multiple_iterations(self):
        """
        Test that CYCLE_LOOP_END is called once per iteration across multiple iterations.
        Each iteration should call loop end function exactly once after commands.
        This validates the function is consistently called in every iteration.
        """
        loop_end_count = [0]
        iteration_count = [0]
        
        def loop_func():
            iteration_count[0] += 1
            return iteration_count[0] <= 5
        
        def loop_end_func():
            loop_end_count[0] += 1
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_END: loop_end_func,
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
        
        assert loop_end_count[0] == 5
    
    def test_cycle_loop_end_optional(self):
        """
        Test that cycles work without CYCLE_LOOP_END defined.
        Cycles should execute normally when CYCLE_LOOP_END is not provided.
        This validates backward compatibility with existing cycles.
        """
        iteration_count = [0]
        
        def loop_func():
            result = iteration_count[0] < 2
            if result:
                iteration_count[0] += 1
            return result
        
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
        
        # Should not raise an error
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        assert iteration_count[0] == 2
    
    def test_cycle_loop_end_execution_order(self):
        """
        Test that execution order is: commands, CYCLE_LOOP_END, then CYCLE_LOOP check.
        Commands should complete before loop end, and loop end before next iteration.
        This validates the correct placement of loop end in the cycle lifecycle.
        """
        execution_log = []
        iteration_count = [0]
        
        def loop_func():
            execution_log.append(f'loop_check_{iteration_count[0]}')
            iteration_count[0] += 1
            return iteration_count[0] <= 2
        
        def loop_start_func():
            execution_log.append(f'loop_start_{iteration_count[0]}')
        
        def loop_end_func():
            execution_log.append(f'loop_end_{iteration_count[0]}')
        
        def command_action():
            execution_log.append(f'command_{iteration_count[0]}')
        
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_ACTION: command_action
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_START: loop_start_func,
                CYCLE_LOOP_END: loop_end_func,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        def mock_run(cmd_def):
            action = cmd_def.get(COMMAND_ACTION)
            if action:
                action()
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def.get(COMMAND_NAME))
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        # Expected: loop_check_0, loop_start_1, command_1, loop_end_1, loop_check_1, loop_start_2, command_2, loop_end_2, loop_check_2
        expected = [
            'loop_check_0', 'loop_start_1', 'command_1', 'loop_end_1',
            'loop_check_1', 'loop_start_2', 'command_2', 'loop_end_2',
            'loop_check_2'
        ]
        assert execution_log == expected
    
    def test_cycle_loop_end_access_to_state(self):
        """
        Test that CYCLE_LOOP_END can read state set by cycle commands.
        Loop end should have access to state modified during iteration.
        This validates that state changes are visible to loop end function.
        """
        state = {'value': 0}
        
        def loop_func():
            return state['value'] < 2
        
        def command_action():
            state['value'] += 1
        
        def loop_end_func():
            state['checked'] = state['value']
        
        commands = {
            'cmd1': {
                COMMAND_NAME: 'cmd1',
                COMMAND_ACTION: command_action
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_END: loop_end_func,
                CYCLE_COMMANDS: ['cmd1']
            }
        }
        
        def mock_run(cmd_def):
            action = cmd_def.get(COMMAND_ACTION)
            if action:
                action()
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def.get(COMMAND_NAME))
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        # Loop end should have seen the final value
        assert state['checked'] == 2
    
    def test_cycle_loop_end_modify_state(self):
        """
        Test that CYCLE_LOOP_END can modify state for next iteration.
        State modifications in loop end should persist to next iteration.
        This validates that loop end can be used for counter increments and cleanup.
        """
        state = {'counter': 0, 'iterations': 0}
        
        def loop_func():
            return state['iterations'] < 3
        
        def loop_end_func():
            state['iterations'] += 1
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_END: loop_end_func,
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
        
        assert state['iterations'] == 3
    
    def test_cycle_loop_end_error_handling(self):
        """
        Test that error in CYCLE_LOOP_END raises CycleExecutionError with context.
        Exceptions in loop end should be wrapped with cycle name and error details.
        This validates proper error handling and debugging information.
        """
        iteration_count = [0]
        
        def loop_func():
            iteration_count[0] += 1
            return iteration_count[0] <= 2
        
        def loop_end_func():
            raise ValueError("Test error in loop end")
        
        commands = {}
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'test-cycle',
                CYCLE_LOOP: loop_func,
                CYCLE_LOOP_END: loop_end_func,
                CYCLE_COMMANDS: []
            }
        }
        
        def mock_run(cmd_def):
            pass
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            pass
        
        def mock_sort(queue, cmd_dict):
            return []
        
        with pytest.raises(cycle.CycleExecutionError) as exc_info:
            cycle.execute_cycle(
                parent_cmd, commands, mock_run, mock_queue_add, mock_sort
            )
        
        error_message = str(exc_info.value)
        assert 'test-cycle' in error_message
        assert 'Test error in loop end' in error_message
    
    def test_cycle_loop_end_with_nested_cycles(self):
        """
        Test that nested cycles each call their own CYCLE_LOOP_END correctly.
        Each cycle should maintain its own loop end calls independently.
        This validates proper nesting and isolation of lifecycle functions.
        """
        parent_calls = []
        nested_calls = []
        parent_iteration = [0]
        nested_iteration = [0]
        
        def parent_loop():
            parent_iteration[0] += 1
            return parent_iteration[0] <= 2
        
        def parent_loop_end():
            parent_calls.append(parent_iteration[0])
        
        def nested_loop():
            nested_iteration[0] += 1
            result = nested_iteration[0] <= 2
            if not result:
                nested_iteration[0] = 0  # Reset for next parent iteration
            return result
        
        def nested_loop_end():
            nested_calls.append(nested_iteration[0])
        
        commands = {
            'nested-parent': {
                COMMAND_NAME: 'nested-parent',
                COMMAND_CYCLE: {
                    CYCLE_NAME: 'nested-cycle',
                    CYCLE_LOOP: nested_loop,
                    CYCLE_LOOP_END: nested_loop_end,
                    CYCLE_COMMANDS: []
                }
            }
        }
        parent_cmd = {
            COMMAND_NAME: 'parent',
            COMMAND_CYCLE: {
                CYCLE_NAME: 'parent-cycle',
                CYCLE_LOOP: parent_loop,
                CYCLE_LOOP_END: parent_loop_end,
                CYCLE_COMMANDS: ['nested-parent']
            }
        }
        
        def mock_run(cmd_def):
            if cycle._is_cycle_command(cmd_def):
                cycle.execute_cycle(
                    cmd_def, commands, mock_run, mock_queue_add, mock_sort
                )
        
        def mock_queue_add(cmd_def, queue, cmd_dict):
            queue.append(cmd_def.get(COMMAND_NAME))
        
        def mock_sort(queue, cmd_dict):
            return queue
        
        cycle.execute_cycle(
            parent_cmd, commands, mock_run, mock_queue_add, mock_sort
        )
        
        # Parent should call loop_end 2 times
        assert len(parent_calls) == 2
        # Nested should call loop_end 2 times per parent iteration = 4 times
        assert len(nested_calls) == 4


