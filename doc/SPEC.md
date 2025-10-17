# Simple App Framework

## Features

Provides:
    1. A command line interpreter that allows the user to:
        - set switches and parameters
        - issue commands to the application
    2. Store configuration values in a way that makes them available to the entire application
    3. Logging, including a TRACE log level
    4. Access to a data backend with roll-up versioning

### Command Switches and Params

Note: the following defines a param schema and template examples. Implementations must accept param definitions at runtime and register CLI aliases dynamically; the example aliases (e.g. `--simple-param`) are templates, not required literal flags.

#### Schema
- `name` (unique name)
- `description`
- `bind_to` (binds to a config param)
- `persisted` 
    - save to disk if set, load from disk if not
    - Independant of `--save-config` and `--load-config`
        - Saves and loads automatically to a global storage file, `config.cfg` (or other file denoted by `config.config_file`)
- `type` 
    - one of:
        - `string`
        - `number`
        - `toggle` 
            - takes no param, switches a setting on or off. sets bound config value to opposite of default
        - `list` 
            - takes multiple values, either from this param being passed multiple times, or from more than one value in a row after a single param, e.g. `--input file1 file2 file3` or `-i file1 -i file2 -i file3`
- `default` 
    - if param not specified or loaded from disk, use this
- `aliases[]` 
    - CLI forms that set the param, e.g. `--param`, `--param=VALUE`, `-p`. `=VALUE` indicates the long form accepts either `--param=VALUE` or `--param VALUE`. For short flags use `-p VALUE`. `VALUE` is a placeholder.
For list params, aliases may be repeated (`-i file1 -i file2`) or accept multiple values after a single alias (`--input file1 file2`).
- `required` (whether this param must always be specified)
- `xor_with` (list of param names, only one can be used)

#### Hard Coded Params

These params are present by default:

- `--save-config=file`
- `--load-config=file`

```python

builtin_commands 
commands.register()
```

save and load files, overridden by manual settings

#### Basics

Example:
```python
simple_param = {
    'name': 'simple_param',
    'description': 'A simple parameter with a single simple value',
    'bind_to': 'simple_p',
    'type': 'string',
    'default': 'a simple value!',
    'aliases': [ '--simple-param', '-sp'],
    'required': False
}
```
Describes a simple parameter with a single string value that is assigned to `config['simple_p']`. If not on the command line, then `config['simple_p']` will be assigned the value 'a simple value!' from the `default` param.

It can be called with either `--simple-param "A value"`, `--simple-param="A value"` or `-sp "A value"`:

```bash
bash python -m spafw37 --simple-param "A value"
```

```bash
bash python -m spafw37 --simple-param="A value"
```

```bash
bash python -m spafw37 -sp "A value"
```

#### Numeric Param

Example:
```python
simple_param = {
    'name': 'numeric_param',
    'description': 'A simple parameter with a single numeric value',
    'bind_to': 'number_p',
    'type': 'number',
    'default': 'a numeric value!',
    'aliases': [ '--number-param', '-num'],
    'required': False
}
```
Identical to the previous example, except the value would be validated as a number.


### Config Store

Populated by params, or loaded from file.

Contains a single `dict`, `config` populated by name:value pairs, where values can be single values or lists.

Example:

```python
config = {
    'db_dir': '.data',
    'log_dir': 'logs',
    'input_files': [
        'file1',
        'file2',
        'file3'
    ]
}
```

Values can either be set at runtime, set by command line params, or loaded from a file.

Should have two functions for loading / saving config values from files, `load_config(file : str) -> dict` and `save_config(file: str, dict: config)`.

`load_config(file: str)` will run on `__init__` to load any data from the file denoted by `config.config_file` ("the config file" hereafter )if that file exists. Any params on the command line defined with the `persisted` flag will be saved to the config file using `save_config(file: str, dict: config)` when they are set.

The `config` module should be accessible from anywhere in the app. 