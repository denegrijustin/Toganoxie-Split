"""NOAA NOMADS raw-model adapter.

Builds GRIB-filter subset URLs, tracks model availability, and exposes
metadata for GFS, HRRR, RAP, NAM, and NBM.
"""

from datetime import datetime, timezone

import requests
import streamlit as st

BASE_URL = "https://nomads.ncep.noaa.gov/cgi-bin"
TIMEOUT = 12  # seconds
MODEL_AVAILABILITY_DELAY_HOURS = 5  # typical lag before data appears

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

NOMADS_MODELS: dict[str, dict] = {
    "gfs": {
        "name": "GFS (Global Forecast System)",
        "dataset": "gfs_0p25",
        "filter_name": "filter_gfs_0p25.pl",
        "run_hours": [0, 6, 12, 18],
        "max_forecast_hour": 384,
        "forecast_hour_step": 3,
        "file_template": "gfs.t{run:02d}z.pgrb2.0p25.f{fhr:03d}",
        "dir_template": "gfs.{date}/{run:02d}/atmos",
        "variables": [
            "TMP", "RH", "UGRD", "VGRD", "DPT",
            "PRATE", "REFC", "GUST", "CAPE", "PRES",
        ],
        "levels": [
            "2_m_above_ground", "10_m_above_ground",
            "surface", "entire_atmosphere",
        ],
    },
    "hrrr": {
        "name": "HRRR (High-Res Rapid Refresh)",
        "dataset": "hrrr_2d",
        "filter_name": "filter_hrrr_2d.pl",
        "run_hours": list(range(24)),
        "max_forecast_hour": 48,
        "forecast_hour_step": 1,
        "file_template": "hrrr.t{run:02d}z.wrfsfcf{fhr:02d}.grib2",
        "dir_template": "hrrr.{date}/conus",
        "variables": [
            "TMP", "RH", "UGRD", "VGRD", "DPT",
            "PRATE", "REFC", "GUST", "CAPE",
        ],
        "levels": [
            "2_m_above_ground", "10_m_above_ground",
            "surface", "entire_atmosphere",
        ],
    },
    "rap": {
        "name": "RAP (Rapid Refresh)",
        "dataset": "rap",
        "filter_name": "filter_rap.pl",
        "run_hours": list(range(24)),
        "max_forecast_hour": 21,
        "forecast_hour_step": 1,
        "file_template": "rap.t{run:02d}z.wrfprsf{fhr:02d}.grib2",
        "dir_template": "rap.{date}",
        "variables": [
            "TMP", "RH", "UGRD", "VGRD", "DPT",
            "PRATE", "REFC", "GUST", "CAPE",
        ],
        "levels": [
            "2_m_above_ground", "10_m_above_ground",
            "surface", "entire_atmosphere",
        ],
    },
    "nam": {
        "name": "NAM (North American Mesoscale)",
        "dataset": "nam",
        "filter_name": "filter_nam.pl",
        "run_hours": [0, 6, 12, 18],
        "max_forecast_hour": 84,
        "forecast_hour_step": 3,
        "file_template": "nam.t{run:02d}z.awphys{fhr:02d}.tm00.grib2",
        "dir_template": "nam.{date}",
        "variables": [
            "TMP", "RH", "UGRD", "VGRD", "DPT",
            "PRATE", "REFC", "GUST", "CAPE",
        ],
        "levels": [
            "2_m_above_ground", "10_m_above_ground", "surface",
        ],
    },
    "nbm": {
        "name": "NBM (National Blend of Models)",
        "dataset": "blend",
        "filter_name": "filter_blend.pl",
        "run_hours": [1, 7, 13, 19],
        "max_forecast_hour": 264,
        "forecast_hour_step": 1,
        "file_template": "blend.t{run:02d}z.core.f{fhr:03d}.co.grib2",
        "dir_template": "blend.{date}/{run:02d}/core",
        "variables": ["TMP", "DPT", "WIND", "GUST", "QPF"],
        "levels": [
            "2_m_above_ground", "10_m_above_ground", "surface",
        ],
    },
}

# ---------------------------------------------------------------------------
# Human-readable labels
# ---------------------------------------------------------------------------

NOMADS_VARIABLE_LABELS: dict[str, str] = {
    "TMP": "Temperature",
    "RH": "Relative Humidity",
    "UGRD": "U-Wind Component",
    "VGRD": "V-Wind Component",
    "DPT": "Dew Point",
    "PRATE": "Precipitation Rate",
    "REFC": "Composite Reflectivity",
    "GUST": "Wind Gust",
    "CAPE": "CAPE",
    "PRES": "Surface Pressure",
    "WIND": "Wind Speed",
    "QPF": "Quantitative Precipitation",
}

NOMADS_LEVEL_LABELS: dict[str, str] = {
    "2_m_above_ground": "2m AGL",
    "10_m_above_ground": "10m AGL",
    "surface": "Surface",
    "entire_atmosphere": "Entire Atmosphere",
}

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_available_models() -> dict:
    """Return the full NOMADS model registry."""
    return dict(NOMADS_MODELS)


