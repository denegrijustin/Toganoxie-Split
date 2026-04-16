from utils.units import c_to_f


def test_c_to_f() -> None:
    assert c_to_f(0) == 32.0
