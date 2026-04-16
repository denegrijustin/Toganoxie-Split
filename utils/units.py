"""Unit conversion utilities for the Toganoxie Split weather app."""

_CARDINALS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]


def c_to_f(value_c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (value_c * 9.0 / 5.0) + 32.0


def f_to_c(value_f: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (value_f - 32.0) * 5.0 / 9.0


def mps_to_mph(value_mps: float) -> float:
    """Convert meters/sec to miles/hour."""
    return value_mps * 2.23694


def kmh_to_mph(value_kmh: float) -> float:
    """Convert km/h to mph."""
    return value_kmh * 0.621371


def mm_to_inches(value_mm: float) -> float:
    """Convert millimeters to inches."""
    return value_mm * 0.0393701


def hpa_to_inhg(value_hpa: float) -> float:
    """Convert hectopascals to inches of mercury."""
    return value_hpa * 0.02953


def m_to_ft(value_m: float) -> float:
    """Convert meters to feet."""
    return value_m * 3.28084


def deg_to_cardinal(degrees: float) -> str:
    """Convert wind direction degrees to cardinal direction (N, NNE, NE, etc)."""
    idx = round(degrees % 360 / 22.5) % 16
    return _CARDINALS[idx]
