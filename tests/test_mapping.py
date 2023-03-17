import unittest
import json
import os

import mapping


class TestStaticString(unittest.TestCase):
    
    def test_get_static_string_valid(self):
        """
        Test that a correctly formatted array passed to _get_static_string returns the expected result
        """
        self.assertEqual(mapping._get_static_string(['STRING', 'test']), "test")
    
    def test_get_static_string_no_value(self):
        """
        Test that an incorrectly formatted array passed to _get_static_string will
        raise an exception
        """

        with self.assertRaises(Exception):
            mapping._get_static_string(['STRING'])


class TestStaticInteger(unittest.TestCase):

    def test_get_static_int_valid(self):
        """
        Test that a correctly passed array will return the expected integer
        """
        self.assertEqual(mapping._get_static_int(['INT', '1']), 1)

    def test_get_static_int_invalid(self):
        """
        Test that a correctly passed array with an invalid value will raise an exception
        """

        with self.assertRaises(Exception):
            mapping._get_static_int(['INT', 'test'])

    def test_get_static_int_no_value(self):
        """
        Test that a correctly passed array with no value will raise an exception
        """

        with self.assertRaises(Exception):
            mapping._get_static_int(['INT'])


class TestStaticFloat(unittest.TestCase):
    
    def test_get_static_float(self):
        """
        Test that a correctly passed array will return the expected float
        """

        self.assertEqual(mapping._get_static_float(['FLOAT', '1']), 1)
        self.assertEqual(mapping._get_static_float(['FLOAT', '1', '1']), 1.1)

    def test_get_static_float_invalid(self):
        """
        Test that a correctly passed array with an invalid value will raise an exception
        """

        with self.assertRaises(Exception):
            mapping._get_static_float(['FLOAT', 'test'])

        
        self.assertEqual(mapping._get_static_float(['FLOAT', '1', 'test']), 1)


class TestStaticList(unittest.TestCase):

    def test_get_static_list_valid(self):
        """
        Test that a correctly passed array will return the expected list
        """

        self.assertEqual(mapping._get_static_list(['LIST', '1, 2, 3']), ['1', '2', '3'])

    def test_get_static_list_single(self):
        """
        Test that a correctly passed array with a single string will pass an array with 
        a length of 1
        """

        self.assertEqual(mapping._get_static_list(['LIST', '1']), ['1'])

    def test_get_static_list_no_value(self):
        """
        Test that an array with no value will return an empty list
        """

        self.assertEqual(mapping._get_static_list(['LIST']), [])


class TestStaticBool(unittest.TestCase):

    def test_get_static_bool_valid(self):
        """
        Test that a correctly passed array will return the expected boolean
        """

        self.assertEqual(mapping._get_static_bool(['BOOL', 'True']), True)
        self.assertEqual(mapping._get_static_bool(['BOOL', 'False']), False)

    def test_get_static_bool_invalid(self):
        """
        Test that a correctly passed array with an invalid value will raise an exception
        """

        with self.assertRaises(Exception):
            mapping._get_static_bool(['BOOL', 'test'])

class TestGetMappedValue(unittest.TestCase):

    def setUp(self):
        """
        Create Value Dictionary
        """

        self.value_dict = {
            'value_1': {
                'v1_key1': 'This is a String',
                'v1_key2': 2
            }
        }

    def test_get_mapped_value_valid(self):
        """
        Test that a correctly formatted value is returned when provided a valid address
        """
        
        self.assertEqual(mapping._get_mapped_value('value_1.v1_key1', **self.value_dict), self.value_dict['value_1']['v1_key1'])
        self.assertEqual(mapping._get_mapped_value('value_1.v1_key2', **self.value_dict), self.value_dict['value_1']['v1_key2'])

    def test_get_mapped_value_invalid(self):
        """
        Test that an exception is raised when passed an invalid address
        Invalid address is defined as an address that does not exist in the value dictionary
        """
        with self.assertRaises(Exception):
            mapping._get_mapped_value('value_1.v1_key3', **self.value_dict)

    def test_get_mapped_value_invalid_with_OR(self):
        """
        Test that a STATIC value is returned when an invalid address is passed with an OR
        and a STATIC value is provided
        """

        mapped_key = 'value_1.v1_key3.OR.STRING.test'
        self.assertEqual(mapping._get_mapped_value(mapped_key, **self.value_dict), 'test')

    def test_get_mapped_value_invalid_with_OR_and_valid_address(self):
        """
        Test that a valid value is returned when an invalid address is passed with an OR
        and a valid address is provided
        """

        mapped_key = 'value_1.v1_key3.OR.value_1.v1_key1'
        self.assertEqual(mapping._get_mapped_value(mapped_key, **self.value_dict), self.value_dict['value_1']['v1_key1'])
        
    def test_get_mapped_value_NULL(self):

        self.assertIsNone(mapping._get_mapped_value('NULL'))

    def test_calls_static_string(self):

        self.assertEqual(mapping._get_mapped_value('STRING.test'), 'test')

    def test_calls_static_int(self):

        self.assertEqual(mapping._get_mapped_value('INT.1'), 1)

    def test_calls_static_float(self):
            
            self.assertEqual(mapping._get_mapped_value('FLOAT.1'), 1)
            self.assertEqual(mapping._get_mapped_value('FLOAT.1.1'), 1.1)

    def test_calls_static_list(self):

        self.assertEqual(mapping._get_mapped_value('LIST.1, 2, 3'), ['1', '2', '3'])

    def test_calls_static_bool(self):

        self.assertTrue(mapping._get_mapped_value('BOOL.True'))
        self.assertFalse(mapping._get_mapped_value('BOOL.False'))