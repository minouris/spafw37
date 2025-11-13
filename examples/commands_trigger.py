"""
Parameter-Triggered Commands Example

Demonstrates COMMAND_TRIGGER_PARAM - commands automatically invoked when a parameter is set.

When a parameter is set on the command line, commands with COMMAND_TRIGGER_PARAM matching
that parameter will be automatically queued and executed. This is useful for initialization,
setup tasks, or loading resources that depend on specific parameters being provided.

Key Concepts:
- COMMAND_TRIGGER_PARAM: Parameter name that triggers the command
- Triggered commands run automatically before explicitly queued commands
- Useful for setup/initialization tasks
- Can be combined with COMMAND_REQUIRED_PARAMS for validation

Usage Examples:
    # Show help
    python commands_trigger.py --help
    
    # Normal processing without plugins
    python commands_trigger.py process
    
    # Setting plugin-dir triggers load-plugins command automatically
    python commands_trigger.py process --plugin-dir ./plugins
    
    # Setting config-file triggers load-config command automatically
    python commands_trigger.py process --config-file settings.json
    
    # Both triggers can fire together
    python commands_trigger.py process --plugin-dir ./plugins --config-file settings.json
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_TRIGGER_PARAM,
    COMMAND_REQUIRED_PARAMS,
)


def setup():
    """Configure parameters and commands with triggers."""
    
    # Define parameters that can trigger commands
    params = [
        {
            PARAM_NAME: 'plugin-dir',
            PARAM_DESCRIPTION: 'Directory containing plugins to load',
            PARAM_ALIASES: ['--plugin-dir', '--plugins', '-p'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
        },
        {
            PARAM_NAME: 'config-file',
            PARAM_DESCRIPTION: 'Configuration file to load',
            PARAM_ALIASES: ['--config-file', '--config', '-c'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
        },
        {
            PARAM_NAME: 'data-source',
            PARAM_DESCRIPTION: 'Data source URL or path',
            PARAM_ALIASES: ['--data-source', '--data', '-d'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
        },
    ]
    
    # Command automatically triggered when plugin-dir is set
    def load_plugins():
        """Load plugins from the specified directory."""
        plugin_dir = spafw37.get_config_str('plugin-dir')
        print(f"[TRIGGERED] Loading plugins from: {plugin_dir}")
        print("  - data_transformer.py")
        print("  - output_formatter.py")
        print("  - validation_rules.py")
        print("Plugins loaded successfully!")
        print()
    
    # Command automatically triggered when config-file is set
    def load_config():
        """Load configuration from the specified file."""
        config_file = spafw37.get_config_str('config-file')
        print(f"[TRIGGERED] Loading configuration from: {config_file}")
        print("  Setting: timeout = 30s")
        print("  Setting: max_retries = 3")
        print("  Setting: output_format = json")
        print("Configuration loaded successfully!")
        print()
    
    # Command automatically triggered when data-source is set
    def connect_data_source():
        """Connect to the specified data source."""
        data_source = spafw37.get_config_str('data-source')
        print(f"[TRIGGERED] Connecting to data source: {data_source}")
        print("  Connection established")
        print("  Authentication verified")
        print("  Ready to process data")
        print()
    
    # Regular command that users explicitly invoke
    def process():
        """Process data with optional plugins and configuration."""
        print("[PROCESS] Starting data processing...")
        
        # Check if optional features were triggered
        if spafw37.get_config_str('plugin-dir'):
            print("  Processing with loaded plugins")
        if spafw37.get_config_str('config-file'):
            print("  Using loaded configuration")
        if spafw37.get_config_str('data-source'):
            print("  Reading from connected data source")
        
        print("  Processing complete!")
        print()
    
    def analyze():
        """Analyze results."""
        print("[ANALYZE] Analyzing results...")
        print("  Analysis complete!")
        print()
    
    commands = [
        # Triggered command: Runs automatically when plugin-dir is set
        {
            COMMAND_NAME: 'load-plugins',
            COMMAND_DESCRIPTION: 'Load plugins from directory (auto-triggered by --plugin-dir)',
            COMMAND_ACTION: load_plugins,
            COMMAND_TRIGGER_PARAM: 'plugin-dir',
            COMMAND_REQUIRED_PARAMS: ['plugin-dir'],
        },
        
        # Triggered command: Runs automatically when config-file is set
        {
            COMMAND_NAME: 'load-config',
            COMMAND_DESCRIPTION: 'Load configuration file (auto-triggered by --config-file)',
            COMMAND_ACTION: load_config,
            COMMAND_TRIGGER_PARAM: 'config-file',
            COMMAND_REQUIRED_PARAMS: ['config-file'],
        },
        
        # Triggered command: Runs automatically when data-source is set
        {
            COMMAND_NAME: 'connect-data-source',
            COMMAND_DESCRIPTION: 'Connect to data source (auto-triggered by --data-source)',
            COMMAND_ACTION: connect_data_source,
            COMMAND_TRIGGER_PARAM: 'data-source',
            COMMAND_REQUIRED_PARAMS: ['data-source'],
        },
        
        # Regular commands - user must explicitly invoke these
        {
            COMMAND_NAME: 'process',
            COMMAND_DESCRIPTION: 'Process data',
            COMMAND_ACTION: process,
        },
        {
            COMMAND_NAME: 'analyze',
            COMMAND_DESCRIPTION: 'Analyze results',
            COMMAND_ACTION: analyze,
        },
    ]
    
    spafw37.add_params(params)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    print("Parameter-Triggered Commands Example")
    print("Demonstrates COMMAND_TRIGGER_PARAM\n")
    spafw37.run_cli()
