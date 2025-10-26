"""Tests for buffered parameter registration and run-level parsing."""

import pytest
import warnings
from spafw37 import cli, config, param, command
from spafw37.config_consts import (
    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT, PARAM_BIND_TO,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE, PARAM_TYPE_LIST,
    CONFLICT_POLICY_FIRST, CONFLICT_POLICY_LAST, CONFLICT_POLICY_ERROR,
    RUN_LEVELS_ALIAS_LONG, RUN_LEVELS_ALIAS_SHORT
)


def setup_function():
    """Reset module state between tests."""
    param._param_aliases.clear()
    param._params.clear()
    param._buffered_registrations.clear()
    param._run_levels.clear()
    param._xor_list.clear()
    param._conflict_policy = CONFLICT_POLICY_FIRST
    config._non_persisted_config_names.clear()
    config._config.clear()
    config._persistent_config.clear()
    cli._pre_parse_actions.clear()
    cli._post_parse_actions.clear()
    command._commands.clear()
    command._finished_commands.clear()
    command._command_queue.clear()
    command._phases = {command.PHASE_DEFAULT: []}
    command._phases_completed.clear()


def test_register_param_buffers_definition():
    """Test that register_param adds to buffer without immediate registration."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'test-param',
            PARAM_ALIASES: ['--test', '-t'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_DEFAULT: 'default_value'
        }
    )
    
    assert len(param._buffered_registrations) == 1
    assert param._params == {}
    assert param._param_aliases == {}


def test_build_parser_flushes_buffer():
    """Test that build_parser processes buffered registrations."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'param1',
            PARAM_ALIASES: ['--param1'],
            PARAM_TYPE: PARAM_TYPE_TEXT
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'param2',
            PARAM_ALIASES: ['--param2'],
            PARAM_TYPE: PARAM_TYPE_NUMBER
        }
    )
    
    count = cli.build_parser()
    
    assert count == 2
    assert len(param._buffered_registrations) == 0
    assert 'param1' in param._params
    assert 'param2' in param._params
    assert '--param1' in param._param_aliases
    assert '--param2' in param._param_aliases


def test_buffered_registration_basic():
    """Test basic buffered registration workflow."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'timeout',
            PARAM_ALIASES: ['--timeout'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_DEFAULT: 30
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'verbose',
            PARAM_ALIASES: ['--verbose'],
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False
        }
    )
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['--timeout', '60'])
    
    assert effective['timeout'] == 60
    assert effective['verbose'] is False


def test_buffered_registration_conflicts_first_policy():
    """Test conflict resolution with 'first' policy."""
    setup_function()
    
    param.set_conflict_policy(CONFLICT_POLICY_FIRST)
    
    param.register_param(
        **{
            PARAM_NAME: 'test',
            PARAM_ALIASES: ['--test'],
            PARAM_DEFAULT: 'first'
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'test',
            PARAM_ALIASES: ['--test'],
            PARAM_DEFAULT: 'second'
        }
    )
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cli.build_parser()
        assert len(w) == 1
        assert 'Duplicate' in str(w[0].message)
    
    assert param._params['test'][PARAM_DEFAULT] == 'first'


def test_buffered_registration_conflicts_last_policy():
    """Test conflict resolution with 'last' policy."""
    setup_function()
    
    param.set_conflict_policy(CONFLICT_POLICY_LAST)
    
    param.register_param(
        **{
            PARAM_NAME: 'test',
            PARAM_ALIASES: ['--test'],
            PARAM_DEFAULT: 'first'
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'test',
            PARAM_ALIASES: ['--test'],
            PARAM_DEFAULT: 'second'
        }
    )
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cli.build_parser()
        assert len(w) == 1
    
    assert param._params['test'][PARAM_DEFAULT] == 'second'


def test_buffered_registration_conflicts_error_policy():
    """Test conflict resolution with 'error' policy."""
    setup_function()
    
    param.set_conflict_policy(CONFLICT_POLICY_ERROR)
    
    param.register_param(
        **{
            PARAM_NAME: 'test',
            PARAM_ALIASES: ['--test'],
            PARAM_DEFAULT: 'first'
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'test',
            PARAM_ALIASES: ['--test'],
            PARAM_DEFAULT: 'second'
        }
    )
    
    with pytest.raises(ValueError, match="Duplicate parameter registration"):
        cli.build_parser()


def test_register_run_level():
    """Test registering a run-level definition."""
    setup_function()
    
    param.register_run_level('dev', {'log_level': 'debug', 'timeout': 10})
    
    assert 'dev' in param._run_levels
    assert param._run_levels['dev']['log_level'] == 'debug'
    assert param._run_levels['dev']['timeout'] == 10


def test_register_run_level_invalid_defaults():
    """Test that non-dict defaults raise an error."""
    setup_function()
    
    with pytest.raises(ValueError, match="Run-level defaults must be a dict"):
        param.register_run_level('bad', "not a dict")


def test_run_levels_merge_order():
    """Test that run-levels merge in correct order."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'value',
            PARAM_ALIASES: ['--value'],
            PARAM_DEFAULT: 'base'
        }
    )
    
    param.register_run_level('r1', {'value': 'r1'})
    param.register_run_level('r2', {'value': 'r2'})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['-R', 'r1,r2'])
    
    assert effective['value'] == 'r2'


