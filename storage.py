import json
from json import JSONDecodeError
import logging
import os
from typing import Dict, Optional

from exceptions import NotAuthenticated, InvalidPayload, MissingDataKey


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def project_lookup(key: str) -> Optional[str]:
    projects = os.environ.get("ALLOWED_PROJECTS", "").split(",")
    for project in projects:
        try:
            name, api_key = project.split("-", 1)
            if api_key == key:
                return name
        except ValueError:
            logger.error(f"Invalid ALLOWED_PROJECTS key in env var: {project}")
    return None


def authorize(api_key: Optional[str]) -> str:
    if not api_key:
        raise NotAuthenticated("API key not provided")
    project = project_lookup(api_key)
    if not project:
        raise NotAuthenticated(f"API key is not valid: {api_key[:4]}...")
    logger.info(f"Using project={project}")
    return project


def get_authorization_key(
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


def get_payload(event) -> Dict[any, any]:
    try:
        body = (event.get("body") or "").strip()
        return body and json.loads(body) or {}
    except JSONDecodeError as ex:
        raise InvalidPayload(ex)


def get_json_data(project: str, key: str):
    logger.info(f"Retrieving {project}.{key}")
    return {"test": 1}


def set_json_data(project: str, key: str, data: Dict[any, any]):
    logger.info(f"Setting {project}.{key} to {data}")
    return {"test": 1}


def json_request(event, context):
    try:
        payload = get_payload(event)
        params = event.get("queryStringParameters") or {}
        api_key = get_authorization_key(
            params=params, payload=payload, headers=event.get("headers") or {}
        )
        project = authorize(api_key)
        key = params.get("key")
        method = event["httpMethod"]
        if not key:
            raise MissingDataKey()
        if method == "GET":
            data = get_json_data(project, key)
        elif method == "POST":
            data = set_json_data(project, key, payload)
        else:
            logger.error(f"Unknown method {method}")
            raise Exception(f"HTTP method {method} is not supported.")
        return {"statusCode": 200, "body": json.dumps(data)}
    except InvalidPayload as ex:
        logger.warning(ex)
        return {"statusCode": 400, "body": "Invalid JSON payload"}
    except NotAuthenticated as exc:
        return {"statusCode": 401, "body": str(exc)}
    except MissingDataKey:
        return {
            "statusCode": 400,
            "body": f'"key" must be specified in query parameters.',
        }
    except Exception as exc:
        logger.error(exc)
        return {"statusCode": 500, "body": "Unknown error. Check logs."}
