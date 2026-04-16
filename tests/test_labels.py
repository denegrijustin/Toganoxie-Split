from utils.labels import label_for_variable


def test_label_for_variable_simple_mode() -> None:
    assert label_for_variable("wind_speed") == "Wind Speed"
