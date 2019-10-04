import json
import logging

from src import auth, requests, s3
from exceptions import NotAuthenticated, InvalidPayload, MissingDataKey


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        payload = requests.get_payload_from_request(event)
        params = event.get("queryStringParameters") or {}
        project = auth.authorize_request(event)
        key = params.get("key")
        method = event["httpMethod"]
        if not key:
            raise MissingDataKey()
        if method == "GET":
            data = s3.get_json_data_from_s3(project, key=key)
        elif method == "POST":
            data = s3.set_json_data_in_s3(project, key, payload)
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
