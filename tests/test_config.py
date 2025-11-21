from spafw37 import config_func as config, param
import spafw37.config
from spafw37.config_func import _persistent_config
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PERSISTENCE_ALWAYS,
    PARAM_PERSISTENCE_NEVER,
    PARAM_CONFIG_NAME,
    PARAM_RUNTIME_ONLY,
    PARAM_TYPE,
    PARAM_PERSISTENCE,
    PARAM_DEFAULT,
)

def test_set_and_get_config_value():
    """Test setting and retrieving parameter values through the param API.
    
    This test verifies that parameter values can be set and retrieved correctly
    through the param layer, which is the proper interface to config.
    
    The test expects the value to be retrievable from the config dict using the
    bind name because params are the authoritative interface to configuration.
    """
    test_param = {
        PARAM_NAME: "test_param",
        PARAM_CONFIG_NAME: "test_param_bind",
        PARAM_TYPE: "text"
    }
    param.add_param(test_param)
    test_value = "test_value"
    param.set_param(param_name="test_param", value=test_value)
    retrieved_value = spafw37.config.get_config_value("test_param_bind")
    assert retrieved_value == test_value

def test_set_config_list_value():
    """Test setting list parameter values through the param API.
    
    This test verifies that list parameter values can be set multiple times
    through the param layer. The test expects values to accumulate in the list.
    
    This validates that the param-to-config data flow works correctly for list types.
    """
    test_param = {
        PARAM_NAME: "list_param",
        PARAM_CONFIG_NAME: "list_param_bind",
        PARAM_TYPE: "list"
    }
    param.add_param(test_param)
    param.join_param(param_name="list_param", value="value1")
    param.join_param(param_name="list_param", value=["value2", "value3"])
    retrieved_value = spafw37.config.get_config_value("list_param_bind")
    assert retrieved_value == ["value1", "value2", "value3"]

def test_non_persistent_param():
    """Test that non-persistent params are correctly identified.
    
    This test verifies that parameters marked with PARAM_PERSISTENCE_NEVER are
    identified as non-persistent through the param API query function.
    
    This validates the unidirectional query flow from config layer to param layer.
    """
    test_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    param.add_param(test_param)
    test_value = "should_not_persist"
    param.set_param(param_name="non_persistent_param", value=test_value)
    non_persisted_names = param.get_non_persisted_config_names()
    assert "non_persistent_param_bind" in non_persisted_names

def test_load_config_file(tmp_path):
    config_data = {
        "param1": "value1",
        "param2": 42
    }
    config_file = tmp_path / "config.json"
    with open(config_file, 'w') as f:
        import json
        json.dump(config_data, f)
    
    loaded_config = config.load_config(str(config_file))
    assert loaded_config == config_data

def test_save_and_load_user_config(tmp_path):
    """Test saving and loading user configuration through param API.
    
    This test verifies that user configuration can be saved and loaded correctly
    through the param layer, validating the complete param-to-config data flow.
    
    This validates that persistence management works correctly for user configs.
    """
    test_param = {
        PARAM_NAME: "user_param",
        PARAM_CONFIG_NAME: "user_param_bind",
        PARAM_TYPE: "text"
    }
    param.add_param(test_param)
    test_value = "user_value"
    param.set_param(param_name="user_param", value=test_value)
    spafw37.config.set_config_value(config.CONFIG_OUTFILE_PARAM, str(tmp_path / "user_config.json"))
    
    config_file = tmp_path / "user_config.json"
    config.save_user_config()
    
    # Clear current config and load from file
    spafw37.config._config = {}
    spafw37.config.set_config_value(config.CONFIG_INFILE_PARAM, str(tmp_path / "user_config.json"))
    config.load_user_config()
    
    retrieved_value = spafw37.config.get_config_value("user_param_bind")
    assert retrieved_value == test_value

def test_filter_temporary_config():
    """Test filtering temporary config through param API.
    
    This test verifies that temporary (non-persistent) parameters are correctly
    filtered out when querying through the config layer using param metadata.
    
    This validates the unidirectional query flow for persistence filtering.
    """
    temp_param = {
        PARAM_NAME: "temp_param",
        PARAM_CONFIG_NAME: "temp_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "text"
    }
    param.add_params([temp_param, persistent_param])
    param.set_param(param_name="temp_param", value="temp_value")
    param.set_param(param_name="persistent_param", value="persistent_value")
    
    full_config = spafw37.config._config
    filtered_config = config.filter_temporary_config(full_config)
    
    assert "temp_param_bind" not in filtered_config
    assert "persistent_param_bind" in filtered_config
    assert filtered_config["persistent_param_bind"] == "persistent_value"

def test_manage_config_persistence():
    """Test persistence management through param API.
    
    This test verifies that persistent and non-persistent parameters are correctly
    tracked through the param layer's notification system to config_func.
    
    This validates the unidirectional notification flow for persistence tracking.
    """
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    non_persistent_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    param.add_params([persistent_param, non_persistent_param])
    param.set_param(param_name="persistent_param", value="persistent_value")
    param.set_param(param_name="non_persistent_param", value="non_persistent_value")

    non_persisted_names = param.get_non_persisted_config_names()
    assert non_persistent_param[PARAM_CONFIG_NAME] in non_persisted_names
    assert _persistent_config.get(persistent_param[PARAM_CONFIG_NAME]) == "persistent_value"

