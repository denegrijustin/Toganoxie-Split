from unittest.mock import MagicMock, patch

import services.open_meteo as om


def test_open_meteo_module_imports() -> None:
    assert om is not None


def test_available_models_non_empty() -> None:
    assert isinstance(om.AVAILABLE_MODELS, list)
    assert len(om.AVAILABLE_MODELS) > 0


@patch("services.open_meteo.requests.get")
def test_get_forecast(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "current": {"temperature_2m": 72.0},
        "hourly": {"temperature_2m": [70.0, 71.0]},
    }
    mock_get.return_value.raise_for_status = MagicMock()

    result = om.get_forecast(39.1, -95.1)
    assert "current" in result
    assert result["current"]["temperature_2m"] == 72.0


@patch("services.open_meteo.requests.get")
def test_validate_model_true(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "hourly": {"temperature_2m": [70.0, 71.0, 72.0]}
    }
    mock_get.return_value.raise_for_status = MagicMock()

    assert om.validate_model(39.1, -95.1, "gfs_seamless") is True


@patch("services.open_meteo.requests.get")
def test_validate_model_false(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {"hourly": {"temperature_2m": []}}
    mock_get.return_value.raise_for_status = MagicMock()

    assert om.validate_model(39.1, -95.1, "bad_model") is False


@patch("services.open_meteo.requests.get")
def test_get_model_comparison(mock_get: MagicMock) -> None:
    mock_get.return_value.json.return_value = {
        "hourly": {"temperature_2m": [65.0]}
    }
    mock_get.return_value.raise_for_status = MagicMock()

    result = om.get_model_comparison(39.1, -95.1, models=["gfs_seamless", "hrrr_conus"])
    assert "gfs_seamless" in result
    assert "hrrr_conus" in result


@patch("services.open_meteo.requests.get")
def test_get_forecast_error_returns_empty(mock_get: MagicMock) -> None:
    import requests
    mock_get.side_effect = requests.RequestException("network error")

    result = om.get_forecast(39.1, -95.1, model="gfs_seamless")
    assert result == {}
