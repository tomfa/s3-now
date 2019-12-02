from src.s3 import JSON_LOCATION_KEY, get_json_data


def test_get_json_data(mocker):
    s3_download = mocker.patch("src.s3._download_file_as_string")
    s3_download.return_value = "{}"

    get_json_data("project")

    s3_download.assert_called_once_with("project", file=JSON_LOCATION_KEY)


def test_get_payload_from_request(mocker):
    s3_download = mocker.patch("src.s3._download_file_as_string")
    s3_download.return_value = "{}"

    get_json_data("project", key="ost")

    s3_download.assert_called_once_with("project", file=JSON_LOCATION_KEY)