def get_latest_run(model_id: str) -> tuple[str, int]:
    """Estimate the latest *available* run for *model_id*.

    NOMADS data typically appears 4-6 hours after the nominal run time.
    We subtract ``MODEL_AVAILABILITY_DELAY_HOURS`` from the current UTC
    time, then find the most recent run hour that has likely been
    published.

    Returns ``(date_str, run_hour)`` where *date_str* is ``YYYYMMDD``.

    Raises ``ValueError`` for unknown model IDs.
    """
    cfg = NOMADS_MODELS.get(model_id)
    if cfg is None:
        raise ValueError(f"Unknown NOMADS model: {model_id!r}")

    now = datetime.now(timezone.utc)
    effective_hour = now.hour - MODEL_AVAILABILITY_DELAY_HOURS

    run_hours = sorted(cfg["run_hours"])

    if effective_hour < run_hours[0]:
        # Rolled back to previous day's last run
        from datetime import timedelta

        prev = now - timedelta(days=1)
        return prev.strftime("%Y%m%d"), run_hours[-1]

    # Pick the largest run hour <= effective_hour
    best = run_hours[0]
    for rh in run_hours:
        if rh <= effective_hour:
            best = rh
        else:
            break

    return now.strftime("%Y%m%d"), best


def _parse_run(run: str, model_id: str) -> tuple[str, int]:
    """Parse a *run* string into ``(date_str, run_hour)``.

    Accepts formats:
    * ``"YYYYMMDD/HH"`` – explicit date and hour
    * ``"HH"`` or ``"H"`` – hour only; date taken from
      :func:`get_latest_run`
    """
    if "/" in run:
        parts = run.split("/", 1)
        return parts[0], int(parts[1])

    run_hour = int(run)
    date_str, _ = get_latest_run(model_id)
    return date_str, run_hour


def build_subset_url(
    model: str,
    run: str,
    forecast_hour: int,
    variables: list[str] | None = None,
    levels: list[str] | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> str:
    """Build a NOMADS GRIB-filter URL for the requested subset.

    Parameters
    ----------
    model:
        Model key (e.g. ``"gfs"``, ``"hrrr"``).
    run:
        Run identifier – either ``"YYYYMMDD/HH"`` (e.g. ``"20240101/06"``)
        or just an hour string (e.g. ``"06"``).
    forecast_hour:
        Forecast lead-time in hours.
    variables:
        GRIB variable names to include.  Defaults to all variables the
        model supports.
    levels:
        Level names to include.  Defaults to all levels the model
        supports.
    lat, lon:
        If both are provided, a ±1° subregion box is added.

    Returns
    -------
    str
        Fully-formed NOMADS filter URL.

    Raises
    ------
    ValueError
        If *model* is unknown or *forecast_hour* is out of range.
    """
    cfg = NOMADS_MODELS.get(model)
    if cfg is None:
        raise ValueError(f"Unknown NOMADS model: {model!r}")

    if forecast_hour < 0 or forecast_hour > cfg["max_forecast_hour"]:
        raise ValueError(
            f"Forecast hour {forecast_hour} out of range for {model} "
            f"(0–{cfg['max_forecast_hour']})"
        )

    date_str, run_hour = _parse_run(run, model)

    if variables is None:
        variables = list(cfg["variables"])
    if levels is None:
        levels = list(cfg["levels"])

    filename = cfg["file_template"].format(run=run_hour, fhr=forecast_hour)
    directory = cfg["dir_template"].format(date=date_str, run=run_hour)

    # Encode the directory with %2F separators
    dir_param = "%2F" + directory.replace("/", "%2F")

    url = (
        f"{BASE_URL}/{cfg['filter_name']}"
        f"?dir={dir_param}"
        f"&file={filename}"
    )

    for var in variables:
        url += f"&var_{var}=on"

    for lev in levels:
        url += f"&lev_{lev}=on"

    if lat is not None and lon is not None:
        url += (
            f"&subregion="
            f"&toplat={lat + 1}"
            f"&leftlon={lon - 1}"
            f"&rightlon={lon + 1}"
            f"&bottomlat={lat - 1}"
        )

    return url


# ---------------------------------------------------------------------------
# Availability validation (cached)
# ---------------------------------------------------------------------------


@st.cache_data(ttl=900)
def validate_model_availability(model_id: str) -> bool:
    """Check whether the NOMADS filter endpoint for *model_id* is reachable.

    Sends a lightweight HEAD request to the filter script.  Returns
    ``True`` when the server responds with any 2xx/3xx status, ``False``
    otherwise.  Results are cached for 15 minutes.
    """
    cfg = NOMADS_MODELS.get(model_id)
    if cfg is None:
        return False

    url = f"{BASE_URL}/{cfg['filter_name']}"
    try:
        resp = requests.head(url, timeout=TIMEOUT)
        return resp.status_code < 400
    except requests.RequestException:
        return False


@st.cache_data(ttl=900)
def get_validated_models() -> list[str]:
    """Return model IDs whose NOMADS endpoints are currently accessible.

    Results are cached for 15 minutes.
    """
    return [
        mid for mid in NOMADS_MODELS
        if validate_model_availability(mid)
    ]
