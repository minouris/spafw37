from spafw37 import config, param
from spafw37.config import _persistent_config
from spafw37.config_consts import (
    PARAM_PERSISTENCE_ALWAYS, 
    PARAM_PERSISTENCE_NEVER, 
    PARAM_NAME, 
    PARAM_BIND_TO, 
    PARAM_RUNTIME_ONLY, 
    PARAM_TYPE, 
    PARAM_PERSISTENCE, 
    PARAM_DEFAULT)

def test_set_and_get_config_value():
    test_param = {
        PARAM_NAME: "test_param",
        PARAM_BIND_TO: "test_param_bind",
        PARAM_TYPE: "string"
    }
    test_value = "test_value"
    config.set_config_value(test_param, test_value)
    retrieved_value = config.get_config_value("test_param_bind")
    assert retrieved_value == test_value

def test_set_config_list_value():
    test_param = {
        PARAM_NAME: "list_param",
        PARAM_BIND_TO: "list_param_bind",
        PARAM_TYPE: "list"
    }
    config.set_config_value(test_param, "value1")
    config.set_config_value(test_param, ["value2", "value3"])
    retrieved_value = config.get_config_value("list_param_bind")
    assert retrieved_value == ["value1", "value2", "value3"]

def test_non_persistent_param():
    test_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_BIND_TO: "non_persistent_param_bind",
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
        PARAM_BIND_TO: "user_param_bind",
        PARAM_TYPE: "string"
    }
    file_param_in = {
        PARAM_NAME: config.CONFIG_INFILE_PARAM,
        PARAM_BIND_TO: config.CONFIG_INFILE_PARAM,
        PARAM_TYPE: "string"
    }
    file_param_out = {
        PARAM_NAME: config.CONFIG_OUTFILE_PARAM,
        PARAM_BIND_TO: config.CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: "string"
    }
    test_value = "user_value"
    config.set_config_value(test_param, test_value)
    config.set_config_value(file_param_out, str(tmp_path / "user_config.json"))
    
    config_file = tmp_path / "user_config.json"
    config.save_user_config()
    
    # Clear current config and load from file
    config._config = {}
    config.set_config_value(file_param_in, str(tmp_path / "user_config.json"))
    config.load_user_config()
    
    retrieved_value = config.get_config_value("user_param_bind")
    assert retrieved_value == test_value

def test_filter_temporary_config():
    temp_param = {
        PARAM_NAME: "temp_param",
        PARAM_BIND_TO: "temp_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_BIND_TO: "persistent_param_bind",
        PARAM_TYPE: "string"
    }
    config.set_config_value(temp_param, "temp_value")
    config.set_config_value(persistent_param, "persistent_value")
    
    full_config = config._config
    filtered_config = config.filter_temporary_config(full_config)
    
    assert "temp_param_bind" not in filtered_config
    assert "persistent_param_bind" in filtered_config
    assert filtered_config["persistent_param_bind"] == "persistent_value"

def test_manage_config_persistence():
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_BIND_TO: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    non_persistent_param = {
        PARAM_NAME: "non_persistent_param",
        PARAM_BIND_TO: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    config.set_config_value(persistent_param, "persistent_value")
    config.set_config_value(non_persistent_param, "non_persistent_value")

    assert non_persistent_param[PARAM_BIND_TO] in config._non_persisted_config_names
    assert _persistent_config.get(persistent_param[PARAM_BIND_TO]) == "persistent_value"

def test_load_persistent_config(tmp_path):
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_BIND_TO: "persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
    config.set_config_value(persistent_param, "persistent_value")
    
    # Save persistent config to file
    persistent_config_file = tmp_path / "persistent_config.json"
    config._config_file = str(persistent_config_file)
    config.save_persistent_config()
    
    # Clear current config and persistent config
    config._config = {}
    _persistent_config.clear()
    
    # Load persistent config from file
    config.load_persistent_config()
    
    retrieved_value = config.get_config_value("persistent_param_bind")
    assert retrieved_value == "persistent_value"

def test_save_persistent_config(tmp_path):
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_BIND_TO: "persistent_param_bind",
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
        PARAM_BIND_TO: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_BIND_TO: "persistent_param_bind",
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
        PARAM_BIND_TO: "non_persistent_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    test_value = "should_not_persist"
    config.set_config_value(test_param, test_value)
    assert "non_persistent_param_bind" not in _persistent_config

def test_non_persistent_param_not_saved_in_user_save(tmp_path):
    test_param = {
        PARAM_NAME: "user_param",
        PARAM_BIND_TO: "user_param_bind",
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    file_param_out = {
        PARAM_NAME: config.CONFIG_OUTFILE_PARAM,
        PARAM_BIND_TO: config.CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
    persistent_param = {
        PARAM_NAME: "persistent_param",
        PARAM_BIND_TO: "persistent_param_bind",
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
    config._config = {}
    config.set_config_value({
        PARAM_NAME: config.CONFIG_INFILE_PARAM,
        PARAM_BIND_TO: config.CONFIG_INFILE_PARAM,
        PARAM_TYPE: "string",
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }, str(config_file))
    config.load_user_config()
    retrieved_value = config.get_config_value("user_param_bind")
    assert retrieved_value is None
    retrieved_persistent_value = config.get_config_value("persistent_param_bind")
    assert retrieved_persistent_value == "persistent_value"

# test that a RUNTIME_ONLY param is marked as NEVER persisted
def test_runtime_only_param_set_never_persisted():
    runtime_only_param = {
        PARAM_NAME: "runtime_only_param",
        PARAM_BIND_TO: "runtime_only_param_bind",
        PARAM_TYPE: "string",
        PARAM_RUNTIME_ONLY: True
    }
    param.add_param(runtime_only_param)
    assert config.is_persistence_never(runtime_only_param) is True