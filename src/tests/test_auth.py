import pytest

import exceptions
from src.auth import authorize_request


def test_authorize_accepts_auth_key_in_params(
    api_key, project, request_builder
):
    request = request_builder(params={"api-key": api_key})

    authorized_project = authorize_request(request)

    assert authorized_project == project


def test_authorize_accepts_auth_key_in_post_payload(
    api_key, project, request_builder
):
    request = request_builder(body={"api-key": api_key})

    authorized_project = authorize_request(request)

    assert authorized_project == project


def test_authorize_accepts_auth_key_in_header(
    api_key, project, request_builder
):
    request = request_builder(headers={"Authorization": f"Bearer {api_key}"})

    authorized_project = authorize_request(request)

    assert authorized_project == project


def test_authorize_attempts_prioritizes_params(
    api_key, project, request_builder, invalid_api_key
):
    request = request_builder(
        params={"api-key": api_key},
        body={"api-key": invalid_api_key},
        headers={"Authorization": f"Bearer {invalid_api_key}"},
    )

    authorized_project = authorize_request(request)

    assert authorized_project == project


def test_authorize_attempts_prioritizes_payload_over_header(
    api_key, project, request_builder, invalid_api_key
):
    request = request_builder(
        body={"api-key": api_key},
        headers={"Authorization": f"Bearer {invalid_api_key}"},
    )

    authorized_project = authorize_request(request)

    assert authorized_project == project


def test_accepts_multiple_auth_projects(
    other_api_key, other_project, request_builder
):
    request = request_builder(body={"api-key": other_api_key})

    authorized_project = authorize_request(request)

    assert authorized_project == other_project


def test_raises_on_invalid_auth_key(invalid_api_key, request_builder):
    request = request_builder(body={"api-key": invalid_api_key})

    with pytest.raises(exceptions.NotAuthenticated):
        authorize_request(request)
