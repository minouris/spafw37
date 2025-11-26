"""Tests for switch parameter change behaviour (Issue #32).

This module tests the three switch change behaviours for TOGGLE parameters:
- SWITCH_REJECT: Raise error if another switch is already set (default)
- SWITCH_UNSET: Automatically unset conflicting switches
- SWITCH_RESET: Reset conflicting switches to their default values

Note: Switch change behaviour currently only applies to TOGGLE parameters.
This is consistent with the original XOR implementation.
"""

import pytest
from spafw37 import param, config
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_TEXT,
    PARAM_SWITCH_LIST,
    PARAM_SWITCH_CHANGE_BEHAVIOR,
    PARAM_DEFAULT,
    PARAM_ALIASES,
    SWITCH_UNSET,
    SWITCH_RESET,
    SWITCH_REJECT,
)


def setup_function():
    """Reset module state between tests."""
    param._param_aliases.clear()
    param._params.clear()
    param._preparse_args.clear()
    config._config.clear()
    param._xor_list.clear()
    param._set_batch_mode(False)
    param._set_xor_validation_enabled(True)


# =============================================================================
# SWITCH_REJECT Tests (Default Behaviour)
# =============================================================================

def test_switch_reject_default_toggle_raises_error():
    """Test that SWITCH_REJECT is the default behaviour for mutually exclusive toggle parameters.
    
    This test verifies that when one toggle in a switch group is set and another conflicting
    toggle is set without explicit PARAM_SWITCH_CHANGE_BEHAVIOR configuration, a ValueError is raised.
    This behaviour is expected because SWITCH_REJECT is the default to maintain backward compatibility
    and prevent accidental configuration conflicts.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'mode_a',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_b'],
            # PARAM_SWITCH_CHANGE_BEHAVIOR omitted - defaults to SWITCH_REJECT
        },
        {
            PARAM_NAME: 'mode_b',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_a'],
        },
    ])
    
    param.set_param('mode_a', True)
    assert param.get_param('mode_a') is True
    
    with pytest.raises(ValueError, match="Cannot set 'mode_b', conflicts with 'mode_a'"):
        param.set_param('mode_b', True)


def test_switch_reject_explicit_toggle_raises_error():
    """Test that explicitly configured SWITCH_REJECT behaviour raises errors for conflicting toggles.
    
    This test verifies that when PARAM_SWITCH_CHANGE_BEHAVIOR is explicitly set to SWITCH_REJECT,
    attempting to set a conflicting toggle parameter raises a ValueError with a descriptive message.
    This behaviour is expected because explicit configuration should be honoured and SWITCH_REJECT
    enforces strict mutual exclusion to prevent configuration errors.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'fast',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['slow'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'slow',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['fast'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
    ])
    
    param.set_param('fast', True)
    with pytest.raises(ValueError, match="conflicts with 'fast'"):
        param.set_param('slow', True)


def test_switch_reject_three_way_group_raises_error():
    """Test that SWITCH_REJECT behaviour works correctly with three mutually exclusive parameters.
    
    This test verifies that in a switch group with three toggle parameters, setting any parameter
    when another is already active raises a ValueError identifying the conflict.
    This behaviour is expected because mutual exclusion must apply across all members of the group,
    not just pairwise, to maintain consistent configuration state.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'small',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['medium', 'large'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'medium',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['small', 'large'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'large',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['small', 'medium'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
    ])
    
    param.set_param('small', True)
    with pytest.raises(ValueError, match="conflicts with 'small'"):
        param.set_param('medium', True)
    with pytest.raises(ValueError, match="conflicts with 'small'"):
        param.set_param('large', True)


def test_switch_reject_does_not_modify_params():
    """Test that SWITCH_REJECT behaviour does not modify any parameters when a conflict is detected.
    
    This test verifies that when SWITCH_REJECT raises a ValueError due to a conflict, both the
    existing parameter and the conflicting parameter being set remain in their original states.
    This behaviour is expected because error conditions should be atomic operations that leave
    the system in a consistent state without partial modifications.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'option_a',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['option_b'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'option_b',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['option_a'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
    ])
    
    param.set_param('option_a', True)
    assert param.get_param('option_a') is True
    
    with pytest.raises(ValueError):
        param.set_param('option_b', True)
    
    # option_a unchanged, option_b not set
    assert param.get_param('option_a') is True
    assert param.get_param('option_b') is None


# =============================================================================
# SWITCH_UNSET Tests
# =============================================================================

