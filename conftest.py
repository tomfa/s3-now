import json
from typing import Callable, Dict, Optional, Union, Any

import pytest


@pytest.fixture
def request_builder() -> Callable:
    def fun(
        *,
        params: Dict[str, str] = None,
        method: Union[str] = "GET",
        headers: Optional[Dict] = None,
        body: Optional[str] = None,
    ) -> Dict:
        params = params or {}
        request = {"queryStringParameters": params, "httpMethod": method}
        if headers:
            request["headers"] = headers
        if body:
            assert type(body) == str, "Test request with non-string body"
            request["body"] = body
        return request

    return fun


@pytest.fixture
def api_key():
    # Defined in pytest.ini
    return "api-key-123"


@pytest.fixture
def project():
    # Defined in pytest.ini
    return "testproject"


@pytest.fixture
def other_api_key():
    # Defined in pytest.ini
    return "api-key-234"


@pytest.fixture
def other_project():
    # Defined in pytest.ini
    return "othertestproject"


@pytest.fixture
def invalid_api_key():
    # Defined in pytest.ini
    return "invalid-api-key"
