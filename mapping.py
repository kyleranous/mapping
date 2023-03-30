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


def _get_static_string(address):
    """
    Return the static string in Value
    """
    LOGGER.debug('Mapping Static String: %s', address)
    if len(address) > 1:
        mapped_value = str(address[1])
        return mapped_value

    raise ValueError(f"Error converting value: {address[1]} to string")

def _get_static_int(address, **value_dicts):
    """
    Takes in the value map and returns a static Integer
    """
    LOGGER.debug('Mapping Static Integer: %s', address)
    if len(address) > 1:
        try:
            mapped_value = int(address[1])
            return mapped_value

        except ValueError as exc:
            # Check if Statement has an OR clause
            if len(address) > 3:
                if 'OR' in address:
                    new_address = ".".join(address[address.index('OR')+1:])
                    LOGGER.warning('Failed to Map Integer: %s, using OR clause: %s',
                                   address[1],
                                   new_address)

                    return _get_mapped_value(new_address, **value_dicts)

            LOGGER.error('Error converting value: %s to integer', address[1])
            raise ValueError(f"Error converting value: {address[1]} to integer") from exc

    raise RuntimeError(f"Error converting value: {address[1]} to integer")

def _get_static_float(address, **value_dicts):
    """
    Takes in the value map and returns a static Float value
    """
    LOGGER.debug('Mapping Static Float: %s', address)
    try:
        if len(address) > 1:
            if address[1].isdigit():
                if len(address) >= 3:

                    if address[2].isdigit():

                        mapped_value = float(f'{address[1]}.{address[2]}')
                        return mapped_value
                mapped_value = float(address[1])
                return mapped_value

        raise ValueError(f"Error converting value: {address[1]} to float")
    except ValueError as exc:
        if len(address) >= 3:
            if 'OR' in address:
                new_address = ".".join(address[address.index('OR')+1:])
                LOGGER.warning('Failed to Map Float: %s, using OR clause: %s',
                               address[1],
                               new_address)
                return _get_mapped_value(new_address, **value_dicts)
        LOGGER.error('Error converting value: %s to float', address[1])
        raise ValueError(f"Error converting value: {address[1]} to float") from exc


def _get_static_list(address):
    """
    Takes in the value_targets and returns a list
    """
    LOGGER.debug('Mapping Static List: %s', address)
    if len(address) > 1:
        try:
            address[1] = address[1].replace(', ', ',')
            address[1] = address[1].replace(' ,', ',')
            mapped_value = address[1].split(',')
            return mapped_value
        except Exception as exc:
            LOGGER.error('Error converting value: %s to list', address[1])
            raise RuntimeError(f"Error converting value: {address[1]} to list") from exc

    return []


def _get_static_bool(value_targets):
    """
    Get Value_target and return a boolean
    """
    LOGGER.debug('Mapping Static Boolean: %s', value_targets)
    if value_targets[1] in ['True', 'true', 'TRUE']:
        return True
    if value_targets[1] in ['False', 'false', 'FALSE']:
        return False
    LOGGER.error('Error converting value: %s to boolean', value_targets[1])
    raise RuntimeError(f"Error converting value: {value_targets[1]} to boolean")


# Dictionary defining reserved keywords and the function to call for each keyword
RESERVED_KEYWORDS = {
    'STRING': _get_static_string,
    'INT': _get_static_int,
    'FLOAT': _get_static_float,
    'LIST': _get_static_list,
    'BOOL': _get_static_bool
}


def map_dictionary(map_dict, **value_dicts):
    """
    Loop through the map dictionary and build a new dictionary from the values found 
    in the value dictionaries.
    """

    LOGGER.info('Beginning Mapping of Dictionary')
    LOGGER.debug('Map: %s', json.dumps(map_dict))
    LOGGER.debug('Value Dictionaries: %s', json.dumps(value_dicts))
    # Initialize the mapped dictionary
    mapped_dict = {}
    # Validate each key in the map dictionary and route to the appropriate function
    for map_key, address in map_dict.items():
        # If the value is SKIP, skip that key
        LOGGER.debug('Mapping Key: %s to value: %s', map_key, address)
        if address == 'SKIP':
            LOGGER.debug('Skipping Key: %s', map_key)
            continue

        # If the value is a dictionary, pass the dictionary back to map_dictionary function
        # With the current value_dicts
        if isinstance(address, dict):
            LOGGER.info('Value is a dictionary, mapping dictionary to Key: %s', map_key)
            result = map_dictionary(address, **value_dicts)
            mapped_dict[map_key] = result
        # Get the mapped value for the key
        else:
            #Check if result was skipped as part of follow on mapping
            result = _get_mapped_value(address, **value_dicts)
            if result == 'SKIP':
                LOGGER.debug('Skipping Key: %s', map_key)
                continue
            mapped_dict[map_key] = result
    return mapped_dict


def _get_mapped_value(address, **value_dicts):
    """
    Takes in a map address and returns the value from the value dictionaries or static definition
    """
    LOGGER.debug('Getting Mapped Value for: %s', address)
    # Split map_address into value keys
    address_keys = address.split('.')
    # Check if the first key is `NULL` and return None if it is
    if address_keys[0] == 'NULL':
        LOGGER.debug('Value is NULL, returning None')
        return None
    # Check for SKIP and return SKIP if found
    if address_keys[0] == 'SKIP':
        return 'SKIP'
        
    # Check if the first key is a reserved keyword
    if address_keys[0] in RESERVED_KEYWORDS:
        try:
            # Call the reserved keyword function and return the result
            # Note Recursion and recalculation of value_keys is handled
            # in the reserved keyword functions
            result = RESERVED_KEYWORDS[address_keys[0]](address_keys)
            return result
        except Exception as exc:
            # If the reserved keyword function fails, raise an exception
            raise RuntimeError(f'Error getting mapped value: {address}') from exc
    else:
        # If the first key is not a reserved keyword, get the value for the map address
        return _get_value_from_value_dict(address, **value_dicts)


def _get_value_from_value_dict(address, **value_dicts):
    """
    Takes in an address from the map and returns the value at that address from the value
    dictionaries.
    """
    # Split map_address into key_groups separated by OR keyword
    key_groups = address.split('.OR.')

    try:
        #Split Address from first key_group
        address_keys = key_groups[0].split('.')
        # Get the first value from the value dictionaries
        result = value_dicts[address_keys[0]]
        # Loop through the rest of the address keys and return the value in result
        for address_key in address_keys[1:]:
            LOGGER.debug('Getting Value for Key: %s', address_key)
            result = result[address_key]
        # If a result was found, return it
        return result
    except KeyError as exc:
        # If the first key_group failed, check if there are more key_groups
        if len(key_groups) > 1:
            new_target = '.OR.'.join(key_groups[1:])
            LOGGER.warning('Error getting value from value dictionary: %s Using Value from OR: %s',
                           key_groups[0],
                           new_target)
            # Rejoin the rest of the key_groups and send string back to _get_mapped_value
            return _get_mapped_value(new_target, **value_dicts)
        # If no more key_groups exist, raise an exception
        LOGGER.error('Failed to map value from value dictionary: %s', address)
        raise KeyError(f'Error getting value from value dictionary: {address}') from exc
