"""Label and unit mapping utilities for weather variables."""

VARIABLE_LABELS: dict[str, str] = {
    "temperature_2m": "Temperature",
    "relative_humidity_2m": "Humidity",
    "dew_point_2m": "Dew Point",
    "apparent_temperature": "Feels Like",
    "precipitation_probability": "Precip Chance",
    "precipitation": "Precipitation",
    "rain": "Rain",
    "snowfall": "Snowfall",
    "cloud_cover": "Cloud Cover",
    "wind_speed_10m": "Wind Speed",
    "wind_direction_10m": "Wind Direction",
    "wind_gusts_10m": "Wind Gusts",
    "surface_pressure": "Pressure",
    "cape": "CAPE",
    "freezing_level_height": "Freezing Level",
    "temperature_2m_max": "High Temp",
    "temperature_2m_min": "Low Temp",
    "precipitation_sum": "Total Precip",
    "precipitation_probability_max": "Max Precip Chance",
    "wind_speed_10m_max": "Max Wind Speed",
    "wind_gusts_10m_max": "Max Wind Gusts",
    # NWS/NOMADS fields
    "tmp": "Temperature",
    "rh": "Humidity",
    "ugrd": "U-Wind Component",
    "vgrd": "V-Wind Component",
    "dpt": "Dew Point",
    "prate": "Precip Rate",
    "refc": "Composite Reflectivity",
    "gust": "Wind Gust",
    "pres": "Pressure",
}

VARIABLE_UNITS: dict[str, str] = {
    "temperature_2m": "°F",
    "relative_humidity_2m": "%",
    "dew_point_2m": "°F",
    "apparent_temperature": "°F",
    "precipitation_probability": "%",
    "precipitation": "in",
    "rain": "in",
    "snowfall": "in",
    "cloud_cover": "%",
    "wind_speed_10m": "mph",
    "wind_direction_10m": "°",
    "wind_gusts_10m": "mph",
    "surface_pressure": "hPa",
    "cape": "J/kg",
    "freezing_level_height": "ft",
}


def label_for_variable(raw_name: str, advanced: bool = False) -> str:
    """Map raw variable names to plain-English labels.

    In advanced mode, return the raw name unchanged.
    In simple mode, use VARIABLE_LABELS lookup, falling back to title-cased name.
    """
    if advanced:
        return raw_name
    return VARIABLE_LABELS.get(raw_name, raw_name.replace("_", " ").title())


def unit_for_variable(raw_name: str) -> str:
    """Return the display unit string for a variable, or empty string if unknown."""
    return VARIABLE_UNITS.get(raw_name, "")


def format_value(raw_name: str, value: float | None) -> str:
    """Format a value with its unit for display. Return 'N/A' for None."""
    if value is None:
        return "N/A"
    unit = unit_for_variable(raw_name)
    if unit:
        return f"{value}{unit}"
    return str(value)
