"""
Tests for configurable cycle nesting depth feature.

This module tests the get/set functions for max cycle nesting depth
in the cycle, config, and core modules.
"""

import pytest
from spafw37 import cycle
from spafw37 import config
from spafw37 import core as spafw37


@pytest.fixture(autouse=True)
def reset_depth():
    """Reset cycle nesting depth to default before each test.
    
    This ensures that tests are isolated and don't affect each other.
    Runs automatically before and after each test.
    """
    cycle.set_max_cycle_nesting_depth(5)
    yield
    cycle.set_max_cycle_nesting_depth(5)


class TestCycleModuleDepthFunctions:
    """Tests for cycle module's depth getter and setter."""
    
    def test_get_default_max_nesting_depth(self):
        """
        Test that get_max_cycle_nesting_depth returns default value of 5.
        Default value should be 5 levels as documented.
        This validates the initial state of the module.
        """
        depth = cycle.get_max_cycle_nesting_depth()
        assert depth == 5
    
    def test_set_max_nesting_depth_valid_value(self):
        """
        Test that set_max_cycle_nesting_depth accepts valid positive integers.
        Should successfully set the depth and return it via getter.
        This validates basic setter functionality.
        """
        cycle.set_max_cycle_nesting_depth(10)
        assert cycle.get_max_cycle_nesting_depth() == 10
        
        cycle.set_max_cycle_nesting_depth(1)
        assert cycle.get_max_cycle_nesting_depth() == 1
        
        cycle.set_max_cycle_nesting_depth(100)
        assert cycle.get_max_cycle_nesting_depth() == 100
    
    def test_set_max_nesting_depth_rejects_zero(self):
        """
        Test that set_max_cycle_nesting_depth rejects zero.
        Zero is not a valid depth value.
        This validates input validation for boundary case.
        """
        with pytest.raises(ValueError, match="positive integer"):
            cycle.set_max_cycle_nesting_depth(0)
        # Should remain at previous value
        assert cycle.get_max_cycle_nesting_depth() == 5
    
    def test_set_max_nesting_depth_rejects_negative(self):
        """
        Test that set_max_cycle_nesting_depth rejects negative values.
        Negative depths don't make sense and should be rejected.
        This validates input validation for invalid range.
        """
        with pytest.raises(ValueError, match="positive integer"):
            cycle.set_max_cycle_nesting_depth(-1)
        # Should remain at previous value
        assert cycle.get_max_cycle_nesting_depth() == 5
    
    def test_set_max_nesting_depth_rejects_non_integer(self):
        """
        Test that set_max_cycle_nesting_depth rejects non-integer types.
        Should reject strings, floats, None, etc.
        This validates type checking in the setter.
        """
        with pytest.raises(ValueError, match="positive integer"):
            cycle.set_max_cycle_nesting_depth("10")
        
        with pytest.raises(ValueError, match="positive integer"):
            cycle.set_max_cycle_nesting_depth(10.5)
        
        with pytest.raises(ValueError, match="positive integer"):
            cycle.set_max_cycle_nesting_depth(None)
        
        # Should remain at previous value
        assert cycle.get_max_cycle_nesting_depth() == 5
    
    def test_depth_persists_across_calls(self):
        """
        Test that depth value persists across multiple get/set operations.
        Setting a value should maintain it until explicitly changed.
        This validates state management in the module.
        """
        cycle.set_max_cycle_nesting_depth(7)
        assert cycle.get_max_cycle_nesting_depth() == 7
        assert cycle.get_max_cycle_nesting_depth() == 7  # Still 7
        
        cycle.set_max_cycle_nesting_depth(3)
        assert cycle.get_max_cycle_nesting_depth() == 3
        assert cycle.get_max_cycle_nesting_depth() == 3  # Still 3


class TestConfigModuleDepthFunctions:
    """Tests for config module's depth getter and setter delegates."""
    
    def test_get_max_nesting_depth_delegates_to_cycle(self):
        """
        Test that config.get_max_cycle_nesting_depth delegates to cycle module.
        Config module should be a pass-through to cycle module.
        This validates the delegation pattern.
        """
        cycle.set_max_cycle_nesting_depth(15)
        assert config.get_max_cycle_nesting_depth() == 15
    
    def test_set_max_nesting_depth_delegates_to_cycle(self):
        """
        Test that config.set_max_cycle_nesting_depth delegates to cycle module.
        Setting via config should affect cycle module state.
        This validates bidirectional delegation.
        """
        config.set_max_cycle_nesting_depth(20)
        assert cycle.get_max_cycle_nesting_depth() == 20
        assert config.get_max_cycle_nesting_depth() == 20
    
    def test_config_setter_validates_input(self):
        """
        Test that config.set_max_cycle_nesting_depth validates input.
        Should propagate validation errors from cycle module.
        This validates error propagation through delegation.
        """
        with pytest.raises(ValueError, match="positive integer"):
            config.set_max_cycle_nesting_depth(0)
        
        with pytest.raises(ValueError, match="positive integer"):
            config.set_max_cycle_nesting_depth(-5)


