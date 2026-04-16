import services.open_meteo


def test_open_meteo_module_imports() -> None:
    assert services.open_meteo is not None
