import pytest

from utils.units import (
    c_to_f,
    f_to_c,
    mps_to_mph,
    kmh_to_mph,
    mm_to_inches,
    hpa_to_inhg,
    m_to_ft,
    deg_to_cardinal,
)


def test_c_to_f_freezing() -> None:
    assert c_to_f(0) == 32.0


def test_c_to_f_boiling() -> None:
    assert c_to_f(100) == 212.0


def test_f_to_c_freezing() -> None:
    assert f_to_c(32) == pytest.approx(0.0)


def test_mps_to_mph() -> None:
    assert mps_to_mph(1.0) == pytest.approx(2.23694)


def test_kmh_to_mph() -> None:
    assert kmh_to_mph(100.0) == pytest.approx(62.1371)


def test_mm_to_inches() -> None:
    assert mm_to_inches(25.4) == pytest.approx(1.0, rel=1e-3)


def test_hpa_to_inhg() -> None:
    assert hpa_to_inhg(1013.25) == pytest.approx(29.92, rel=1e-2)


def test_m_to_ft() -> None:
    assert m_to_ft(1.0) == pytest.approx(3.28084)


def test_deg_to_cardinal_north() -> None:
    assert deg_to_cardinal(0) == "N"


def test_deg_to_cardinal_east() -> None:
    assert deg_to_cardinal(90) == "E"


def test_deg_to_cardinal_south() -> None:
    assert deg_to_cardinal(180) == "S"


def test_deg_to_cardinal_west() -> None:
    assert deg_to_cardinal(270) == "W"
