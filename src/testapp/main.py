from spafw37.config import set_config_file
import spafw37.configure

set_config_file('config.json')

if __name__ == "__main__":
    import sys
    import spafw37.cli as cli
    from spafw37.command import CommandParameterError
    from spafw37.help import display_all_help, display_command_help
    
    # Pass user-provided command-line arguments (excluding program name)
    try:
        cli.handle_cli_args(sys.argv[1:])
    except CommandParameterError as e:
        # On command parameter error, display help for that specific command
        print(f"Error: {e}")
        print()
        if e.command_name:
            display_command_help(e.command_name)
        else:
            display_all_help()
        sys.exit(1)
    except ValueError as e:
        # On other errors, display general help
        print(f"Error: {e}")
        print()
        display_all_help()
        sys.exit(1)