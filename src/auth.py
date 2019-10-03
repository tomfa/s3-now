import logging
import os
from typing import Dict, Optional

from exceptions import NotAuthenticated
from src import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _project_lookup(key: str) -> Optional[str]:
    projects = os.environ.get("ALLOWED_PROJECTS", "").split(",")
    for project in projects:
        try:
            name, api_key = project.split("-", 1)
            if api_key == key:
                return name
        except ValueError:
            logger.error(f"Invalid ALLOWED_PROJECTS key in env var: {project}")
    return None


def _authorize_key(*, api_key: Optional[str]) -> str:
    if not api_key:
        raise NotAuthenticated("API key not provided")
    project = _project_lookup(api_key)
    if not project:
        raise NotAuthenticated(f"API key is not valid: {api_key[:4]}...")
    logger.info(f"Using project={project}")
    return project


def _get_request_auth_key(
    *, params: Dict[str, str], payload: Dict[str, str], headers: Dict[str, str]
) -> Optional[str]:
    if params.get("api-key"):
        logger.info("Using api-key from query parameters.")
        return params["api-key"]
    if payload.get("api-key"):
        logger.info("Using api-key from payload.")
        return payload["api-key"]
    auth_header = (headers.get("Authorization") or "").split()
    if auth_header:
        logger.info("Using api-key from Authorization headers.")
        return auth_header[-1]


def authorize_request(event) -> str:
    payload = requests.get_payload_from_event(event)
    params = event.get("queryStringParameters") or {}
    api_key = _get_request_auth_key(
        params=params, payload=payload, headers=event.get("headers") or {}
    )
    return _authorize_key(api_key=api_key)