def test_load_persistent_config(tmp_path):
    """Test loading persistent config through param API.
    
    This test verifies that persistent configuration is correctly loaded from
    file and accessible through the config layer after being set via param API.
    
    This validates the complete persistence cycle through the param layer.
    """
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    param.add_param(persistent_param)
    param.set_param(param_name="persistent_param", value="persistent_value")
    
    # Save persistent config to file
    persistent_config_file = tmp_path / "persistent_config.json"
    config._config_file = str(persistent_config_file)
    config.save_persistent_config()
    
    # Clear current config and persistent config
    spafw37.config._config = {}
    _persistent_config.clear()
    
    # Load persistent config from file
    config.load_persistent_config()
    
    retrieved_value = spafw37.config.get_config_value("persistent_param_bind")
    assert retrieved_value == "persistent_value"

def test_save_persistent_config(tmp_path):
    """Test saving persistent config through param API.
    
    This test verifies that persistent configuration is correctly saved to file
    when set through the param API, validating the persistence notification flow.
    
    This validates that PARAM_PERSISTENCE_ALWAYS triggers correct file saving.
    """
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    param.add_param(persistent_param)
    param.set_param(param_name="persistent_param", value="persistent_value")
    
    # Save persistent config to file
    persistent_config_file = tmp_path / "persistent_config.json"
    config._config_file = str(persistent_config_file)
    config.save_persistent_config()
    
    # Load the saved file to verify contents
    with open(persistent_config_file, 'r') as f:
        import json
        saved_data = json.load(f)
    
    assert saved_data.get("persistent_param_bind") == "persistent_value"

def test_not_save_non_persistent_config(tmp_path):
    """Test that non-persistent params are not saved through param API.
    
    This test verifies that parameters marked PARAM_PERSISTENCE_NEVER are correctly
    excluded from persistent config files when saved through the param layer.
    
    This validates the persistence filtering logic in the notification flow.
    """
    non_persistent_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    param.add_params([persistent_param, non_persistent_param])
    param.set_param(param_name="persistent_param", value="persistent_value")
    param.set_param(param_name="non_persistent_param", value="non_persistent_value")
    
    # Save persistent config to file
    persistent_config_file = tmp_path / "persistent_config.json"
    config._config_file = str(persistent_config_file)
    config.save_persistent_config()
    
    # Load the saved file to verify contents
    with open(persistent_config_file, 'r') as f:
        import json
        saved_data = json.load(f)
    
    assert "non_persistent_param_bind" not in saved_data
    assert saved_data.get("persistent_param_bind") == "persistent_value"

def test_non_persistent_param_not_in_persistent_config():
    """Test that non-persistent params don't appear in persistent config dict.
    
    This test verifies that parameters marked PARAM_PERSISTENCE_NEVER are not
    tracked in the _persistent_config dict when set through the param API.
    
    This validates that the notification system correctly filters non-persistent params.
    """
    test_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    param.add_param(test_param)
    test_value = "should_not_persist"
    param.set_param(param_name="non_persistent_param", value=test_value)
    assert "non_persistent_param_bind" not in _persistent_config