def test_switch_unset_toggle_removes_conflicting_param():
    """Test that SWITCH_UNSET behaviour automatically removes conflicting toggle parameters.
    
    This test verifies that when a toggle parameter is set and another toggle in the same
    switch group is set with SWITCH_UNSET behaviour, the first parameter is completely removed.
    This behaviour is expected because SWITCH_UNSET enables mode switching by automatically
    clearing previous mode selections without requiring manual cleanup.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'mode_read',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_write'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'mode_write',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_read'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    param.set_param('mode_read', True)
    assert param.get_param('mode_read') is True
    assert param.get_param('mode_write') is None
    
    # Setting mode_write should unset mode_read
    param.set_param('mode_write', True)
    assert param.get_param('mode_read') is None
    assert param.get_param('mode_write') is True


def test_switch_unset_three_way_group_removes_all_conflicts():
    """Test that SWITCH_UNSET behaviour removes all conflicting parameters in a three-way switch group.
    
    This test verifies that when any parameter in a three-parameter switch group is set,
    all other conflicting parameters are automatically unset regardless of how many are active.
    This behaviour is expected because SWITCH_UNSET must clear all conflicts to maintain
    mutual exclusion across the entire group, not just pairwise relationships.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'color_red',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['color_green', 'color_blue'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'color_green',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['color_red', 'color_blue'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'color_blue',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['color_red', 'color_green'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    param.set_param('color_red', True)
    assert param.get_param('color_red') is True
    
    param.set_param('color_green', True)
    assert param.get_param('color_red') is None
    assert param.get_param('color_green') is True
    assert param.get_param('color_blue') is None
    
    param.set_param('color_blue', True)
    assert param.get_param('color_red') is None
    assert param.get_param('color_green') is None
    assert param.get_param('color_blue') is True


def test_switch_unset_switching_back_and_forth():
    """Test that SWITCH_UNSET behaviour allows repeated mode switching without errors.
    
    This test verifies that parameters with SWITCH_UNSET can be set and changed multiple times
    in sequence, with each new setting automatically unsetting the conflicting parameter.
    This behaviour is expected because SWITCH_UNSET is designed for dynamic mode switching
    where users can change modes freely during execution without manual state management.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'mode_a',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_b'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'mode_b',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_a'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    # Switch multiple times
    param.set_param('mode_a', True)
    assert param.get_param('mode_a') is True
    
    param.set_param('mode_b', True)
    assert param.get_param('mode_a') is None
    assert param.get_param('mode_b') is True
    
    param.set_param('mode_a', True)
    assert param.get_param('mode_a') is True
    assert param.get_param('mode_b') is None
    
    param.set_param('mode_b', True)
    assert param.get_param('mode_a') is None
    assert param.get_param('mode_b') is True


def test_switch_unset_no_conflict_when_none_set():
    """Test that SWITCH_UNSET behaviour allows setting parameters when no conflicts exist.
    
    This test verifies that when no conflicting parameters are currently set, a parameter with
    SWITCH_UNSET behaviour can be set without errors or unexpected side effects.
    This behaviour is expected because SWITCH_UNSET only acts when actual conflicts exist,
    allowing normal parameter setting when the switch group is empty.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'opt_x',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['opt_y'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'opt_y',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['opt_x'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    # No conflicts initially
    param.set_param('opt_x', True)
    assert param.get_param('opt_x') is True
    assert param.get_param('opt_y') is None


# =============================================================================
# SWITCH_RESET Tests
# =============================================================================

def test_switch_reset_toggle_resets_to_default():
    """Test that SWITCH_RESET behaviour restores conflicting toggle parameters to their default values.
    
    This test verifies that when a toggle with SWITCH_RESET behaviour is set, conflicting toggles
    are reset to their PARAM_DEFAULT values rather than being completely removed.
    This behaviour is expected because SWITCH_RESET preserves parameter definitions in configuration
    while ensuring only one switch is active, useful for toggles with meaningful default states.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'priority_high',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_low'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'priority_low',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_high'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    param.set_param('priority_high', True)
    assert param.get_param('priority_high') is True
    assert param.get_param('priority_low') is None  # Not set yet
    
    # Setting priority_low should reset priority_high to default (False)
    param.set_param('priority_low', True)
    assert param.get_param('priority_high') is False  # Reset to default
    assert param.get_param('priority_low') is True


def test_switch_reset_three_way_group_resets_all_conflicts():
    """Test that SWITCH_RESET behaviour resets all conflicting parameters in a three-way switch group.
    
    This test verifies that when any parameter in a three-parameter switch group is set,
    all conflicting parameters are reset to their default values if defined.
    This behaviour is expected because SWITCH_RESET must maintain mutual exclusion across the
    entire group while preserving parameter definitions with their default states.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'level_low',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['level_medium', 'level_high'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'level_medium',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['level_low', 'level_high'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'level_high',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['level_low', 'level_medium'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    param.set_param('level_low', True)
    param.set_param('level_medium', True)
    # level_low should be reset to False, level_high unset
    assert param.get_param('level_low') is False
    assert param.get_param('level_medium') is True
    assert param.get_param('level_high') is None
    
    param.set_param('level_high', True)
    # level_medium should be reset to False, level_low already False
    assert param.get_param('level_low') is False
    assert param.get_param('level_medium') is False
    assert param.get_param('level_high') is True


def test_switch_reset_no_default_unsets_param():
    """Test that SWITCH_RESET behaviour unsets parameters that have no PARAM_DEFAULT defined.
    
    This test verifies that when a conflicting parameter has no default value, SWITCH_RESET
    completely removes the parameter rather than setting it to a default value.
    This behaviour is expected because reset_param() unsets parameters without defaults,
    providing consistent behaviour when defaults are not defined.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'style_bold',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            # No PARAM_DEFAULT specified
            PARAM_SWITCH_LIST: ['style_italic'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'style_italic',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            # No PARAM_DEFAULT specified
            PARAM_SWITCH_LIST: ['style_bold'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    param.set_param('style_bold', True)
    assert param.get_param('style_bold') is True
    
    # Reset with no default should unset
    param.set_param('style_italic', True)
    assert param.get_param('style_bold') is None
    assert param.get_param('style_italic') is True


def test_switch_reset_switching_back_and_forth():
    """Test that SWITCH_RESET behaviour allows repeated mode switching with default value restoration.
    
    This test verifies that parameters with SWITCH_RESET can be set multiple times in sequence,
    with each new setting resetting conflicting parameters to their defaults.
    This behaviour is expected because SWITCH_RESET enables dynamic mode switching while
    maintaining predictable parameter states through default value restoration.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'encrypt_on',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['encrypt_off'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'encrypt_off',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['encrypt_on'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    # Switch multiple times
    param.set_param('encrypt_on', True)
    assert param.get_param('encrypt_on') is True
    assert param.get_param('encrypt_off') is None  # Not set yet
    
    param.set_param('encrypt_off', True)
    assert param.get_param('encrypt_on') is False  # Reset to default
    assert param.get_param('encrypt_off') is True
    
    param.set_param('encrypt_on', True)
    assert param.get_param('encrypt_on') is True
    assert param.get_param('encrypt_off') is False  # Reset to default


# =============================================================================
# Batch Mode Tests
# =============================================================================

def test_batch_mode_flag_default_false():
    """Test that the internal batch mode flag is False by default.
    
    This test verifies that _get_batch_mode() returns False when no batch operations are active.
    This behaviour is expected because batch mode is only enabled during set_values() processing
    to enforce strict switch validation for command-line argument parsing.
    """
    setup_function()
    assert param._get_batch_mode() is False


def test_set_batch_mode_enables_flag():
    """Test that the _set_batch_mode() function can enable batch mode.
    
    This test verifies that calling _set_batch_mode(True) sets the internal flag to True.
    This behaviour is expected because the framework needs to enable batch mode during
    set_values() to enforce SWITCH_REJECT behaviour for CLI argument validation.
    """
    setup_function()
    param._set_batch_mode(True)
    assert param._get_batch_mode() is True


def test_set_batch_mode_disables_flag():
    """Test that the _set_batch_mode() function can disable batch mode.
    
    This test verifies that calling _set_batch_mode(False) sets the internal flag to False
    after it was previously enabled.
    This behaviour is expected because set_values() must restore normal switch behaviour
    after completing CLI argument processing.
    """
    setup_function()
    param._set_batch_mode(True)
    param._set_batch_mode(False)
    assert param._get_batch_mode() is False


def test_batch_mode_forces_switch_reject():
    """Test that batch mode overrides SWITCH_UNSET configuration and enforces SWITCH_REJECT behaviour.
    
    This test verifies that when batch mode is active, switch conflicts raise errors even when
    PARAM_SWITCH_CHANGE_BEHAVIOR is configured as SWITCH_UNSET.
    This behaviour is expected because CLI argument parsing requires strict validation to provide
    clear error messages about conflicting command-line arguments to users.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'opt_a',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['opt_b'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,  # Configured as UNSET
        },
        {
            PARAM_NAME: 'opt_b',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['opt_a'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    param._set_batch_mode(True)
    
    param.set_param('opt_a', True)
    
    # Should raise error even though SWITCH_UNSET is configured
    with pytest.raises(ValueError, match="conflicts with 'opt_a'"):
        param.set_param('opt_b', True)
    
    param._set_batch_mode(False)


def test_batch_mode_forces_switch_reject_with_reset_config():
    """Test that batch mode overrides SWITCH_RESET configuration and enforces SWITCH_REJECT behaviour.
    
    This test verifies that when batch mode is active, switch conflicts raise errors even when
    PARAM_SWITCH_CHANGE_BEHAVIOR is configured as SWITCH_RESET.
    This behaviour is expected because CLI argument parsing requires strict validation regardless
    of configured switch behaviour to ensure users receive clear error messages.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'priority_high',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_low'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,  # Configured as RESET
        },
        {
            PARAM_NAME: 'priority_low',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_high'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    param._set_batch_mode(True)
    
    param.set_param('priority_high', True)
    
    # Should raise error even though SWITCH_RESET is configured
    with pytest.raises(ValueError, match="conflicts with 'priority_high'"):
        param.set_param('priority_low', True)
    
    param._set_batch_mode(False)


def test_set_values_enables_and_disables_batch_mode():
    """Test that set_values() correctly manages batch mode lifecycle during parameter processing.
    
    This test verifies that set_values() enables batch mode before processing parameters and
    disables it after completion, returning to normal switch behaviour.
    This behaviour is expected because set_values() is used for CLI parsing which requires
    strict validation, but subsequent programmatic calls should use configured behaviour.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'test_param',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--test'],
        },
    ])
    
    # Batch mode should be False initially
    assert param._get_batch_mode() is False
    
    # set_values should process successfully
    param.set_values([{'alias': '--test', 'value': 'test'}])
    
    # After set_values completes, batch mode should be False again
    assert param._get_batch_mode() is False
    assert param.get_param('test_param') == 'test'


def test_set_values_disables_batch_mode_on_error():
    """Test that set_values() disables batch mode even when parameter validation fails.
    
    This test verifies that when set_values() encounters an error during parameter processing,
    batch mode is still disabled to prevent the flag from remaining in an incorrect state.
    This behaviour is expected because proper cleanup must occur regardless of success or failure
    to maintain consistent system state for subsequent operations.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'conflict_a',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--ca'],
            PARAM_SWITCH_LIST: ['conflict_b'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'conflict_b',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--cb'],
            PARAM_SWITCH_LIST: ['conflict_a'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    param.set_param('conflict_a', True)
    
    # set_values should raise error due to batch mode forcing SWITCH_REJECT
    with pytest.raises(ValueError):
        param.set_values([{'alias': '--cb', 'value': True}])
    
    # Batch mode should still be False after error
    assert param._get_batch_mode() is False


# =============================================================================
# XOR Validation Skip Tests
# =============================================================================

def test_switch_behavior_respects_skip_xor_validation():
    """Test that switch change behaviour is bypassed when XOR validation is disabled.
    
    This test verifies that when _set_xor_validation_enabled(False) is called, conflicting
    switch parameters can be set without triggering SWITCH_REJECT or other behaviours.
    This behaviour is expected because disabling XOR validation allows testing scenarios and
    special cases where mutual exclusion rules should not apply.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'mode_a',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_b'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'mode_b',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['mode_a'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
    ])
    
    param.set_param('mode_a', True)
    
    # Disable XOR validation
    param._set_xor_validation_enabled(False)
    
    # Should not raise error even with SWITCH_REJECT
    param.set_param('mode_b', True)
    assert param.get_param('mode_a') is True
    assert param.get_param('mode_b') is True
    
    # Re-enable for cleanup
    param._set_xor_validation_enabled(True)


# =============================================================================
# Mixed Behaviour Tests
# =============================================================================

def test_mixed_behaviors_in_same_group():
    """Test that parameters in the same switch group can have different switch change behaviours.
    
    This test verifies that one parameter can use SWITCH_REJECT while another in the same
    group uses SWITCH_UNSET, with each parameter's behaviour applying when it is set.
    This behaviour is expected because switch change behaviour is a per-parameter setting,
    allowing flexible configuration for different use cases within the same mutual exclusion group.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'strict',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['lenient'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,  # Strict validation
        },
        {
            PARAM_NAME: 'lenient',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['strict'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,  # Automatic clearing
        },
    ])
    
    # strict uses REJECT
    param.set_param('lenient', True)
    with pytest.raises(ValueError):
        param.set_param('strict', True)
    
    # lenient uses UNSET
    param.set_param('lenient', True)
    assert param.get_param('strict') is None
    assert param.get_param('lenient') is True


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

def test_switch_behavior_with_no_conflict():
    """Test that parameters with switch behaviour can be set normally when no conflicts exist.
    
    This test verifies that when no conflicting parameters are currently active, a parameter
    in a switch group can be set without errors regardless of its switch change behaviour.
    This behaviour is expected because switch change behaviour only applies when actual conflicts
    are detected, allowing normal parameter operations when the switch group is empty.
    """
    setup_function()
    param.add_params([
        {
            PARAM_NAME: 'alpha',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['beta'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
        {
            PARAM_NAME: 'beta',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_SWITCH_LIST: ['alpha'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,
        },
    ])
    
    # No conflicts initially - both None
    assert param.get_param('alpha') is None
    assert param.get_param('beta') is None
    
    # Setting alpha to True works (no conflict)
    param.set_param('alpha', True)
    assert param.get_param('alpha') is True
    assert param.get_param('beta') is None
