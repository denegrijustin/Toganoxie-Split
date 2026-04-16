from utils.labels import (
    VARIABLE_LABELS,
    VARIABLE_UNITS,
    label_for_variable,
    unit_for_variable,
    format_value,
)


def test_label_for_variable_simple_mode() -> None:
    assert label_for_variable("wind_speed") == "Wind Speed"


def test_label_for_variable_known_key() -> None:
    assert label_for_variable("temperature_2m") == "Temperature"


def test_label_for_variable_advanced_mode() -> None:
    assert label_for_variable("temperature_2m", advanced=True) == "temperature_2m"


def test_unit_for_variable_known() -> None:
    assert unit_for_variable("temperature_2m") == "°F"


def test_unit_for_variable_unknown() -> None:
    assert unit_for_variable("unknown_var") == ""


def test_format_value_with_unit() -> None:
    assert format_value("temperature_2m", 72.0) == "72.0°F"


def test_format_value_none() -> None:
    assert format_value("temperature_2m", None) == "N/A"


def test_format_value_no_unit() -> None:
    result = format_value("unknown_var", 42.0)
    assert result == "42.0"


def test_variable_labels_has_expected_entries() -> None:
    assert "temperature_2m" in VARIABLE_LABELS
    assert "wind_speed_10m" in VARIABLE_LABELS
    assert "cape" in VARIABLE_LABELS


def test_variable_units_has_expected_entries() -> None:
    assert "wind_speed_10m" in VARIABLE_UNITS
    assert VARIABLE_UNITS["wind_speed_10m"] == "mph"