def test_run_levels_precedence_cli_overrides():
    """Test that CLI arguments override run-level values."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'value',
            PARAM_ALIASES: ['--value'],
            PARAM_DEFAULT: 'base'
        }
    )
    
    param.register_run_level('prod', {'value': 'prod_value'})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['-R', 'prod', '--value', 'cli_value'])
    
    assert effective['value'] == 'cli_value'


def test_run_levels_missing_level():
    """Test that missing run-level generates warning and is ignored."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'value',
            PARAM_ALIASES: ['--value'],
            PARAM_DEFAULT: 'base'
        }
    )
    
    cli.build_parser()
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        effective, _ = cli.parse_args(['-R', 'nonexistent'])
        assert len(w) == 1
        assert 'Unknown run-level' in str(w[0].message)
    
    assert effective['value'] == 'base'


def test_run_levels_comma_separated():
    """Test that comma-separated run-levels are parsed correctly."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'a',
            PARAM_ALIASES: ['--a'],
            PARAM_DEFAULT: 'base_a'
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'b',
            PARAM_ALIASES: ['--b'],
            PARAM_DEFAULT: 'base_b'
        }
    )
    
    param.register_run_level('r1', {'a': 'r1_a'})
    param.register_run_level('r2', {'b': 'r2_b'})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['-R', 'r1,r2'])
    
    assert effective['a'] == 'r1_a'
    assert effective['b'] == 'r2_b'


def test_run_levels_multiple_flags():
    """Test that multiple -R flags are processed correctly."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'value',
            PARAM_ALIASES: ['--value'],
            PARAM_DEFAULT: 'base'
        }
    )
    
    param.register_run_level('r1', {'value': 'r1'})
    param.register_run_level('r2', {'value': 'r2'})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['-R', 'r1', '-R', 'r2'])
    
    assert effective['value'] == 'r2'


def test_run_levels_with_long_alias():
    """Test using --run-levels long form."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'value',
            PARAM_ALIASES: ['--value'],
            PARAM_DEFAULT: 'base'
        }
    )
    
    param.register_run_level('test', {'value': 'test_value'})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['--run-levels', 'test'])
    
    assert effective['value'] == 'test_value'


def test_normalize_run_levels_input():
    """Test run-levels input normalization."""
    setup_function()
    
    assert cli._normalize_run_levels_input(None) == []
    assert cli._normalize_run_levels_input([]) == []
    assert cli._normalize_run_levels_input('dev') == ['dev']
    assert cli._normalize_run_levels_input('dev,prod') == ['dev', 'prod']
    assert cli._normalize_run_levels_input(['dev', 'prod']) == ['dev', 'prod']
    assert cli._normalize_run_levels_input(['dev,stage', 'prod']) == ['dev', 'stage', 'prod']


def test_merge_run_levels_order():
    """Test that merge_run_levels applies levels in order."""
    setup_function()
    
    param.register_run_level('r1', {'a': 'r1_a', 'b': 'r1_b'})
    param.register_run_level('r2', {'a': 'r2_a'})
    
    base = {'a': 'base_a', 'b': 'base_b', 'c': 'base_c'}
    result = cli._merge_run_levels(['r1', 'r2'], base)
    
    assert result['a'] == 'r2_a'
    assert result['b'] == 'r1_b'
    assert result['c'] == 'base_c'


def test_get_effective_config_full_pipeline():
    """Test complete effective config computation."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'timeout',
            PARAM_ALIASES: ['--timeout'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_DEFAULT: 30
        }
    )
    param.register_param(
        **{
            PARAM_NAME: 'log_level',
            PARAM_ALIASES: ['--log-level'],
            PARAM_DEFAULT: 'info'
        }
    )
    
    param.register_run_level('dev', {'log_level': 'debug', 'timeout': 10})
    param.register_run_level('prod', {'log_level': 'error', 'timeout': 60})
    
    cli.build_parser()
    
    effective = cli.get_effective_config(['-R', 'dev,prod', '--timeout', '45'])
    
    assert effective['log_level'] == 'error'
    assert effective['timeout'] == 45


def test_parse_args_without_run_levels():
    """Test parse_args with merge_run_levels=False."""
    setup_function()
    
    param.register_param(
        **{
            PARAM_NAME: 'value',
            PARAM_ALIASES: ['--value'],
            PARAM_DEFAULT: 'base'
        }
    )
    
    param.register_run_level('r1', {'value': 'r1'})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['-R', 'r1'], merge_run_levels=False)
    
    assert effective['value'] == 'base'


def test_list_run_levels():
    """Test listing registered run-levels."""
    setup_function()
    
    param.register_run_level('dev', {})
    param.register_run_level('prod', {})
    param.register_run_level('test', {})
    
    levels = param.list_run_levels()
    
    assert set(levels) == {'dev', 'prod', 'test'}


