"""
mapping.py is a library for Mapping values from multiple dictionaries to a single dictionary. 
The function takes in a single map dictionary and any number of value dictionaries, it then creates
a new dictionary with the keys from the map dictionary and the values from the mapped value 
categories.

This function allows for the creation of MAP files (json) that can be swapped out without have to 
change any of the underlying code.

Function allows for the use of reserved keywords to map static values or add fallback values.

Keywords:
    STRING: `STRING.<value>` - Maps a static string defined in the map file to the key
    INT: `INT.<value>` - Maps a static integer defined in the map file to the key
    FLOAT: `FLOAT.<value>` or `FLOAT.<value>.<value>` (For non-integer values) - Maps a static float 
        defined in the map file to the key
    LIST: `LIST.<value>` - Maps a static list (Of String Values) defined in the map file to the key
    BOOL: `BOOL.true` or `BOOL.false` - Maps a static boolean defined in the map file to the key

    SKIP: Skips the key and doesn't add it to the output dictionary
    NULL: Adds the key to the output dictionary with a value of None
    OR: Allows for defining a fallback value if the first Key can't be populated. OR statements can 
        be strung together to create multiple fallbacks.
    
"""
import json
import os
import logging


LOGGER = logging.getLogger(__name__)
LOG_LEVEL_SET = os.environ.get('LOG_LEVEL', 'DEBUG') or 'DEBUG'
LOG_LEVEL = logging.DEBUG if LOG_LEVEL_SET.lower() in ['debug'] else logging.INFO
LOGGER.setLevel(LOG_LEVEL)


def _get_static_string(value_targets):
    """
    Return the static string in Value
    """
    LOGGER.debug(f'Mapping Static String: {value_targets}')
    if len(value_targets) > 1:
        try:
            mapped_value = str(value_targets[1])
            return mapped_value

        except ValueError:
            # Check if Statement has an OR clause
            LOGGER.error(f'Error converting value: {value_targets[1]} to string')
            raise Exception(f"Error converting value: {value_targets[1]} to string")

    raise Exception(f"Error converting value: {value_targets[1]} to string")

def _get_static_int(value_targets, **value_dicts):
    """
    Takes in the value map and returns a static Integer
    """
    LOGGER.debug(f'Mapping Static Integer: {value_targets}')
    if len(value_targets) > 1:
        try:
            mapped_value = int(value_targets[1])
            return mapped_value

        except ValueError:
            # Check if Statement has an OR clause
            if len(value_targets) > 3:
                if 'OR' in value_targets:
                    LOGGER.warning(f'Failed to Map Integer: {value_targets[1]}, using OR clause: {value_targets[value_targets.index("OR")+1:]}')
                    return _get_mapped_value(".".join(value_targets[value_targets.index('OR')+1:]), **value_dicts)
            LOGGER.error(f'Error converting value: {value_targets[1]} to integer')
            raise Exception(f"Error converting value: {value_targets[1]} to integer")

    raise Exception(f"Error converting value: {value_targets[1]} to integer")

def _get_static_float(value_targets, **value_dicts):
    """
    Takes in the value map and returns a static Float value
    """
    LOGGER.debug(f'Mapping Static Float: {value_targets}')
    try:
        if len(value_targets) > 1:
            
            if value_targets[1].isdigit():
                
                if len(value_targets) >= 3:

                    if value_targets[2].isdigit():

                        mapped_value = float(f'{value_targets[1]}.{value_targets[2]}')
                        return mapped_value  
                mapped_value = float(value_targets[1])
                return mapped_value
            else:
                raise ValueError
                        
    except ValueError:
        if len(value_targets) >= 3:
            if 'OR' in value_targets:
                LOGGER.warning(f'Failed to Map Float: {value_targets[1]}, using OR clause: {value_targets[value_targets.index("OR")+1:]}')
                return _get_mapped_value(".".join(value_targets[value_targets.index('OR')+1:]), **value_dicts)
        LOGGER.error(f'Error converting value: {value_targets[1]} to float')
        raise Exception(f"Error converting value: {value_targets[1]} to float")
            

def _get_static_list(value_targets, **value_dicts):
    """
    Takes in the value_targets and returns a list
    """
    LOGGER.debug(f'Mapping Static List: {value_targets}')
    if len(value_targets) > 1:
        try:
            value_targets[1] = value_targets[1].replace(', ', ',')
            value_targets[1] = value_targets[1].replace(' ,', ',')
            mapped_value = value_targets[1].split(',')
            return mapped_value
        except Exception as e:
            LOGGER.error(f'Error converting value: {value_targets[1]} to list')
            raise Exception(f"Error converting value: {value_targets[1]} to list")

    return []
    

def _get_static_bool(value_targets, **value_dicts):
    """
    Get Value_target and return a boolean
    """
    LOGGER.debug(f'Mapping Static Boolean: {value_targets}')
    if value_targets[1] in ['True', 'true', 'TRUE']:
        return True
    elif value_targets[1] in ['False', 'false', 'FALSE']:
        return False
    LOGGER.error(f'Error converting value: {value_targets[1]} to boolean')
    raise Exception(f"Error converting value: {value_targets[1]} to boolean")


