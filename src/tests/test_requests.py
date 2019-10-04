from src.requests import get_payload_from_request


def test_get_payload_from_request(request_builder):
    payload = {"cheesecake": "percorinocheesecake"}

    request = request_builder(method="POST", body=payload)

    assert get_payload_from_request(request) == payload


def test_get_payload_when_empty(request_builder):
    request = request_builder()

    assert get_payload_from_request(request) == {}
