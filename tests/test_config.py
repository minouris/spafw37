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
    test_param = {
        PARAM_NAME: "test_param",
        PARAM_CONFIG_NAME: "test_param_bind",
        PARAM_TYPE: "string"
    }
    test_value = "test_value"
    config.set_config_value(test_param, test_value)
    retrieved_value = spafw37.config.get_config_value("test_param_bind")
    assert retrieved_value == test_value

def test_set_config_list_value():
    test_param = {
        PARAM_NAME: "list_param",
        PARAM_CONFIG_NAME: "list_param_bind",
        PARAM_TYPE: "list"
    }
    config.set_config_value(test_param, "value1")
    config.set_config_value(test_param, ["value2", "value3"])
    retrieved_value = spafw37.config.get_config_value("list_param_bind")
    assert retrieved_value == ["value1", "value2", "value3"]

def test_non_persistent_param():
    test_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    test_value = "should_not_persist"
    config.set_config_value(test_param, test_value)
    assert "non_persistent_param_bind" in config._non_persisted_config_names

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
    test_param = {
        PARAM_NAME: "user_param",
        PARAM_CONFIG_NAME: "user_param_bind",
        PARAM_TYPE: "string"
    }
    file_param_in = {
        PARAM_NAME: config.CONFIG_INFILE_PARAM,
        PARAM_CONFIG_NAME: config.CONFIG_INFILE_PARAM,
        PARAM_TYPE: "string"
    }
    file_param_out = {
        PARAM_NAME: config.CONFIG_OUTFILE_PARAM,
        PARAM_CONFIG_NAME: config.CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: "string"
    }
    test_value = "user_value"
    config.set_config_value(test_param, test_value)
    config.set_config_value(file_param_out, str(tmp_path / "user_config.json"))
    
    config_file = tmp_path / "user_config.json"
    config.save_user_config()
    
    # Clear current config and load from file
    spafw37.config._config = {}
    config.set_config_value(file_param_in, str(tmp_path / "user_config.json"))
    config.load_user_config()
    
    retrieved_value = spafw37.config.get_config_value("user_param_bind")
    assert retrieved_value == test_value

def test_filter_temporary_config():
    temp_param = {
        PARAM_NAME: "temp_param",
        PARAM_CONFIG_NAME: "temp_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "string"
    }
    config.set_config_value(temp_param, "temp_value")
    config.set_config_value(persistent_param, "persistent_value")
    
    full_config = spafw37.config._config
    filtered_config = config.filter_temporary_config(full_config)
    
    assert "temp_param_bind" not in filtered_config
    assert "persistent_param_bind" in filtered_config
    assert filtered_config["persistent_param_bind"] == "persistent_value"

def test_manage_config_persistence():
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    non_persistent_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    config.set_config_value(persistent_param, "persistent_value")
    config.set_config_value(non_persistent_param, "non_persistent_value")

    assert non_persistent_param[PARAM_CONFIG_NAME] in config._non_persisted_config_names
    assert _persistent_config.get(persistent_param[PARAM_CONFIG_NAME]) == "persistent_value"

def test_load_persistent_config(tmp_path):
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    config.set_config_value(persistent_param, "persistent_value")
    
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
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    config.set_config_value(persistent_param, "persistent_value")
    
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
    non_persistent_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    config.set_config_value(persistent_param, "persistent_value")
    config.set_config_value(non_persistent_param, "non_persistent_value")
    
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
    test_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_CONFIG_NAME: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    test_value = "should_not_persist"
    config.set_config_value(test_param, test_value)
    assert "non_persistent_param_bind" not in _persistent_config

def test_non_persistent_param_not_saved_in_user_save(tmp_path):
    test_param = {
        PARAM_NAME: "user_param",
        PARAM_CONFIG_NAME: "user_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    file_param_out = {
        PARAM_NAME: config.CONFIG_OUTFILE_PARAM,
        PARAM_CONFIG_NAME: config.CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_CONFIG_NAME: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    config_file = tmp_path / "user_config.json"
    test_value = "user_value"
    config.set_config_value(test_param, test_value)
    config.set_config_value(persistent_param, "persistent_value")
    config.set_config_value(file_param_out, str(config_file))
    config.save_user_config()
    # Clear current config and load from file
    spafw37.config._config = {}
    config.set_config_value({
        PARAM_NAME: config.CONFIG_INFILE_PARAM,
        PARAM_CONFIG_NAME: config.CONFIG_INFILE_PARAM,
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }, str(config_file))
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
