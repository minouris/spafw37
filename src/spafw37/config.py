# Config dict to hold runtime parameters
_config = {
}


def get_config_value(name):
    return _config.get(name)

def set_config_value(name, value):
    _config[name] = value


def set_config_list_value(value, bind_name):
    if bind_name not in _config:
        _config[bind_name] = []
    if isinstance(value, list):
        _config[bind_name].extend(value)
    else:
        _config[bind_name].append(value)


def list_config_params():
    return list(_config.keys())

def list_config_items():
    return _config.items()


def update_config(new_config):
    _config.update(new_config)