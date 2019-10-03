import json
import logging
import os
from tempfile import TemporaryFile
from typing import Any

from boto3 import resource

from botocore.exceptions import ClientError

from src.dicts import get_key_value_from_dict, merge_dict_with_data


JSON_LOCATION_KEY = "json"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = resource("s3").Bucket(os.environ.get("S3_BUCKET"))


def _get_absolute_file_key(project: str, *, key):
    return f"{project}/{key}"


def download_file_as_string(project: str, *, key: str):
    file_key = _get_absolute_file_key(project, key=key)
    logger.info(f"Downloading {file_key}")
    with TemporaryFile() as tmp_file:
        s3.download_fileobj(file_key, tmp_file)
        tmp_file.seek(0)
        return tmp_file.read()


def upload_file(data: bytes, *, project: str, content_type: str, key: str):
    file_key = _get_absolute_file_key(project, key=key)
    s3.put_object(
        ACL="private", ContentType=content_type, Key=file_key, Body=data
    )


def get_json_data_from_s3(project: str, *, key: str = "") -> Any:
    string_data = download_file_as_string(project, key=JSON_LOCATION_KEY)
    json_data = json.loads(string_data)
    return get_key_value_from_dict(json_data, key=key)


def set_json_data_in_s3(project: str, key: str, data: Any):
    logger.info(f"Setting {project}.{key} to {data}")
    try:
        project_data = get_json_data_from_s3(project)
    except ClientError:
        logger.info(
            "Generic botocore ClientError. Assuming missing key", exc_info=True
        )
        project_data = {}
    new_data = merge_dict_with_data(project_data, key_path=key, data=data)
    upload_file(
        json.dumps(new_data).encode(),
        project=project,
        key=JSON_LOCATION_KEY,
        content_type="application/json",
    )
    return new_data
