#!/usr/bin/env python
"""Compare output of _parse_cli_args() vs _parse_cli_args_regex()."""

import sys
sys.path.insert(0, '/workspaces/spafw37/src')

from spafw37 import cli, param, command
from spafw37.constants.param import PARAM_NAME, PARAM_ALIASES, PARAM_TYPE

# Setup test params and commands
def setup_test_environment():
    """Register params and commands for testing."""
    param._param_aliases.clear()
    param._params.clear()
    command._commands.clear()
    
    # Register test params
    test_params = [
        {
            PARAM_NAME: 'input',
            PARAM_ALIASES: ['--input', '-i'],
            PARAM_TYPE: 'text',
        },
        {
            PARAM_NAME: 'output',
            PARAM_ALIASES: ['--output', '-o'],
            PARAM_TYPE: 'text',
        },
        {
            PARAM_NAME: 'verbose',
            PARAM_ALIASES: ['--verbose', '-v'],
            PARAM_TYPE: 'toggle',
        },
        {
            PARAM_NAME: 'count',
            PARAM_ALIASES: ['--count', '-c'],
            PARAM_TYPE: 'number',
        },
        {
            PARAM_NAME: 'items',
            PARAM_ALIASES: ['--items'],
            PARAM_TYPE: 'list',
        },
        {
            PARAM_NAME: 'config',
            PARAM_ALIASES: ['--config'],
            PARAM_TYPE: 'dict',
        },
        {
            PARAM_NAME: 'email',
            PARAM_ALIASES: ['--email'],
            PARAM_TYPE: 'text',
        },
        {
            PARAM_NAME: 'message',
            PARAM_ALIASES: ['--message', '-m'],
            PARAM_TYPE: 'text',
        },
    ]
    
    for p in test_params:
        param.add_param(p)
    
    # Register test commands
    def dummy_action():
        pass
    
    test_commands = [
        {'name': 'build', 'action': dummy_action, 'description': 'Build project'},
        {'name': 'test', 'action': dummy_action, 'description': 'Run tests'},
        {'name': 'deploy', 'action': dummy_action, 'description': 'Deploy'},
    ]
    
    for cmd in test_commands:
        command.add_command(cmd)


def compare_parsers(args, test_name):
    """Compare output of both parsers."""
    print(f"\n{'='*80}")
    print(f"Test: {test_name}")
    print(f"Args: {args}")
    print(f"{'-'*80}")
    
    try:
        result_original = cli._parse_cli_args(args)
        print("✓ Original parser succeeded")
    except Exception as e:
        print(f"✗ Original parser failed: {e}")
        result_original = None
    
    try:
        result_regex = cli._parse_cli_args_regex(args)
        print("✓ Regex parser succeeded")
    except Exception as e:
        print(f"✗ Regex parser failed: {e}")
        result_regex = None
    
    if result_original and result_regex:
        # Sort params by alias for comparison
        orig_params = sorted(result_original['params'], key=lambda x: x['alias'])
        regex_params = sorted(result_regex['params'], key=lambda x: x['alias'])
        
        orig_commands = sorted(result_original['commands'])
        regex_commands = sorted(result_regex['commands'])
        
        commands_match = orig_commands == regex_commands
        params_match = orig_params == regex_params
        
        print(f"\nCommands match: {'✓' if commands_match else '✗'}")
        print(f"  Original: {orig_commands}")
        print(f"  Regex:    {regex_commands}")
        
        print(f"\nParams match: {'✓' if params_match else '✗'}")
        print(f"  Original: {orig_params}")
        print(f"  Regex:    {regex_params}")
        
        return commands_match and params_match
    
    return False


def main():
    """Run comparison tests."""
    setup_test_environment()
    
    test_cases = [
        # Basic tests
        (["--input", "file.txt"], "Simple param with value"),
        (["--verbose"], "Toggle param"),
        (["--input=file.txt"], "Param with embedded value"),
        (["build"], "Single command"),
        (["build", "test"], "Multiple commands"),
        
        # Mixed scenarios
        (["build", "--verbose", "--input", "file.txt"], "Command with params"),
        (["--input", "file.txt", "build", "--output", "out.txt"], "Params and command mixed"),
        (["--count", "123", "test", "--verbose"], "Number param, command, toggle"),
        
        # Complex values
        (["--email=mike.norrish@gmail.com"], "Email address with special chars"),
        (["--message", "Hello, world!"], "Text with punctuation"),
        (["--input=/usr/local/bin/file"], "Path with slashes"),
        (["--config={'key':'value'}"], "JSON object"),
        
        # Multiple values (for list params)
        (["--items", "one", "two", "three"], "List param with multiple values"),
        (["--items", "one", "--verbose", "--items", "two"], "List param with toggle in between"),
    ]
    
    results = []
    for args, description in test_cases:
        passed = compare_parsers(args, description)
        results.append((description, passed))
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    for desc, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {desc}")
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Both parsers produce identical output.")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed.")


if __name__ == '__main__':
    main()
