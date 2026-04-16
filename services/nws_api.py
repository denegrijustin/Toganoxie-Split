"""NWS API adapter – talks to api.weather.gov and caches responses."""

import requests
import streamlit as st

BASE_URL = "https://api.weather.gov"
HEADERS = {"User-Agent": "toganoxie-split/2.0 (weather-app)"}
TIMEOUT = 10  # seconds


def _get(url: str) -> dict:
    """Perform a GET request and return the parsed JSON, or {} on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError):
        return {}


@st.cache_data(ttl=600)
def get_point_metadata(lat: float, lon: float) -> dict:
    """Return NWS point metadata for the given coordinates.

    Calls ``GET /points/{lat},{lon}`` and returns the ``properties`` dict,
    which contains links to forecast, forecastHourly, forecastGridData,
    observationStations, etc.
    """
    data = _get(f"{BASE_URL}/points/{lat},{lon}")
    return data.get("properties", {})


@st.cache_data(ttl=900)
def get_forecast(lat: float, lon: float) -> list[dict]:
    """Return the list of forecast period dicts for the given coordinates.

    Uses :func:`get_point_metadata` to resolve the forecast URL, then
    fetches and returns the period entries.
    """
    meta = get_point_metadata(lat, lon)
    forecast_url = meta.get("forecast", "")
    if not forecast_url:
        return []
    data = _get(forecast_url)
    return data.get("properties", {}).get("periods", [])


@st.cache_data(ttl=900)
def get_hourly_forecast(lat: float, lon: float) -> list[dict]:
    """Return the list of hourly forecast period dicts.

    Uses :func:`get_point_metadata` to resolve the forecastHourly URL,
    then fetches and returns the period entries.
    """
    meta = get_point_metadata(lat, lon)
    hourly_url = meta.get("forecastHourly", "")
    if not hourly_url:
        return []
    data = _get(hourly_url)
    return data.get("properties", {}).get("periods", [])


@st.cache_data(ttl=300)
def get_alerts(state: str) -> list[dict]:
    """Return active weather alerts for a US state (two-letter code).

    Calls ``GET /alerts/active?area={state}`` and returns a list of
    alert feature property dicts.
    """
    data = _get(f"{BASE_URL}/alerts/active?area={state}")
    features = data.get("features", [])
    return [f.get("properties", {}) for f in features]


@st.cache_data(ttl=300)
def get_alerts_for_point(lat: float, lon: float) -> list[dict]:
    """Return active weather alerts for a specific lat/lon point.

    Calls ``GET /alerts/active?point={lat},{lon}`` and returns a list of
    alert feature property dicts.
    """
    data = _get(f"{BASE_URL}/alerts/active?point={lat},{lon}")
    features = data.get("features", [])
    return [f.get("properties", {}) for f in features]