# Dictionary defining reserved keywords and the function to call for each keyword
RESERVED_KEYWORDS = {
    'STRING': _get_static_string,
    'INT': _get_static_int,
    'FLOAT': _get_static_float,
    'LIST': _get_static_list,
    'BOOL': _get_static_bool
}


def map_dictionary( map, **value_dicts,): 
    """
    Loop through the map dictionary and build a new dictionary from the values found in the value dictionaries.
    """

    LOGGER.info(f'Beginning Mapping of Dictionary')
    LOGGER.debug(f'Map: {json.dumps(map)}')
    LOGGER.debug(f'Value Dictionaries: {json.dumps(value_dicts)}')
    # Initialize the mapped dictionary
    mapped_dict = {}
    # Validate each key in the map dictionary and route to the appropriate function
    for key, value in map.items():
        # If the value is SKIP, skip that key
        LOGGER.debug(f'Mapping Key: {key} to value: {value}')
        if value == 'SKIP':
            LOGGER.debug(f'Skipping Key: {key}')
            continue 
        
        # If the value is a dictionary, pass the dictionary back to map_dictionary function
        # With the current value_dicts
        if type(value) is dict:
            LOGGER.info(f'Value is a dictionary, mapping dictionary to Key: {key}')
            mapped_dict[key] = map_dictionary(value, **value_dicts)
        # Get the mapped value for the key
        else:
            mapped_dict[key] = _get_mapped_value(value, **value_dicts)
        
    return mapped_dict


def _get_mapped_value(map_address, **value_dicts):
    """
    Takes in a map address and returns the value from the value dictionaries or static definition
    """
    LOGGER.debug(f'Getting Mapped Value for: {map_address}')
    # Split map_address into value keys
    value_keys = map_address.split('.')
    # Check if the first key is `NULL` and return None if it is
    if value_keys[0] == 'NULL':
        LOGGER.debug(f'Value is NULL, returning None')
        return None
    # Check if the first key is a reserved keyword
    if value_keys[0] in RESERVED_KEYWORDS.keys():
        try:
            # Call the reserved keyword function and return the result
            # Note Recursion and recalculation of value_keys is handled in the reserved keyword functions
            result = RESERVED_KEYWORDS[value_keys[0]](value_keys)
            return result
        except Exception as e:
            # If the reserved keyword function fails, raise an exception
            raise Exception(f'Error getting mapped value: {e}')
    else:
        # If the first key is not a reserved keyword, get the value for the map address
        return _get_value_from_value_dict(map_address, **value_dicts)
    

def _get_value_from_value_dict(map_address, **value_dicts):
    """
    Takes in an address from the map and returns the value at that address from the value
    dictionaries.
    """
    # Split map_address into key_groups separated by OR keyword
    key_groups = map_address.split('.OR.')
        
    try: 
        #Split Address from first key_group
        address = key_groups[0].split('.')
        # Get the first value from the value dictionaries
        result = value_dicts[address[0]]
        # Loop through the rest of the address keys and return the value in result
        for address_key in address[1:]:
            LOGGER.debug(f'Getting Value for Key: {address_key}')
            result = result[address_key]
        # If a result was found, return it
        return result
    except KeyError:
        # If the first key_group failed, check if there are more key_groups
        if len(key_groups) > 1:
            LOGGER.warning(f'Error getting value from value dictionary: {key_groups[0]} Using Value from OR: {".OR.".join(key_groups[1:])}')
            # Rejoin the rest of the key_groups and send string back to _get_mapped_value
            return _get_mapped_value('.OR.'.join(key_groups[1:]), **value_dicts)
        # If no more key_groups exist, raise an exception
        LOGGER.error(f'Failed to map value from value dictionary: {map_address}')
        raise Exception(f'Error getting value from value dictionary: {map_address}')


# Script to test the functions
test_map = {
    'id1': 'STRING.1234',
    'id2': 'INT.123',
    'id3': 'INT.test.OR.INT.cat.OR.INT.12',
    'id4': 'FLOAT.12',
    'id5': 'BOOL.True',
    'id99': 'BOOL.False',
    'id6': {
        'id6.id7': 'STRING.This is a string',
        'id6.id8': 'NULL'
    },
    'nested_values': {
        'id9': 'STRING.this is the first layer',
        'id10': {
            'id11': 'STRING.This is the second layer',
            'id12': {
                'id13': 'STRING.This is the third layer'
            }
        }
    },
    'from_value_map': 'value_dict_1.id1',
    'from_nested_map': 'value_dict_1.id2.id3',
    'dict_from_nested_map': 'value_dict_1.id4.OR.STRING.This Failed'
}

value_dicts = {
    'value_dict_1': {
        'id1': '1234',
        'id2': {
            'id3': 'test'
        }
    }
}

print(json.dumps(map_dictionary(test_map, **value_dicts), indent=4))