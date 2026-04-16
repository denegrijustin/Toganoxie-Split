import app


def test_app_imports() -> None:
    assert app is not None


def test_folium_import() -> None:
    import folium
    assert folium is not None


def test_streamlit_folium_import() -> None:
    import streamlit_folium
    assert streamlit_folium is not None
