import json

from botocore.exceptions import ClientError
import pytest

from exceptions import NotAuthenticated
from src.api.json_api import handler
from src import s3, auth


@pytest.fixture
def mock_auth(mocker):
    def fun(project=None, *, fail=False):
        auth_mocker = mocker.patch.object(auth, "authorize_request")
        if fail:
            auth_mocker.side_effect = NotAuthenticated("Mocked failure")
        else:
            auth_mocker.return_value = project
        return auth_mocker

    return fun


@pytest.fixture
def mock_get_data(mocker):
    def fun(existing_data):
        data_mock = mocker.patch("src.s3._download_file_as_string")
        data_mock.return_value = json.dumps(existing_data)
        return data_mock

    return fun


@pytest.fixture
def mock_upload_data(mocker):
    def fun(fail=False):
        mock = mocker.patch("src.s3._upload_file")
        if fail:
            mock.side_effect = ClientError("Something something about boto3")
        return mock

    return fun


def test_get_request(mock_auth, mock_get_data, request_builder):
    mock_auth()
    mock_get_data({"fish": "chips"})

    request = request_builder(
        method="GET", params=dict(api_key="api-key", key="fish")
    )
    response = handler(request, {})

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps("chips")


def test_post_request(
    mock_auth, mock_get_data, mock_upload_data, request_builder
):
    mock_auth()
    mock_upload_data()
    mock_get_data({"fish": "chips"})

    request = request_builder(
        method="POST",
        params=dict(api_key="api_key", key="data"),
        body=json.dumps(1),
    )
    response = handler(request, {})

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps({"fish": "chips", "data": 1})


def test_post_request_with_bad_data_returns_400(mock_auth, request_builder):
    mock_auth()

    request = request_builder(
        method="POST",
        params=dict(api_key="api_key", key="data"),
        body='{"JSON WHO"}',
    )
    response = handler(request, {})

    assert response["statusCode"] == 400
    assert "Invalid JSON" in response["body"]


def test_post_without_key(mock_auth, request_builder):
    mock_auth()

    request = request_builder(
        method="POST", params=dict(api_key="api_key"), body="{}"
    )
    response = handler(request, {})

    assert response["statusCode"] == 400
    assert "must be specified" in response["body"]


def test_auth_failure_returns_401(mock_auth, request_builder):
    mock_auth(fail=True)

    request = request_builder(
        method="GET", params=dict(api_key="api-key", key="fish")
    )
    response = handler(request, {})

    assert response["statusCode"] == 401


def test_mock_unknown_error_returns_generic_500(mocker, request_builder):
    mock = mocker.patch("src.requests.get_payload_from_request")
    mock.side_effect = Exception("Unexpected and sensitive info")

    request = request_builder(
        method="GET", params=dict(api_key="api-key", key="fish")
    )
    response = handler(request, {})

    assert response["statusCode"] == 500
    assert "Unknown error" in response["body"]
    assert "sensitive" not in response["body"]