class TestCoreModuleDepthFunctions:
    """Tests for core module's public API depth functions."""
    
    def test_get_max_nesting_depth_public_api(self):
        """
        Test that core.get_max_cycle_nesting_depth provides public API access.
        Core module should expose the function for user applications.
        This validates the public API surface.
        """
        cycle.set_max_cycle_nesting_depth(12)
        assert spafw37.get_max_cycle_nesting_depth() == 12
    
    def test_set_max_nesting_depth_public_api(self):
        """
        Test that core.set_max_cycle_nesting_depth provides public API access.
        Users should be able to configure depth via core module.
        This validates the complete public API workflow.
        """
        spafw37.set_max_cycle_nesting_depth(8)
        assert spafw37.get_max_cycle_nesting_depth() == 8
        assert cycle.get_max_cycle_nesting_depth() == 8
    
    def test_core_setter_validates_input(self):
        """
        Test that core.set_max_cycle_nesting_depth validates input.
        Public API should enforce same validation as internal modules.
        This validates consistent error handling across API layers.
        """
        with pytest.raises(ValueError, match="positive integer"):
            spafw37.set_max_cycle_nesting_depth(0)
        
        with pytest.raises(ValueError, match="positive integer"):
            spafw37.set_max_cycle_nesting_depth("not a number")
    
    def test_core_api_integration(self):
        """
        Test full integration of depth configuration through public API.
        Complete workflow: set via core, verify via all modules.
        This validates end-to-end functionality for users.
        """
        # Set via public API
        spafw37.set_max_cycle_nesting_depth(25)
        
        # Verify via all access points
        assert spafw37.get_max_cycle_nesting_depth() == 25
        assert config.get_max_cycle_nesting_depth() == 25
        assert cycle.get_max_cycle_nesting_depth() == 25


class TestDepthEffectOnNesting:
    """Tests verifying that depth setting actually affects nesting validation."""
    
    def test_default_depth_allows_five_levels(self):
        """
        Test that default depth of 5 allows 5 levels of nesting.
        Should not raise error at depth 5.
        This validates default configuration matches documentation.
        """
        from spafw37.constants.cycle import CYCLE_COMMANDS
        from spafw37.constants.command import COMMAND_NAME, COMMAND_REQUIRED_PARAMS
        
        # Create a deeply nested structure (5 levels)
        commands = {f'cmd{i}': {COMMAND_NAME: f'cmd{i}', COMMAND_REQUIRED_PARAMS: []} for i in range(6)}
        
        cycle_def = {
            CYCLE_COMMANDS: ['cmd0']
        }
        
        # Nested 5 levels deep should work
        result = cycle._collect_cycle_params_recursive(cycle_def, commands, depth=5)
        assert isinstance(result, set)
    
    def test_default_depth_rejects_six_levels(self):
        """
        Test that default depth of 5 rejects 6 levels of nesting.
        Should raise CycleValidationError at depth 6.
        This validates depth enforcement at the limit.
        """
        from spafw37.constants.cycle import CYCLE_COMMANDS, CYCLE_NAME
        from spafw37.constants.command import COMMAND_NAME, COMMAND_REQUIRED_PARAMS
        
        commands = {f'cmd{i}': {COMMAND_NAME: f'cmd{i}', COMMAND_REQUIRED_PARAMS: []} for i in range(7)}
        
        cycle_def = {
            CYCLE_NAME: 'test-cycle',
            CYCLE_COMMANDS: ['cmd0']
        }
        
        # Nested 6 levels deep should fail
        with pytest.raises(cycle.CycleValidationError, match="nesting depth exceeds maximum"):
            cycle._collect_cycle_params_recursive(cycle_def, commands, depth=6)
    
    def test_increased_depth_allows_deeper_nesting(self):
        """
        Test that increasing depth limit allows deeper nesting.
        Configuring higher depth should permit more nesting levels.
        This validates that configuration actually affects validation.
        """
        from spafw37.constants.cycle import CYCLE_COMMANDS
        from spafw37.constants.command import COMMAND_NAME, COMMAND_REQUIRED_PARAMS
        
        # Increase limit to 10
        spafw37.set_max_cycle_nesting_depth(10)
        
        commands = {f'cmd{i}': {COMMAND_NAME: f'cmd{i}', COMMAND_REQUIRED_PARAMS: []} for i in range(11)}
        
        cycle_def = {
            CYCLE_COMMANDS: ['cmd0']
        }
        
        # 10 levels should now work
        result = cycle._collect_cycle_params_recursive(cycle_def, commands, depth=10)
        assert isinstance(result, set)
        
        # But 11 should still fail
        with pytest.raises(cycle.CycleValidationError, match="nesting depth exceeds maximum"):
            cycle._collect_cycle_params_recursive(cycle_def, commands, depth=11)
    
    def test_decreased_depth_restricts_nesting(self):
        """
        Test that decreasing depth limit restricts nesting more.
        Configuring lower depth should prevent previously allowed nesting.
        This validates that configuration works in both directions.
        """
        from spafw37.constants.cycle import CYCLE_COMMANDS, CYCLE_NAME
        from spafw37.constants.command import COMMAND_NAME, COMMAND_REQUIRED_PARAMS
        
        # Decrease limit to 2
        spafw37.set_max_cycle_nesting_depth(2)
        
        commands = {f'cmd{i}': {COMMAND_NAME: f'cmd{i}', COMMAND_REQUIRED_PARAMS: []} for i in range(4)}
        
        cycle_def = {
            CYCLE_NAME: 'test-cycle',
            CYCLE_COMMANDS: ['cmd0']
        }
        
        # 2 levels should work
        result = cycle._collect_cycle_params_recursive(cycle_def, commands, depth=2)
        assert isinstance(result, set)
        
        # 3 levels should fail
        with pytest.raises(cycle.CycleValidationError, match="nesting depth exceeds maximum"):
            cycle._collect_cycle_params_recursive(cycle_def, commands, depth=3)
