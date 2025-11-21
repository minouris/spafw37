"""Persistence Example - Saving and loading configuration.

This example shows:
- PARAM_PERSISTENCE_ALWAYS - auto-save to config.json
- PARAM_PERSISTENCE_NEVER - never save
- User config files (--save-config, --load-config)
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_DEFAULT,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_ALWAYS,
    PARAM_PERSISTENCE_NEVER,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Define parameters with different persistence settings
params = [
    # Always persisted to config.json
    {
        PARAM_NAME: 'project-path',
        PARAM_DESCRIPTION: 'Project path (saved automatically)',
        PARAM_ALIASES: ['--project', '-p'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: './project',
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS,
    },
    # Saved only to user config files
    {
        PARAM_NAME: 'author',
        PARAM_DESCRIPTION: 'Author name (saved via --save-config)',
        PARAM_ALIASES: ['--author', '-a'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
    # Never persisted
    {
        PARAM_NAME: 'temp-dir',
        PARAM_DESCRIPTION: 'Temp directory (never saved)',
        PARAM_ALIASES: ['--temp', '-t'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: '/tmp',
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
]

def show_config():
    """Display current configuration."""
    spafw37.output("=" * 60)
    spafw37.output("CONFIGURATION")
    spafw37.output("=" * 60)
    
    project_path = spafw37.get_param('project-path')
    author = spafw37.get_param('author')
    temp_dir = spafw37.get_param('temp-dir')
    
    spafw37.output(f"\nProject Path: {project_path}")
    spafw37.output("  [ALWAYS persisted - auto-saved to config.json]")
    
    spafw37.output(f"\nAuthor: {author or '(not set)'}")
    spafw37.output("  [USER_ONLY - saved via --save-config my-config.json]")
    
    spafw37.output(f"\nTemp Directory: {temp_dir}")
    spafw37.output("  [NEVER persisted - runtime only]")
    
    spafw37.output()
    spafw37.output("=" * 60)
    spafw37.output("\nTry these commands:")
    spafw37.output("  1. Modify project path:")
    spafw37.output("     python config_persistence.py show --project /new/path")
    spafw37.output("     (automatically saved to config.json)")
    spafw37.output()
    spafw37.output("  2. Save user config:")
    spafw37.output("     python config_persistence.py show --author 'John' --save-config user.json")
    spafw37.output()
    spafw37.output("  3. Load user config:")
    spafw37.output("     python config_persistence.py show --load-config user.json")
    spafw37.output("=" * 60)

# Define command
commands = [
    {
        COMMAND_NAME: 'show',
        COMMAND_DESCRIPTION: 'Show configuration and persistence info',
        COMMAND_ACTION: show_config,
    },
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('config-persistence-demo')

if __name__ == '__main__':
    spafw37.run_cli()
