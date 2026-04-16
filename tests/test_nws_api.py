from unittest.mock import MagicMock, patch

import requests
import services.nws_api as nws


def test_nws_module_imports() -> None:
    assert nws is not None


@patch("services.nws_api._get")
def test_get_point_metadata(mock__get: MagicMock) -> None:
    mock__get.return_value = {
        "properties": {"forecast": "https://api.weather.gov/forecast"}
    }
    result = nws.get_point_metadata(10.0, -10.0)
    assert "forecast" in result


@patch("services.nws_api._get")
def test_get_forecast(mock__get: MagicMock) -> None:
    mock__get.side_effect = [
        {"properties": {"forecast": "https://api.weather.gov/forecast"}},
        {"properties": {"periods": [{"name": "Tonight", "temperature": 55}]}},
    ]
    result = nws.get_forecast(11.0, -11.0)
    assert len(result) == 1
    assert result[0]["name"] == "Tonight"


@patch("services.nws_api._get")
def test_get_alerts(mock__get: MagicMock) -> None:
    mock__get.return_value = {
        "features": [
            {"properties": {"event": "Tornado Warning", "severity": "Extreme"}}
        ]
    }
    result = nws.get_alerts("KS")
    assert len(result) == 1
    assert result[0]["event"] == "Tornado Warning"


@patch("services.nws_api._get")
def test_get_alerts_for_point(mock__get: MagicMock) -> None:
    mock__get.return_value = {
        "features": [
            {"properties": {"event": "Flood Watch", "severity": "Moderate"}}
        ]
    }
    result = nws.get_alerts_for_point(12.0, -12.0)
    assert len(result) == 1
    assert result[0]["event"] == "Flood Watch"


@patch("services.nws_api._get")
def test_get_point_metadata_request_exception(mock__get: MagicMock) -> None:
    mock__get.return_value = {}
    result = nws.get_point_metadata(13.0, -13.0)
    assert result == {}


@patch("services.nws_api._get")
def test_get_alerts_request_exception(mock__get: MagicMock) -> None:
    mock__get.return_value = {}
    result = nws.get_alerts("ZZ")
    assert result == []


@patch("services.nws_api._get")
def test_get_alerts_for_point_request_exception(mock__get: MagicMock) -> None:
    mock__get.return_value = {}
    result = nws.get_alerts_for_point(14.0, -14.0)
    assert result == []


@patch("services.nws_api.requests.get")
def test_private_get_handles_request_exception(mock_get: MagicMock) -> None:
    mock_get.side_effect = requests.RequestException("network error")
    result = nws._get("https://example.com")
    assert result == {}
