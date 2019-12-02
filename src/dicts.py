import logging
from typing import Dict, Optional, Any, List


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_key_value_from_dict(data: Dict, *, keys: List[str]) -> Optional[Dict]:
    keys = keys or []
    pointer = data
    for sub_key in keys:
        if sub_key == "":
            continue
        if sub_key not in pointer:
            return None
        pointer = pointer[sub_key]
    return pointer


def _merge(dictionary: Dict, new_data: Any) -> Any:
    if type(dictionary) != dict:
        return new_data
    if type(new_data) != dict:
        return new_data
    for key, value in new_data.items():
        dictionary[key] = _merge(dictionary.get(key), value)
    return dictionary


def set_dict_data(
    dictionary: Optional[Dict], *, keys: Optional[List] = None, new_data: Any
) -> Dict:
    if not keys:
        return new_data
    dictionary = dictionary or {}

    first = keys[0]
    remaining_keys = keys[1:]
    dictionary[first] = set_dict_data(
        dictionary.get(first), keys=remaining_keys, new_data=new_data
    )
    return dictionary
