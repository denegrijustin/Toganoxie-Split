"""Geospatial utilities for the Toganoxie Split weather app."""

import math

EARTH_RADIUS_MILES = 3958.8

US_CITIES: dict[str, tuple[float, float]] = {
    "new york, ny": (40.7128, -74.0060),
    "los angeles, ca": (34.0522, -118.2437),
    "chicago, il": (41.8781, -87.6298),
    "houston, tx": (29.7604, -95.3698),
    "phoenix, az": (33.4484, -112.0740),
    "dallas, tx": (32.7767, -96.7970),
    "denver, co": (39.7392, -104.9903),
    "kansas city, mo": (39.0997, -94.5786),
    "toganoxie, ks": (39.1078, -95.1194),
    "topeka, ks": (39.0473, -95.6752),
    "wichita, ks": (37.6872, -97.3301),
    "oklahoma city, ok": (35.4676, -97.5164),
    "miami, fl": (25.7617, -80.1918),
    "seattle, wa": (47.6062, -122.3321),
    "atlanta, ga": (33.7490, -84.3880),
    "minneapolis, mn": (44.9778, -93.2650),
    "st louis, mo": (38.6270, -90.1994),
    "des moines, ia": (41.5868, -93.6250),
    "omaha, ne": (41.2565, -95.9345),
    "memphis, tn": (35.1495, -90.0490),
    "nashville, tn": (36.1627, -86.7816),
    "charlotte, nc": (35.2271, -80.8431),
    "boston, ma": (42.3601, -71.0589),
    "detroit, mi": (42.3314, -83.0458),
    "san francisco, ca": (37.7749, -122.4194),
    "washington, dc": (38.9072, -77.0369),
}

US_STATES: dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}

_STATE_NAME_TO_CODE: dict[str, str] = {
    name.lower(): code for code, name in US_STATES.items()
}


def city_state_to_lat_lon(query: str) -> tuple[float, float]:
    """Resolve city/state query to lat/lon.

    Checks US_CITIES dict (case-insensitive).
    Raises ValueError if the query is not found.
    """
    key = query.strip().lower()
    if key in US_CITIES:
        return US_CITIES[key]
    raise ValueError(f"Unknown location: {query!r}")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in miles between two points."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_MILES * c


def state_code_to_name(code: str) -> str:
    """Convert 2-letter state code to full name. Raises ValueError if unknown."""
    key = code.strip().upper()
    if key in US_STATES:
        return US_STATES[key]
    raise ValueError(f"Unknown state code: {code!r}")


def state_name_to_code(name: str) -> str:
    """Convert state name to 2-letter code. Raises ValueError if unknown."""
    key = name.strip().lower()
    if key in _STATE_NAME_TO_CODE:
        return _STATE_NAME_TO_CODE[key]
    raise ValueError(f"Unknown state name: {name!r}")