def test_get_run_level():
    """Test retrieving a specific run-level."""
    setup_function()
    
    param.register_run_level('dev', {'log_level': 'debug'})
    
    level = param.get_run_level('dev')
    
    assert level == {'log_level': 'debug'}
    assert param.get_run_level('nonexistent') is None


def test_get_buffered_registrations():
    """Test getting a copy of buffered registrations."""
    setup_function()
    
    param.register_param(**{PARAM_NAME: 'p1'})
    param.register_param(**{PARAM_NAME: 'p2'})
    
    buffered = param.get_buffered_registrations()
    
    assert len(buffered) == 2
    assert buffered[0][PARAM_NAME] == 'p1'
    assert buffered[1][PARAM_NAME] == 'p2'


def test_extract_cli_overrides_toggle():
    """Test extracting toggle parameter overrides."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False
    })
    
    overrides = cli._extract_cli_overrides(['--verbose'])
    
    assert overrides['verbose'] is True


def test_extract_cli_overrides_number():
    """Test extracting number parameter overrides."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'count',
        PARAM_ALIASES: ['--count'],
        PARAM_TYPE: PARAM_TYPE_NUMBER
    })
    
    overrides = cli._extract_cli_overrides(['--count', '42'])
    
    assert overrides['count'] == 42


def test_extract_cli_overrides_with_equals():
    """Test extracting parameter with equals syntax."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'path',
        PARAM_ALIASES: ['--path'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    overrides = cli._extract_cli_overrides(['--path=/some/path'])
    
    assert overrides['path'] == '/some/path'


def test_extract_cli_overrides_skips_run_levels():
    """Test that run-level flags are skipped during extraction."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'value',
        PARAM_ALIASES: ['--value'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    overrides = cli._extract_cli_overrides(['-R', 'dev', '--value', 'test'])
    
    assert 'run-levels' not in overrides
    assert overrides['value'] == 'test'


def test_get_base_defaults():
    """Test extracting base defaults from parameters."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'text',
        PARAM_ALIASES: ['--text'],
        PARAM_DEFAULT: 'default_text'
    })
    param.add_param({
        PARAM_NAME: 'toggle',
        PARAM_ALIASES: ['--toggle'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: True
    })
    param.add_param({
        PARAM_NAME: 'no_default',
        PARAM_ALIASES: ['--no-default']
    })
    
    defaults = cli._get_base_defaults()
    
    assert defaults['text'] == 'default_text'
    assert defaults['toggle'] is True
    assert 'no_default' not in defaults


def test_backward_compatibility_add_param():
    """Test that existing add_param continues to work."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'value'
    })
    
    assert 'test' in param._params
    assert '--test' in param._param_aliases


def test_backward_compatibility_handle_cli_args():
    """Test that existing handle_cli_args continues to work."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    
    cli.handle_cli_args(['--test', 'value'])
    
    assert config.get_config_value('test') == 'value'


def test_complex_scenario_multiple_run_levels_and_overrides():
    """Test a complex scenario with multiple run-levels and CLI overrides."""
    setup_function()
    
    param.register_param(**{
        PARAM_NAME: 'host',
        PARAM_ALIASES: ['--host'],
        PARAM_DEFAULT: 'localhost'
    })
    param.register_param(**{
        PARAM_NAME: 'port',
        PARAM_ALIASES: ['--port'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 8000
    })
    param.register_param(**{
        PARAM_NAME: 'debug',
        PARAM_ALIASES: ['--debug'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False
    })
    
    param.register_run_level('base', {'host': 'base.local'})
    param.register_run_level('dev', {'port': 3000, 'debug': True})
    param.register_run_level('prod', {'host': 'prod.example.com', 'port': 443})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args([
        '-R', 'base',
        '-R', 'dev',
        '--host', 'custom.host'
    ])
    
    assert effective['host'] == 'custom.host'
    assert effective['port'] == 3000
    assert effective['debug'] is True


def test_set_conflict_policy_invalid():
    """Test that invalid conflict policy raises error."""
    setup_function()
    
    with pytest.raises(ValueError, match="Invalid conflict policy"):
        param.set_conflict_policy('invalid')


def test_run_levels_with_list_params():
    """Test run-levels work with list parameters."""
    setup_function()
    
    param.register_param(**{
        PARAM_NAME: 'tags',
        PARAM_ALIASES: ['--tags'],
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_DEFAULT: []
    })
    
    param.register_run_level('dev', {'tags': ['dev', 'local']})
    
    cli.build_parser()
    
    effective, _ = cli.parse_args(['-R', 'dev'])
    
    assert effective['tags'] == ['dev', 'local']


def test_buffered_missing_name_warning():
    """Test that buffered registration without name generates warning."""
    setup_function()
    
    param.register_param(**{
        PARAM_ALIASES: ['--test']
    })
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        count = cli.build_parser()
        assert count == 0
        assert len(w) == 1
        assert 'missing' in str(w[0].message).lower()
