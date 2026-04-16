import pytest

from utils.geospatial import (
    US_CITIES,
    US_STATES,
    city_state_to_lat_lon,
    haversine_distance,
    state_code_to_name,
    state_name_to_code,
)


def test_geospatial_module_imports() -> None:
    assert US_CITIES is not None
    assert US_STATES is not None


def test_city_state_to_lat_lon_known() -> None:
    lat, lon = city_state_to_lat_lon("Toganoxie, KS")
    assert lat == pytest.approx(39.1078)
    assert lon == pytest.approx(-95.1194)


def test_city_state_to_lat_lon_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown location"):
        city_state_to_lat_lon("Fake City, ZZ")


def test_haversine_distance_positive() -> None:
    dist = haversine_distance(39.1, -95.1, 40.0, -94.0)
    assert dist > 0


def test_haversine_distance_same_point() -> None:
    dist = haversine_distance(39.1, -95.1, 39.1, -95.1)
    assert dist == pytest.approx(0.0)


def test_state_code_to_name() -> None:
    assert state_code_to_name("KS") == "Kansas"


def test_state_code_to_name_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown state code"):
        state_code_to_name("ZZ")


def test_state_name_to_code() -> None:
    assert state_name_to_code("Kansas") == "KS"


def test_state_name_to_code_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown state name"):
        state_name_to_code("Atlantis")
