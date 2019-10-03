import json
import logging
from typing import Dict

from exceptions import InvalidPayload


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_payload_from_event(event) -> Dict[any, any]:
    try:
        body = (event.get("body") or "").strip()
        return body and json.loads(body) or {}
    except json.JSONDecodeError as ex:
        raise InvalidPayload(ex)
