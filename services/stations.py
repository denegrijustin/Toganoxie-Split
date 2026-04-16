"""Radar station metadata adapter – fetches and parses NEXRAD station data."""

from __future__ import annotations

import math

import requests
import streamlit as st

NEXRAD_STATIONS_URL = (
    "https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt"
)
HEADERS = {"User-Agent": "toganoxie-split/2.0 (weather-app)"}
TIMEOUT = 15  # seconds

# US states + territories for filtering
_US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "GU", "PR", "VI", "AS", "MP",
}

# Hardcoded fallback of ~15 major NEXRAD stations
_FALLBACK_STATIONS: list[dict] = [
    {"icao": "KTLX", "name": "Oklahoma City", "state": "OK", "lat": 35.3331, "lon": -97.2778, "elevation": 1213.0, "type": "NEXRAD"},
    {"icao": "KICT", "name": "Wichita", "state": "KS", "lat": 37.6545, "lon": -97.4428, "elevation": 1335.0, "type": "NEXRAD"},
    {"icao": "KFWS", "name": "Dallas/Fort Worth", "state": "TX", "lat": 32.5731, "lon": -97.3033, "elevation": 683.0, "type": "NEXRAD"},
    {"icao": "KLOT", "name": "Chicago", "state": "IL", "lat": 41.6044, "lon": -88.0847, "elevation": 663.0, "type": "NEXRAD"},
    {"icao": "KJFK", "name": "New York City", "state": "NY", "lat": 40.6399, "lon": -73.7787, "elevation": 87.0, "type": "NEXRAD"},
    {"icao": "KLAX", "name": "Los Angeles", "state": "CA", "lat": 33.9425, "lon": -118.4081, "elevation": 99.0, "type": "NEXRAD"},
    {"icao": "KFFC", "name": "Atlanta", "state": "GA", "lat": 33.3636, "lon": -84.5658, "elevation": 858.0, "type": "NEXRAD"},
    {"icao": "KBMX", "name": "Birmingham", "state": "AL", "lat": 33.1722, "lon": -86.7697, "elevation": 644.0, "type": "NEXRAD"},
    {"icao": "KMOB", "name": "Mobile", "state": "AL", "lat": 30.6794, "lon": -88.2397, "elevation": 208.0, "type": "NEXRAD"},
    {"icao": "KDVN", "name": "Davenport", "state": "IA", "lat": 41.6117, "lon": -90.5808, "elevation": 754.0, "type": "NEXRAD"},
    {"icao": "KMPX", "name": "Minneapolis", "state": "MN", "lat": 44.8489, "lon": -93.5653, "elevation": 942.0, "type": "NEXRAD"},
    {"icao": "KEAX", "name": "Kansas City", "state": "MO", "lat": 38.8103, "lon": -94.2644, "elevation": 995.0, "type": "NEXRAD"},
    {"icao": "KDMX", "name": "Des Moines", "state": "IA", "lat": 41.7311, "lon": -93.7228, "elevation": 981.0, "type": "NEXRAD"},
    {"icao": "KARX", "name": "La Crosse", "state": "WI", "lat": 43.8228, "lon": -91.1911, "elevation": 1276.0, "type": "NEXRAD"},
    {"icao": "KLSX", "name": "St. Louis", "state": "MO", "lat": 38.6986, "lon": -90.6828, "elevation": 608.0, "type": "NEXRAD"},
]


def _parse_nexrad_line(line: str) -> dict | None:
    """Parse a single fixed-width line from nexrad-stations.txt.

    Column positions (1-based → 0-based slices):
        ICAO      10-13   → [9:13]
        NAME      21-50   → [20:50]
        COUNTRY   52-71   → [51:71]
        ST        73-74   → [72:74]
        LAT      107-115  → [106:115]
        LON      117-126  → [116:126]
        ELEV     128-133  → [127:133]
        STNTYPE  141-190  → [140:190]
    """
    if len(line) < 133:
        return None

    icao = line[9:13].strip()
    if not icao or len(icao) != 4:
        return None

    state = line[72:74].strip()
    if state not in _US_STATES:
        return None

    name_raw = line[20:50].strip()
    if not name_raw:
        return None

    try:
        lat = float(line[106:115].strip())
        lon = float(line[116:126].strip())
    except (ValueError, IndexError):
        return None

    try:
        elev = float(line[127:133].strip())
    except (ValueError, IndexError):
        elev = 0.0

    stn_type = line[140:190].strip() if len(line) > 140 else ""
    if not stn_type:
        stn_type = "NEXRAD"

    return {
        "icao": icao,
        "name": name_raw.title(),
        "state": state,
        "lat": lat,
        "lon": lon,
        "elevation": elev,
        "type": stn_type,
    }


@st.cache_data(ttl=86400)
def get_stations() -> list[dict]:
    """Fetch and parse NEXRAD station metadata.

    Try primary source first (NCEI nexrad-stations.txt).
    On error, return a hardcoded fallback list.

    Returns list of dicts with keys:
        icao, name, state, lat, lon, elevation, type
    Filtered to US stations only.  Cached for 24 hours.
    """
    try:
        resp = requests.get(
            NEXRAD_STATIONS_URL, headers=HEADERS, timeout=TIMEOUT
        )
        resp.raise_for_status()
        lines = resp.text.splitlines()

        stations: list[dict] = []
        # Skip the first 2 header lines
        for line in lines[2:]:
            parsed = _parse_nexrad_line(line)
            if parsed is not None:
                stations.append(parsed)

        if stations:
            return stations
    except (requests.RequestException, ValueError, IndexError):
        pass

    return list(_FALLBACK_STATIONS)


def find_nearest_station(
    lat: float, lon: float, stations: list[dict] | None = None
) -> dict | None:
    """Find the nearest radar station to the given coordinates.

    Uses simple Euclidean distance on lat/lon, which is adequate for
    nearest-station lookup within the US.
    """
    if stations is None:
        stations = get_stations()
    if not stations:
        return None

    def _dist(s: dict) -> float:
        return math.hypot(s["lat"] - lat, s["lon"] - lon)

    return min(stations, key=_dist)


def search_stations(
    query: str, stations: list[dict] | None = None
) -> list[dict]:
    """Search stations by ICAO, name, or state (case-insensitive partial match)."""
    if stations is None:
        stations = get_stations()

    q = query.lower()
    return [
        s
        for s in stations
        if q in s["icao"].lower()
        or q in s["name"].lower()
        or q in s["state"].lower()
    ]
