"""Tests for unset_param() and reset_param() functionality."""

import pytest
from spafw37 import param, config
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_DEFAULT,
    PARAM_IMMUTABLE,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
)


@pytest.fixture(autouse=True)
def reset_param_state():
    """Reset param state before each test."""
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    config._config.clear()
    yield
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    config._config.clear()


def test_unset_param_by_param_name():
    """
    Test unsetting a parameter using param_name.
    Parameter should be removed from config dict after unset.
    This validates basic unset functionality through parameter name resolution.
    """
    test_param = {
        PARAM_NAME: 'test-value',
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    param.add_param(test_param)
    param.set_param(param_name='test-value', value='some-value')
    
    assert config.get_config_value('test-value') == 'some-value'
    
    param.unset_param(param_name='test-value')
    
    assert config.get_config_value('test-value') is None


def test_unset_param_by_bind_name():
    """
    Test unsetting a parameter using bind_name.
    Parameter should be removed when accessed via config bind name.
    This validates flexible resolution with explicit bind_name.
    """
    test_param = {
        PARAM_NAME: 'test-param',
        PARAM_CONFIG_NAME: 'test_bind',
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    param.add_param(test_param)
    param.set_param(param_name='test-param', value='value')
    
    assert config.get_config_value('test_bind') == 'value'
    
    param.unset_param(bind_name='test_bind')
    
    assert config.get_config_value('test_bind') is None


def test_unset_param_by_alias():
    """
    Test unsetting a parameter using alias.
    Parameter should be removed when accessed via CLI alias.
    This validates flexible resolution with alias resolution.
    """
    test_param = {
        PARAM_NAME: 'verbose',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        'aliases': ['--verbose', '-v'],
    }
    param.add_param(test_param)
    param.set_param(param_name='verbose', value=True)
    
    assert config.get_config_value('verbose') is True
    
    param.unset_param(alias='--verbose')
    
    assert config.get_config_value('verbose') is None


def test_unset_param_not_found():
    """
    Test unsetting a non-existent parameter raises ValueError.
    Should provide clear error message with parameter identifier.
    This validates error handling for missing parameters.
    """
    with pytest.raises(ValueError, match="Parameter 'nonexistent' not found"):
        param.unset_param(param_name='nonexistent')


def test_unset_param_immutable():
    """
    Test unsetting an immutable parameter raises ValueError.
    Immutable parameters cannot be removed once set.
    This validates immutability protection for unset operations.
    """
    test_param = {
        PARAM_NAME: 'app-version',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_IMMUTABLE: True,
    }
    param.add_param(test_param)
    param.set_param(param_name='app-version', value='1.0.0')
    
    with pytest.raises(ValueError, match="Cannot modify immutable parameter 'app-version'"):
        param.unset_param(param_name='app-version')


def test_unset_param_immutable_default_false():
    """
    Test unsetting succeeds when PARAM_IMMUTABLE not specified.
    Parameters without immutability flag should be freely removable.
    This validates default behavior (not immutable).
    """
    test_param = {
        PARAM_NAME: 'temp-value',
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    param.add_param(test_param)
    param.set_param(param_name='temp-value', value='data')
    
    # Should not raise
    param.unset_param(param_name='temp-value')
    
    assert config.get_config_value('temp-value') is None


def test_unset_param_already_unset():
    """
    Test unsetting an already-unset parameter is a no-op.
    Should not raise error when value doesn't exist.
    This validates graceful handling of unset on unset params.
    """
    test_param = {
        PARAM_NAME: 'optional-value',
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    param.add_param(test_param)
    
    # No error when unsetting unset param
    param.unset_param(param_name='optional-value')
    
    assert config.get_config_value('optional-value') is None


def test_remove_config_value():
    """
    Test config.remove_config_value() helper directly.
    Should remove key from config dict.
    This validates the underlying storage operation.
    """
    config.set_config_value('test-key', 'test-value')
    assert config.get_config_value('test-key') == 'test-value'
    
    config.remove_config_value('test-key')
    
    assert config.get_config_value('test-key') is None


def test_has_config_value():
    """
    Test config.has_config_value() helper directly.
    Should return True for existing keys, False otherwise.
    This validates the existence check operation.
    """
    config.set_config_value('existing-key', 'value')
    
    assert config.has_config_value('existing-key') is True
    assert config.has_config_value('nonexistent-key') is False


def test_check_immutable_not_immutable():
    """
    Test _check_immutable() allows operation when PARAM_IMMUTABLE not set.
    Should return silently without raising error.
    This validates that non-immutable params pass the check.
    """
    test_param = {
        PARAM_NAME: 'normal-param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    param.add_param(test_param)
    param.set_param(param_name='normal-param', value='data')
    
    # Should not raise
    param._check_immutable(test_param)


def test_check_immutable_no_value():
    """
    Test _check_immutable() allows operation when immutable but no value exists yet.
    Should return silently to allow initial assignment.
    This validates that immutable params can be set initially.
    """
    test_param = {
        PARAM_NAME: 'immutable-param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_IMMUTABLE: True,
    }
    param.add_param(test_param)
    
    # Should not raise (no value set yet)
    param._check_immutable(test_param)


def test_check_immutable_has_value():
    """
    Test _check_immutable() blocks operation when immutable and value exists.
    Should raise ValueError to prevent modification.
    This validates that immutable params are protected once set.
    """
    test_param = {
        PARAM_NAME: 'locked-param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_IMMUTABLE: True,
    }
    param.add_param(test_param)
    param.set_param(param_name='locked-param', value='initial')
    
    with pytest.raises(ValueError, match="Cannot modify immutable parameter 'locked-param'"):
        param._check_immutable(test_param)


def test_reset_param_with_default():
    """
    Test reset_param() sets parameter to default value when PARAM_DEFAULT exists.
    Should call set_param() with the default value.
    This validates reset behavior with default values.
    """
    test_param = {
        PARAM_NAME: 'counter',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 0,
    }
    param.add_param(test_param)
    param.set_param(param_name='counter', value=42)
    
    assert config.get_config_value('counter') == 42
    
    param.reset_param(param_name='counter')
    
    assert config.get_config_value('counter') == 0


def test_reset_param_without_default():
    """
    Test reset_param() unsets parameter when PARAM_DEFAULT does not exist.
    Should call unset_param() to remove the value.
    This validates reset behavior without default values.
    """
    test_param = {
        PARAM_NAME: 'temp-data',
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    param.add_param(test_param)
    param.set_param(param_name='temp-data', value='temporary')
    
    assert config.get_config_value('temp-data') == 'temporary'
    
    param.reset_param(param_name='temp-data')
    
    assert config.get_config_value('temp-data') is None


def test_reset_param_by_param_name():
    """
    Test resetting parameter using param_name.
    Should work with parameter name resolution.
    This validates basic reset functionality.
    """
    test_param = {
        PARAM_NAME: 'setting',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'default',
    }
    param.add_param(test_param)
    param.set_param(param_name='setting', value='modified')
    
    param.reset_param(param_name='setting')
    
    assert config.get_config_value('setting') == 'default'


def test_reset_param_by_bind_name():
    """
    Test resetting parameter using bind_name.
    Should work with config bind name resolution.
    This validates flexible resolution with bind_name for reset.
    """
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_bind',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 10,
    }
    param.add_param(test_param)
    param.set_param(param_name='my-param', value=20)
    
    param.reset_param(bind_name='my_bind')
    
    assert config.get_config_value('my_bind') == 10


def test_reset_param_by_alias():
    """
    Test resetting parameter using alias.
    Should work with CLI alias resolution.
    This validates flexible resolution with alias for reset.
    """
    test_param = {
        PARAM_NAME: 'debug',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False,
        'aliases': ['--debug', '-d'],
    }
    param.add_param(test_param)
    param.set_param(param_name='debug', value=True)
    
    param.reset_param(alias='--debug')
    
    assert config.get_config_value('debug') is False


def test_reset_param_not_found():
    """
    Test resetting a non-existent parameter raises ValueError.
    Should provide clear error message.
    This validates error handling for missing parameters in reset.
    """
    with pytest.raises(ValueError, match="Parameter 'missing' not found"):
        param.reset_param(param_name='missing')


def test_reset_param_immutable():
    """
    Test resetting an immutable parameter raises ValueError.
    Immutable parameters cannot be reset (would modify/remove value).
    This validates immutability protection for reset operations.
    """
    test_param = {
        PARAM_NAME: 'version',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_IMMUTABLE: True,
        PARAM_DEFAULT: '1.0.0',
    }
    param.add_param(test_param)
    param.set_param(param_name='version', value='1.0.0')
    
    # Try to reset (which would call set_param with default, but value exists)
    with pytest.raises(ValueError, match="Cannot modify immutable parameter 'version'"):
        param.reset_param(param_name='version')