def test_non_persistent_param_not_saved_in_user_save(tmp_path):
    """Test that non-persistent params are excluded from user config saves.
    
    This test verifies that parameters marked PARAM_PERSISTENCE_NEVER are correctly
    excluded from user config files saved via --save-config through the param API.
    
    This validates the complete filtering flow for user config persistence.
    """
    test_param = {
        PARAM_NAME: "user_param",
        PARAM_CONFIG_NAME: "user_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "text",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    param.add_params([test_param, persistent_param])
    config_file = tmp_path / "user_config.json"
    test_value = "user_value"
    param.set_param(param_name="user_param", value=test_value)
    param.set_param(param_name="persistent_param", value="persistent_value")
    spafw37.config.set_config_value(config.CONFIG_OUTFILE_PARAM, str(config_file))
    config.save_user_config()
    # Clear current config and load from file
    spafw37.config._config = {}
    spafw37.config.set_config_value(config.CONFIG_INFILE_PARAM, str(config_file))
    config.load_user_config()
    retrieved_value = spafw37.config.get_config_value("user_param_bind")
    assert retrieved_value is None
    retrieved_persistent_value = spafw37.config.get_config_value("persistent_param_bind")
    assert retrieved_persistent_value == "persistent_value"

# test that a RUNTIME_ONLY param is marked as NEVER persisted
def test_runtime_only_param_set_never_persisted():
    runtime_only_param = {
        PARAM_NAME: "runtime_only_param",
        PARAM_CONFIG_NAME: "runtime_only_param_bind",
        PARAM_TYPE: "string",
        PARAM_RUNTIME_ONLY: True
    }
    param.add_param(runtime_only_param)
    # Get the activated param from _params
    activated_param = param._params["runtime_only_param"]
    assert param.is_persistence_never(activated_param) is True


# Tests for typed config getters

def test_get_config_int():
    """Test get_config_int with various input types."""
    # Test with integer value
    spafw37.config.set_config_value('test_int', 42)
    assert spafw37.config.get_config_int('test_int') == 42
    
    # Test with string that can be converted to int
    spafw37.config.set_config_value('test_int_str', '123')
    assert spafw37.config.get_config_int('test_int_str') == 123
    
    # Test with None (should return default)
    assert spafw37.config.get_config_int('nonexistent') == 0
    assert spafw37.config.get_config_int('nonexistent', 99) == 99


def test_get_config_str():
    """Test get_config_str with various input types."""
    # Test with string value
    spafw37.config.set_config_value('test_str', 'hello')
    assert spafw37.config.get_config_str('test_str') == 'hello'
    
    # Test with number that can be converted to string
    spafw37.config.set_config_value('test_num_str', 456)
    assert spafw37.config.get_config_str('test_num_str') == '456'
    
    # Test with None (should return default)
    assert spafw37.config.get_config_str('nonexistent') == ''
    assert spafw37.config.get_config_str('nonexistent', 'default') == 'default'


def test_get_config_bool():
    """Test get_config_bool with various input types."""
    # Test with boolean value
    spafw37.config.set_config_value('test_bool_true', True)
    assert spafw37.config.get_config_bool('test_bool_true') is True
    
    spafw37.config.set_config_value('test_bool_false', False)
    assert spafw37.config.get_config_bool('test_bool_false') is False
    
    # Test with truthy/falsy values
    spafw37.config.set_config_value('test_truthy', 1)
    assert spafw37.config.get_config_bool('test_truthy') is True
    
    spafw37.config.set_config_value('test_falsy', 0)
    assert spafw37.config.get_config_bool('test_falsy') is False
    
    # Test with None (should return default)
    assert spafw37.config.get_config_bool('nonexistent') is False
    assert spafw37.config.get_config_bool('nonexistent', True) is True


def test_get_config_float():
    """Test get_config_float with various input types."""
    # Test with float value
    spafw37.config.set_config_value('test_float', 3.14)
    assert spafw37.config.get_config_float('test_float') == 3.14
    
    # Test with int that can be converted to float
    spafw37.config.set_config_value('test_int_float', 42)
    assert spafw37.config.get_config_float('test_int_float') == 42.0
    
    # Test with string that can be converted to float
    spafw37.config.set_config_value('test_str_float', '2.718')
    assert spafw37.config.get_config_float('test_str_float') == 2.718
    
    # Test with None (should return default)
    assert spafw37.config.get_config_float('nonexistent') == 0.0
    assert spafw37.config.get_config_float('nonexistent', 9.99) == 9.99


def test_get_config_list():
    """Test get_config_list with various input types."""
    # Test with list value
    spafw37.config.set_config_value('test_list', ['a', 'b', 'c'])
    assert spafw37.config.get_config_list('test_list') == ['a', 'b', 'c']
    
    # Test with single value (should be wrapped in list)
    spafw37.config.set_config_value('test_single', 'single')
    assert spafw37.config.get_config_list('test_single') == ['single']
    
    # Test with None (should return empty list)
    assert spafw37.config.get_config_list('nonexistent') == []
    
    # Test with custom default
    assert spafw37.config.get_config_list('nonexistent', ['default']) == ['default']


def test_get_config_dict():
    """Test get_config_dict function retrieves dict configuration values.
    
    The function should return the dict value when present, an empty dict when
    value is None and no default provided, or raise ValueError when value is not
    a dict. This validates the dict parameter support in the config system.
    """
    # Test with dict value
    spafw37.config.set_config_value('test_dict', {'key': 'value'})
    assert spafw37.config.get_config_dict('test_dict') == {'key': 'value'}
    
    # Test with None (should return empty dict)
    assert spafw37.config.get_config_dict('nonexistent') == {}
    
    # Test with custom default
    assert spafw37.config.get_config_dict('nonexistent', {'default': 'val'}) == {'default': 'val'}
    
    # Test with non-dict value (should raise ValueError) - this covers line 127
    spafw37.config.set_config_value('test_string', 'not_a_dict')
    try:
        spafw37.config.get_config_dict('test_string')
        assert False, "Should have raised ValueError"
    except ValueError as error:
        assert "not a dictionary" in str(error)



def test_load_config_unicode_decode_error(tmp_path):
    """Test that load_config handles Unicode decode errors properly.
    
    When a config file contains invalid Unicode characters, load_config should
    raise UnicodeDecodeError with a descriptive message. This validates error
    handling for corrupted or binary files (line 108).
    """
    config_file = tmp_path / "invalid_unicode.json"
    
    # Write invalid UTF-8 bytes
    with open(config_file, 'wb') as file:
        file.write(b'\x80\x81\x82')
    
    # Attempt to load should raise UnicodeDecodeError
    try:
        config.load_config(str(config_file))
        assert False, "Should have raised UnicodeDecodeError"
    except UnicodeDecodeError as error:
        assert config_file.name in str(error)
