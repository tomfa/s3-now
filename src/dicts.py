import logging
from typing import Dict, Optional, Any


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_key_value_from_dict(data: Dict, *, key: str) -> Optional[Dict]:
    sub_keys = key and key.split(".") or []
    pointer = data
    for sub_key in sub_keys:
        if sub_key not in pointer:
            return None
        pointer = pointer[sub_key]
    return pointer


def merge_dict_with_data(
    dictionary: Optional[Dict], *, key_path: str, data: Any
) -> Dict:
    if not key_path:
        # Overwrites everything
        return data
    dictionary = dictionary or {}

    sub_keys = key_path.split(".")
    last_key = sub_keys[-1]
    pointer = dictionary
    for sub_key in sub_keys[:-1]:
        if sub_key not in pointer:
            pointer[sub_key] = {}
        pointer = pointer[sub_key]
    pointer[last_key] = data
    return pointer
