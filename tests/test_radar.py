import pytest

import services.radar as radar


def test_radar_module_imports() -> None:
    assert radar is not None


def test_radar_layers_has_expected_keys() -> None:
    for key in ("composite_reflectivity", "base_reflectivity", "base_velocity"):
        assert key in radar.RADAR_LAYERS


def test_list_supported_layers_returns_list_of_dicts() -> None:
    layers = radar.list_supported_layers()
    assert isinstance(layers, list)
    assert len(layers) > 0
    for layer in layers:
        assert "id" in layer
        assert "name" in layer
        assert "wms_url" in layer
        assert "workspace" in layer


def test_get_wms_tile_url_contains_expected_parts() -> None:
    url = radar.get_wms_tile_url("composite_reflectivity")
    assert "opengeo.ncep.noaa.gov" in url
    assert "GetMap" in url
    assert "conus_cref_qcd" in url
    assert "{bbox}" in url


def test_get_wms_tile_url_unknown_layer_raises() -> None:
    with pytest.raises(ValueError, match="Unknown radar layer"):
        radar.get_wms_tile_url("nonexistent_layer")
