"""Open-Meteo adapter – fetches forecast data from the Open-Meteo API."""

import requests
import streamlit as st

BASE_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 15  # seconds

AVAILABLE_MODELS = [
    "gfs_seamless",
    "gfs_global",
    "hrrr_conus",
    "ecmwf_ifs025",
    "gem_seamless",
    "icon_seamless",
    "meteofrance_seamless",
    "jma_seamless",
    "ncep_nbm_conus",
    "ncep_gefs025",
]

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation_probability",
    "precipitation",
    "rain",
    "snowfall",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
    "cape",
    "freezing_level_height",
]

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
]

CURRENT_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "surface_pressure",
]


def _build_params(
    lat: float,
    lon: float,
    *,
    hourly: list[str] | None = None,
    daily: list[str] | None = None,
    current: list[str] | None = None,
    model: str | None = None,
) -> dict:
    """Build query parameters for an Open-Meteo request."""
    params: dict[str, str] = {
        "latitude": str(lat),
        "longitude": str(lon),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
    }
    if hourly:
        params["hourly"] = ",".join(hourly)
    if daily:
        params["daily"] = ",".join(daily)
    if current:
        params["current"] = ",".join(current)
    if model:
        params["models"] = model
    return params


def _get(params: dict) -> dict:
    """Perform a GET request against the Open-Meteo API and return JSON."""
    try:
        resp = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError):
        return {}


@st.cache_data(ttl=900)
def get_forecast(lat: float, lon: float, model: str | None = None) -> dict:
    """Fetch forecast from Open-Meteo.

    Requests current, hourly, and daily variables in US units
    (fahrenheit, mph, inch). If *model* is specified it is included in
    the request. Returns the full JSON response dict, or ``{}`` on error.
    """
    params = _build_params(
        lat,
        lon,
        hourly=HOURLY_VARIABLES,
        daily=DAILY_VARIABLES,
        current=CURRENT_VARIABLES,
        model=model,
    )
    return _get(params)


@st.cache_data(ttl=900)
def get_model_comparison(
    lat: float,
    lon: float,
    models: list[str] | None = None,
    variables: list[str] | None = None,
) -> dict[str, dict]:
    """Fetch forecasts for multiple models and compare them.

    Returns a mapping of *model_name* → *response_dict*.  Models that
    fail are silently skipped.
    """
    if models is None:
        models = list(AVAILABLE_MODELS)
    if variables is None:
        variables = list(HOURLY_VARIABLES)

    results: dict[str, dict] = {}
    for model in models:
        params = _build_params(lat, lon, hourly=variables, model=model)
        data = _get(params)
        if data:
            results[model] = data
    return results


@st.cache_data(ttl=1800)
def validate_model(lat: float, lon: float, model: str) -> bool:
    """Check whether *model* returns valid hourly data for the location.

    Makes a minimal request (single hourly variable) and returns
    ``True`` only when the response contains non-empty hourly data.
    """
    params = _build_params(
        lat, lon, hourly=["temperature_2m"], model=model
    )
    data = _get(params)
    hourly = data.get("hourly", {})
    temps = hourly.get("temperature_2m", [])
    return len(temps) > 0


@st.cache_data(ttl=1800)
def get_validated_models(lat: float, lon: float) -> list[str]:
    """Return the subset of :data:`AVAILABLE_MODELS` that produce data."""
    return [m for m in AVAILABLE_MODELS if validate_model(lat, lon, m)]
