import re

import pytest

import services.nomads as nomads


def test_nomads_module_imports() -> None:
    assert nomads is not None


def test_nomads_models_has_expected_keys() -> None:
    for key in ("gfs", "hrrr", "rap", "nam", "nbm"):
        assert key in nomads.NOMADS_MODELS


def test_get_available_models_returns_dict() -> None:
    result = nomads.get_available_models()
    assert isinstance(result, dict)
    assert "gfs" in result


def test_build_subset_url_contains_expected_parts() -> None:
    url = nomads.build_subset_url("gfs", "20240101/06", 3)
    assert "filter_gfs_0p25.pl" in url
    assert "var_TMP=on" in url
    assert "lev_2_m_above_ground=on" in url
    assert "file=" in url


def test_build_subset_url_with_lat_lon_adds_subregion() -> None:
    url = nomads.build_subset_url("gfs", "20240101/06", 3, lat=39.0, lon=-95.0)
    assert "subregion" in url
    assert "toplat=40" in url
    assert "bottomlat=38" in url


def test_build_subset_url_unknown_model_raises() -> None:
    with pytest.raises(ValueError, match="Unknown NOMADS model"):
        nomads.build_subset_url("fake_model", "20240101/06", 3)


def test_get_latest_run_returns_valid() -> None:
    date_str, run_hour = nomads.get_latest_run("gfs")
    assert re.match(r"\d{8}", date_str)
    assert isinstance(run_hour, int)
    assert run_hour in nomads.NOMADS_MODELS["gfs"]["run_hours"]


def test_nomads_variable_labels_has_entries() -> None:
    assert "TMP" in nomads.NOMADS_VARIABLE_LABELS
    assert "CAPE" in nomads.NOMADS_VARIABLE_LABELS
    assert nomads.NOMADS_VARIABLE_LABELS["TMP"] == "Temperature"


def test_nomads_level_labels_has_entries() -> None:
    assert "surface" in nomads.NOMADS_LEVEL_LABELS
    assert "2_m_above_ground" in nomads.NOMADS_LEVEL_LABELS
