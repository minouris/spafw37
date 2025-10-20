from spafw37.config import set_config_file
import spafw37.configure

set_config_file('config.json')

if __name__ == "__main__":
    import sys
    import spafw37.cli as cli
    # Pass user-provided command-line arguments (excluding program name)
    cli.handle_cli_args(sys.argv[1:])