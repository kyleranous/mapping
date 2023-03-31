"""
mapping.py Unit Tests
"""
import unittest

import mapping


class TestMappingDictionary(unittest.TestCase):
    """
    Test mapping.mapping_dictionary for all expected functionality. 
    """
    def setUp(self):
        """
        Setup the value dictionary being used in each test
        """
        self.value_dict = {
            'value1': {
                'v1k1': 'Test String'
            }
        }


    def test_mapping_static_string(self):
        """
        Test that passing a static string to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'STRING.Test String'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], 'Test String')

    def test_mapping_static_int(self):
        """
        Test that passing a static int to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'INT.1'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], 1)

    def test_mapping_static_float_no_decimal(self):
        """
        Test that passing a static float to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'FLOAT.1'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], 1)

    def test_mapping_static_float_decimal(self):
        """
        Test that passing a static float to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'FLOAT.1.1'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], 1.1)

    def test_mapping_static_list_leading_spaces(self):
        """
        Test that passing a static list to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'LIST.hello, world'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], ['hello', 'world'])

    def test_mapping_static_list_trailing_spaces(self):
        """
        Test that passing a static list to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'LIST.hello ,world'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], ['hello', 'world'])

    def test_mapping_static_list_leading_and_trailing_spaces(self):
        """
        Test that passing a static list to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'LIST.hello , world'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], ['hello', 'world'])

    def test_mapping_static_list_no_spaces(self):
        """
        Test that passing a static list to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'LIST.hello,world'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertEqual(result['key1'], ['hello', 'world'])

    def test_mapping_static_bool_true(self):
        """
        Test that passing a static bool to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'BOOL.true',
            'key2': 'BOOL.True',
            'key3': 'BOOL.TRUE'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertTrue(result['key1'])
        self.assertTrue(result['key2'])
        self.assertTrue(result['key3'])

    def test_mapping_static_bool_false(self):
        """
        Test that passing a static bool to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'BOOL.false',
            'key2': 'BOOL.False',
            'key3': 'BOOL.FALSE'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)

        self.assertFalse(result['key1'])
        self.assertFalse(result['key2'])
        self.assertFalse(result['key3'])

    def test_mapping_skip(self):
        """
        Test that passing SKIP to mapping_dictionary returns the expected value
        """
        map_dict = {
            'key1': 'STRING.Should Be Here',
            'key2': 'SKIP',
            'key3': 'INT.1'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)
        expected = {
            'key1': 'Should Be Here',
            'key3': 1
        }

        self.assertEqual(result, expected)

    def test_mapping_null(self):
        """
        test that passing NULL to map_dictionary returns the expected value
        field with NULL mapped should return a field with a value of None
        """

        map_dict = {
            'key1': 'NULL'
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)
        expected = {
            'key1': None
        }

        self.assertEqual(result, expected)

    def test_mapping_or_invalid_first_condition(self):
        """
        Test that using OR will sucessfully process follow-on static condition if
        first condition is invalid
        """

        map_dict = {
            'key1': 'invalid.test.OR.STRING.Test String',
            'key2': 'invalid.test.OR.INT.1',
            'key3': 'invalid.test.OR.FLOAT.1.1',
            'key4': 'invalid.test.OR.LIST.hello, world',
            'key5': 'invalid.test.OR.BOOL.true',
            'key6': 'invalid.test.OR.NULL',
            'key7': 'invalid.test.OR.SKIP'
        }

        expected_dict = {
            'key1': 'Test String',
            'key2': 1,
            'key3': 1.1,
            'key4': ['hello', 'world'],
            'key5': True,
            'key6': None
        }

        result = mapping.map_dictionary(map_dict, **self.value_dict)
        self.assertEqual(result, expected_dict)

    def test_mapping_or_invalid_second_condition(self):
        """
        Test that using OR will raise an exception if the follow-on condition is invalid
        """

        map_dict = {
            'key1': 'invalid.test.OR.invalid.test2',
        }

        with self.assertRaises(KeyError):
            mapping.map_dictionary(map_dict, **self.value_dict)

    def test_mapping_nested_dictionary(self):
        """
        Test that passing a nested dictionary in a map will return the expected value
        including statics and mapped values
        """

        map_dict = {
            'key1': {
                's1': 'STRING.Static String',
                's2': 'INT.1',
                's3': 'FLOAT.1',
                's4': 'FLOAT.1.1',
                's5': 'LIST.hello, world',
                's6': 'BOOL.true',
                's7': 'NULL',
                's8': 'SKIP',
                's9': 'value1.v1k1',
                's10': 'invalid.test.OR.STRING.From OR Statement'
            }
        }

        expected = {
            'key1': {
                's1': 'Static String',
                's2': 1,
                's3': 1,
                's4': 1.1,
                's5': ['hello', 'world'],
                's6': True,
                's7': None,
                's9': 'Test String',
                's10': 'From OR Statement' 
            }
        }

        self.assertEqual(mapping.map_dictionary(map_dict, **self.value_dict), expected)
