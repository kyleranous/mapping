# Mapping

Mapping is a python library used to map Multiple dictionaries into a single output dictionary.

## Concept of Operation
`mapping.map_dictionary` takes in (2) arguments: A Map Dictionary, and a nested dictionary of value dictionaries. It will use the keys of the Map Dictionary to create a return dictionary with the values from the value address in the value dictionaries.
Ex:
```python
import mapping


# Create Map Dictionary:
map_dict = {
    'key1': 'value_1.id2,
    'key2': 'value_2.id1
}

value_dicts = {
    'value_1': {
        'id1': 'This is the value for ID1',
        'id2': 'This is the value for ID2'
    },
    'value_2': {
        'id1': 756,
        'id2': 'Hello World'
    }
}

results = mapping.map_dictionary(map_dict, **value_dicts)
print(json.dumps(results, indent=4))

>>> {
    "key1": "This is the value for ID2",
    "key2": 756
}
```
Using this function, Map files could be stored as `json` files and dynamically called or updated without requiring a change to the underlying code base. 


## Tasks
 - [ ] `MAP_ARRAY` - Need functionality to beable to create an array of dictionaries if needed.
 ex: If I need to map to an array of objects, I should define the Array with a single object that contains the mapping, the object should contain a target key that identifies which value in the value dicts to iterate through [Issue-1](/issues/1)


## Usage

### Static Values
Several `static` values can be used in the mapping files if you need your output to contain data that doesn't depend on the value dictionaries

#### SKIP
`SKIP` will pass over the key in the mapping file. This is useful if you want to make a default mapping file but not all fields are required

#### NULL
`NULL` will pase `None` to the Key in the output dictionary

#### STRING
`STRING` will pass a static String to the Key in the output dictionary.
*Note*: Since the Mapping Addresses are passed as a String, string does not alow the use of `OR`

#### INT
`INT` will pass a static Integer to the Key in the output dictionary. 
Because the values passed from the Map file are `Strings`, the value needs to be converted to an Integer. If a non-convertable string is passed, it will return an Error. 

#### FLOAT
`FLOAT` will pass a static Float to the Key in the output dictionary. `FLOAT` is unique in that it will look at the 2nd AND third positions in the address to parse the full value.

`FLOAT.1` will return `1.0`
`FLOAT.1.5` will return `1.5`
`FLOAT.1.OR.STRING.Hello` will return `1.0`

#### LIST
`LIST` allows the creation of a list of `STRING` values. `LIST` uses a comma-seperated string to create a Python list in the dictionary
`LIST.Hello World, How, are you, ?` will create the list:
`['Hello World', 'How', 'are you', '?']`

#### BOOL
`BOOL` allows the mapping of a static `true/false` value to the mapped key

#### OR
`OR` allows the adding of backup values to be mapped if the primary value fails.
`value_1.id3.OR.STRING.Key id3 was not present`
In the event of a failure trying to map `value_1.id3` the key would be mapped to a static string `Key id3 was not present`

Multiple `OR` keywords can be chained together to provide more fallback options if wanted.

This can be useful a pricing type situation where your recieving values will negate a field if the value is 0 or null, but the follow on processor requires the field:
`item_price.total.OR.INT.0`

In the above code example, `mapper.map_dict` will first look for a value dictionary called `item_price`, if it finds it, it will look for a key called `total` and try to copy the value, if finding either of those objects fail, it will map a static Integer `0`

### Other Uses

#### Accessing Values from Nested Dictionaries
A Key from the map can be mapped to a nested dictionary by continuing the dot-notation
Ex:

```python
value_dict = {
    'value1': {
        'nested1': {
            'id1': 'This is the nested value'
        }
    }
}

map_dict = {
    'key1': 'value1.nested1.id1'
}

print(mapping.map_dict(map_dict, **value_dict))
>>> {
    'key1': 'This is the nested value'
}
```


#### Mapping a key to an entire value dictionary object
If a mapping file key is mapped to a value that holds a dictionary object, the entire dictionary object will mapped the to key in the output dictionary.
Ex:

```python
value_dict = {
    'value1': {
        'nested1': {
            'id1': 'This is the nested value'
        }
    }
}

map_dict = {
    'key1': 'value1.nested1'
}

print(mapping.map_dict(map_dict, **value_dict))
>>> {
    'key1': {
        'id1': 'This is the nested value'
    }
}
```