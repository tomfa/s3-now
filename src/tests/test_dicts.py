import pytest

from src.dicts import get_key_value_from_dict, set_dict_data


@pytest.fixture
def data():
    return {"recipe": {"cheese": "percorino", "carbs": "pasta"}}


def test_get_key_value_from_dict(data):
    selected_data = get_key_value_from_dict(data, keys=["recipe"])

    assert selected_data == {"cheese": "percorino", "carbs": "pasta"}


def test_get_key_value_from_empty_dict(data):
    selected_data = get_key_value_from_dict({}, keys=["recipe"])

    assert selected_data is None


def test_get_nested_key_value_from_dict(data):
    selected_data = get_key_value_from_dict(data, keys=["recipe", "carbs"])

    assert selected_data == "pasta"


@pytest.mark.parametrize("keys", ([], [""]))
def test_get_value_with_empty_key(data, keys):
    selected_data = get_key_value_from_dict(data, keys=keys)

    assert selected_data == data


@pytest.mark.parametrize("new_data", [None, "fisk", 1, {"a-key": 1}])
def test_update_value_without_key(new_data):
    a = {"a-key": "a-value", "common-key": "a-value"}

    data = set_dict_data(a, keys=[], new_data=new_data)

    assert data == new_data


def test_update_existing_value_with_dict():
    a = {"a-key": "a-value", "common-key": "a-value"}
    new_data = {"b-key": "b-value", "nested-key": "b-value"}

    data = set_dict_data(a, keys=["common-key"], new_data=new_data)

    assert data == {
        "a-key": "a-value",
        "common-key": {"b-key": "b-value", "nested-key": "b-value"},
    }


def test_update_using_nonexisting_key_path():
    a = {"a-key": "a-value", "common-key": "a-value"}
    new_data = {"b-key": "b-value", "nested-key": "b-value"}

    data = set_dict_data(a, keys=["fish", "chips"], new_data=new_data)

    assert data == {
        "a-key": "a-value",
        "common-key": "a-value",
        "fish": {"chips": {"b-key": "b-value", "nested-key": "b-value"}},
    }
