"""
Tests for parameter join functions in param.py.

These tests verify the behavior of join_param_value() which accumulates/merges
parameter values with type-specific joining logic.
"""

import pytest
from spafw37 import param, config
from spafw37.constants.param import (
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
    PARAM_JOIN_SEPARATOR,
    PARAM_DICT_MERGE_TYPE,
    PARAM_DICT_OVERRIDE_STRATEGY,
    DICT_MERGE_SHALLOW,
    DICT_MERGE_DEEP,
    DICT_OVERRIDE_RECENT,
    DICT_OVERRIDE_OLDEST,
    DICT_OVERRIDE_ERROR,
    SEPARATOR_SPACE,
    SEPARATOR_COMMA,
    SEPARATOR_PIPE,
)


def setup_function():
    """
    Reset parameter and configuration state before each test to ensure isolation.
    
    Clears all internal data structures to prevent test interference, ensuring
    each test starts with a clean slate for reproducible results.
    """
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    config._config.clear()


class TestJoinParamValueString:
    """
    Tests for join_param_value() with string parameters.
    
    String joining should concatenate values using a separator, with space as
    the default separator, and support custom separators via parameter definition.
    """

    def test_join_param_value_string_first_call_sets_value(self):
        """
        Tests that first join_param_value() call on empty string param sets value.
        
        When joining to a string parameter that has no existing value, the new value
        should become the initial value because there is nothing to join with.
        """
        test_param = {'name': 'message', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        param.join_param_value(param_name='message', value='Hello')
        
        result = config.get_config_value('message')
        assert result == 'Hello'

    def test_join_param_value_string_default_separator(self):
        """
        Tests that join_param_value() uses space separator by default for strings.
        
        When no separator is specified in parameter definition, space should be used
        because it is the standard default for string concatenation.
        """
        test_param = {'name': 'keywords', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        param.join_param_value(param_name='keywords', value='tag1')
        param.join_param_value(param_name='keywords', value='tag2')
        
        result = config.get_config_value('keywords')
        assert result == 'tag1 tag2'

    def test_join_param_value_string_custom_separator(self):
        """
        Tests that join_param_value() respects PARAM_JOIN_SEPARATOR configuration.
        
        When PARAM_JOIN_SEPARATOR is specified in parameter definition, that separator
        should be used because it allows per-parameter customization.
        """
        test_param = {'name': 'fruits', 'type': PARAM_TYPE_TEXT, PARAM_JOIN_SEPARATOR: SEPARATOR_COMMA}
        param.add_params([test_param])
        
        param.join_param_value(param_name='fruits', value='apple')
        param.join_param_value(param_name='fruits', value='banana')
        param.join_param_value(param_name='fruits', value='cherry')
        
        result = config.get_config_value('fruits')
        assert result == 'apple,banana,cherry'

    def test_join_param_value_string_pipe_separator(self):
        """
        Tests that join_param_value() works with pipe separator.
        
        When SEPARATOR_PIPE is configured, values should be joined with pipe character
        because special separators like pipe are commonly used for delimited data.
        """
        test_param = {'name': 'filters', 'type': PARAM_TYPE_TEXT, PARAM_JOIN_SEPARATOR: SEPARATOR_PIPE}
        param.add_params([test_param])
        
        param.join_param_value(param_name='filters', value='status=active')
        param.join_param_value(param_name='filters', value='type=user')
        
        result = config.get_config_value('filters')
        assert result == 'status=active|type=user'


class TestJoinParamValueList:
    """
    Tests for join_param_value() with list parameters.
    
    List joining should append values to existing list, wrapping single values
    in lists and extending with list values.
    """

    def test_join_param_value_list_first_call_creates_list(self):
        """
        Tests that first join_param_value() call on empty list param creates list.
        
        When joining to a list parameter with no existing value, the new value should
        be wrapped in a list because list params always store list values.
        """
        test_param = {'name': 'files', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        param.join_param_value(param_name='files', value='file1.txt')
        
        result = config.get_config_value('files')
        assert result == ['file1.txt']

    def test_join_param_value_list_accumulation(self):
        """
        Tests that join_param_value() appends to existing list.
        
        When joining single values to a list parameter multiple times, each value
        should be appended because join operation accumulates list items.
        """
        test_param = {'name': 'letters', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        param.join_param_value(param_name='letters', value='a')
        param.join_param_value(param_name='letters', value='b')
        param.join_param_value(param_name='letters', value='c')
        
        result = config.get_config_value('letters')
        assert result == ['a', 'b', 'c']

    def test_join_param_value_list_extends_with_list(self):
        """
        Tests that join_param_value() extends list when joining with another list.
        
        When joining a list value to an existing list, the new list should be extended
        (not nested) because list joining flattens by one level.
        """
        test_param = {'name': 'numbers', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        param.join_param_value(param_name='numbers', value=[1, 2])
        param.join_param_value(param_name='numbers', value=[3, 4])
        
        result = config.get_config_value('numbers')
        assert result == [1, 2, 3, 4]

    def test_join_param_value_list_mixed_single_and_list(self):
        """
        Tests that join_param_value() handles mix of single values and lists.
        
        When joining both single values and list values, single values should be
        appended and list values extended because join operation normalizes inputs.
        """
        test_param = {'name': 'mixed', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        param.join_param_value(param_name='mixed', value='single')
        param.join_param_value(param_name='mixed', value=['multi1', 'multi2'])
        param.join_param_value(param_name='mixed', value='another')
        
        result = config.get_config_value('mixed')
        assert result == ['single', 'multi1', 'multi2', 'another']


class TestJoinParamValueDict:
    """
    Tests for join_param_value() with dict parameters.
    
    Dict joining should merge dictionaries with configurable merge depth (shallow/deep)
    and override strategies (recent/oldest/error) for key conflicts.
    """

    def test_join_param_value_dict_first_call_sets_dict(self):
        """
        Tests that first join_param_value() call on empty dict param sets dict.
        
        When joining to a dict parameter with no existing value, the new dict should
        become the initial value because there is nothing to merge with.
        """
        test_param = {'name': 'options', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        param.join_param_value(param_name='options', value={'key': 'value'})
        
        result = config.get_config_value('options')
        assert result == {'key': 'value'}

    def test_join_param_value_dict_shallow_merge_default(self):
        """
        Tests that join_param_value() uses shallow merge by default for dicts.
        
        When PARAM_DICT_MERGE_TYPE is not specified, shallow merge should be used
        because it is the simpler default and matches standard dict update behavior.
        """
        test_param = {'name': 'metadata', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        param.join_param_value(param_name='metadata', value={'a': 1})
        param.join_param_value(param_name='metadata', value={'b': 2})
        
        result = config.get_config_value('metadata')
        assert result == {'a': 1, 'b': 2}

    def test_join_param_value_dict_shallow_merge_override_recent(self):
        """
        Tests that shallow merge uses recent value override by default.
        
        When keys conflict in shallow merge, the most recent value should win
        because DICT_OVERRIDE_RECENT is the default override strategy.
        """
        test_param = {'name': 'data', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        param.join_param_value(param_name='data', value={'key': 'first'})
        param.join_param_value(param_name='data', value={'key': 'second'})
        
        result = config.get_config_value('data')
        assert result == {'key': 'second'}

    def test_join_param_value_dict_shallow_merge_override_oldest(self):
        """
        Tests that shallow merge can use oldest value override strategy.
        
        When DICT_OVERRIDE_OLDEST is configured, existing values should be kept
        because this strategy preserves first-set values.
        """
        test_param = {
            'name': 'persistent',
            'type': PARAM_TYPE_DICT,
            PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_OLDEST
        }
        param.add_params([test_param])
        
        param.join_param_value(param_name='persistent', value={'key': 'original', 'a': 1})
        param.join_param_value(param_name='persistent', value={'key': 'new', 'b': 2})
        
        result = config.get_config_value('persistent')
        assert result == {'key': 'original', 'a': 1, 'b': 2}

    def test_join_param_value_dict_shallow_merge_override_error(self):
        """
        Tests that shallow merge can raise error on key conflicts.
        
        When DICT_OVERRIDE_ERROR is configured, conflicting keys should raise ValueError
        because this strategy enforces explicit conflict resolution.
        """
        test_param = {
            'name': 'strict',
            'type': PARAM_TYPE_DICT,
            PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_ERROR
        }
        param.add_params([test_param])
        
        param.join_param_value(param_name='strict', value={'key': 'value1'})
        
        with pytest.raises(ValueError, match="key collision"):
            param.join_param_value(param_name='strict', value={'key': 'value2'})

    def test_join_param_value_dict_deep_merge(self):
        """
        Tests that join_param_value() performs deep merge when configured.
        
        When DICT_MERGE_DEEP is configured, nested dicts should be recursively merged
        because deep merge preserves nested structure.
        """
        test_param = {
            'name': 'nested',
            'type': PARAM_TYPE_DICT,
            PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP
        }
        param.add_params([test_param])
        
        param.join_param_value(param_name='nested', value={'a': {'x': 1, 'y': 2}})
        param.join_param_value(param_name='nested', value={'a': {'y': 3, 'z': 4}})
        
        result = config.get_config_value('nested')
        assert result == {'a': {'x': 1, 'y': 3, 'z': 4}}

    def test_join_param_value_dict_deep_merge_multiple_levels(self):
        """
        Tests that deep merge works across multiple nesting levels.
        
        When deeply nested dicts are joined, recursion should merge all levels
        because deep merge applies to entire nested structure.
        """
        test_param = {
            'name': 'deep',
            'type': PARAM_TYPE_DICT,
            PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP
        }
        param.add_params([test_param])
        
        param.join_param_value(param_name='deep', value={'level1': {'level2': {'a': 1}}})
        param.join_param_value(param_name='deep', value={'level1': {'level2': {'b': 2}}})
        
        result = config.get_config_value('deep')
        assert result == {'level1': {'level2': {'a': 1, 'b': 2}}}

    def test_join_param_value_dict_deep_merge_with_oldest_override(self):
        """
        Tests that deep merge respects oldest override strategy at all levels.
        
        When DICT_OVERRIDE_OLDEST is used with deep merge, oldest values should be
        preserved at every nesting level because strategy applies recursively.
        """
        test_param = {
            'name': 'preserve',
            'type': PARAM_TYPE_DICT,
            PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP,
            PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_OLDEST
        }
        param.add_params([test_param])
        
        param.join_param_value(param_name='preserve', value={'a': 1, 'nested': {'x': 'first'}})
        param.join_param_value(param_name='preserve', value={'b': 2, 'nested': {'x': 'second', 'y': 'new'}})
        
        result = config.get_config_value('preserve')
        assert result == {'a': 1, 'b': 2, 'nested': {'x': 'first', 'y': 'new'}}


class TestJoinParamValueErrors:
    """
    Tests for join_param_value() error conditions.
    
    Join operation should raise errors for unsupported types (number, toggle)
    and unknown parameters.
    """

    def test_join_param_value_unknown_param_raises_error(self):
        """
        Tests that join_param_value() raises error for unknown parameter.
        
        When parameter cannot be resolved, ValueError should be raised because
        join operation requires a valid parameter definition.
        """
        with pytest.raises(ValueError, match="Unknown parameter"):
            param.join_param_value(param_name='nonexistent', value='test')

    def test_join_param_value_number_param_raises_error(self):
        """
        Tests that join_param_value() raises error for number parameters.
        
        When attempting to join a number parameter, ValueError should be raised
        because number values cannot be meaningfully accumulated.
        """
        test_param = {'name': 'count', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        
        with pytest.raises(ValueError, match="Cannot join.*number"):
            param.join_param_value(param_name='count', value=42)

    def test_join_param_value_toggle_param_raises_error(self):
        """
        Tests that join_param_value() raises error for toggle parameters.
        
        When attempting to join a toggle parameter, ValueError should be raised
        because toggle values are boolean and cannot be accumulated.
        """
        test_param = {'name': 'verbose', 'type': PARAM_TYPE_TOGGLE}
        param.add_params([test_param])
        
        with pytest.raises(ValueError, match="Cannot join.*toggle"):
            param.join_param_value(param_name='verbose', value=True)


class TestJoinParamValueResolution:
    """
    Tests for join_param_value() flexible resolution modes.
    
    Join function should support all resolution modes (param_name, bind_name, alias)
    with failover logic like other param functions.
    """

    def test_join_param_value_by_bind_name(self):
        """
        Tests that join_param_value() works with bind_name resolution.
        
        When called with bind_name, the parameter should be resolved and values
        accumulated because bind_name is a valid identifier.
        """
        test_param = {'name': 'items', 'type': PARAM_TYPE_LIST, 'config-name': 'item_list'}
        param.add_params([test_param])
        
        param.join_param_value(bind_name='item_list', value='first')
        param.join_param_value(bind_name='item_list', value='second')
        
        result = config.get_config_value('item_list')
        assert result == ['first', 'second']

    def test_join_param_value_by_alias(self):
        """
        Tests that join_param_value() works with alias resolution.
        
        When called with alias, the parameter should be resolved and values
        accumulated because alias is a valid identifier.
        """
        test_param = {'name': 'labels', 'type': PARAM_TYPE_LIST, 'aliases': ['--label', '-l']}
        param.add_params([test_param])
        
        param.join_param_value(alias='--label', value='tag1')
        param.join_param_value(alias='--label', value='tag2')
        
        result = config.get_config_value('labels')
        assert result == ['tag1', 'tag2']
