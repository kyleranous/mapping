import json
import os
import logging

import mapping

LOGGER = logging.getLogger(__name__)
LOG_LEVEL_SET = os.environ.get('LOG_LEVEL', 'DEBUG') or 'DEBUG'
LOG_LEVEL = logging.DEBUG if LOG_LEVEL_SET.lower() in ['debug'] else logging.INFO
LOGGER.setLevel(LOG_LEVEL)
logging.getLogger().addHandler(logging.StreamHandler())

dir_path = os.path.dirname(os.path.realpath(__file__))
# Load map file
with open(os.path.join(dir_path, 'demo', 'map.json')) as w:
    map_dict = json.load(w)
w.close()

with open(os.path.join(dir_path, 'demo', 'values.json')) as w:
    value_dict = json.load(w)
w.close()

result = mapping.map_dictionary(map_dict, **value_dict)
print('*' * 50)
print(json.dumps(result, indent=4))
