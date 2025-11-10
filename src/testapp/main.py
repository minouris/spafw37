from spafw37.config import set_config_file

set_config_file('config.json')

if __name__ == "__main__":
    from spafw37 import core
    core.run_cli()