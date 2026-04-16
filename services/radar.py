"""Radar overlay adapter – provides NOAA/NCEP WMS tile URLs for map overlays."""

import xml.etree.ElementTree as ET

import requests
import streamlit as st

BASE_URL = "https://opengeo.ncep.noaa.gov/geoserver"
HEADERS = {"User-Agent": "toganoxie-split/2.0 (weather-app)"}
TIMEOUT = 10  # seconds

RADAR_LAYERS = {
    "composite_reflectivity": {
        "name": "Composite Reflectivity",
        "layer": "conus_cref_qcd",
        "workspace": "conus",
        "description": "Composite reflectivity mosaic (dBZ)",
    },
    "base_reflectivity": {
        "name": "Base Reflectivity",
        "layer": "conus_bref_qcd",
        "workspace": "conus",
        "description": "Base reflectivity mosaic (dBZ)",
    },
    "base_velocity": {
        "name": "Base Velocity",
        "layer": "conus_bvel_qcd",
        "workspace": "conus",
        "description": "Base velocity mosaic (kts)",
    },
}


def _build_wms_base(workspace: str, layer: str) -> str:
    """Return the OWS endpoint for a given workspace/layer."""
    return f"{BASE_URL}/{workspace}/{layer}/ows"


def _build_getmap_url(workspace: str, layer: str, bbox: str = "{bbox}",
                      width: int = 256, height: int = 256) -> str:
    """Return a WMS GetMap URL (with placeholder bbox by default)."""
    base = _build_wms_base(workspace, layer)
    return (
        f"{base}?service=WMS&version=1.1.1&request=GetMap"
        f"&layers={layer}&bbox={bbox}"
        f"&width={width}&height={height}"
        f"&srs=EPSG:4326&styles=&format=image/png&transparent=true"
    )


def _get_layer_config(layer_id: str) -> dict:
    """Look up a layer config by id, raising ValueError for unknown ids."""
    cfg = RADAR_LAYERS.get(layer_id)
    if cfg is None:
        raise ValueError(
            f"Unknown radar layer '{layer_id}'. "
            f"Valid ids: {', '.join(RADAR_LAYERS)}"
        )
    return cfg


@st.cache_data(ttl=300)
def list_supported_layers() -> list[dict]:
    """Return list of supported radar overlay layer configs.

    Each dict contains: id, name, layer, workspace, description, wms_url.
    """
    results: list[dict] = []
    for layer_id, cfg in RADAR_LAYERS.items():
        results.append({
            "id": layer_id,
            "name": cfg["name"],
            "layer": cfg["layer"],
            "workspace": cfg["workspace"],
            "description": cfg["description"],
            "wms_url": _build_getmap_url(cfg["workspace"], cfg["layer"]),
        })
    return results


def get_wms_tile_url(layer_id: str = "composite_reflectivity") -> str:
    """Return WMS GetMap URL template for the given layer.

    The returned URL contains a ``{bbox}`` placeholder suitable for use
    as a tile-layer overlay in folium or pydeck.
    """
    cfg = _get_layer_config(layer_id)
    return _build_getmap_url(cfg["workspace"], cfg["layer"])


@st.cache_data(ttl=120)
def get_layer_timestamp(layer_id: str = "composite_reflectivity") -> str | None:
    """Try to get the current timestamp/freshness of the radar layer.

    Issues a WMS GetCapabilities request and parses the time dimension
    for the requested layer.  Returns an ISO timestamp string for the
    most recent time value, or ``None`` if unavailable.
    """
    cfg = _get_layer_config(layer_id)
    caps_url = (
        f"{_build_wms_base(cfg['workspace'], cfg['layer'])}"
        f"?service=WMS&version=1.1.1&request=GetCapabilities"
    )
    try:
        resp = requests.get(caps_url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return None

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        return None

    # Search all Extent/Dimension elements for a time value.
    # WMS 1.1.1 uses <Extent name="time">, WMS 1.3.0 uses <Dimension name="time">.
    for elem in root.iter():
        tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag_local in ("Extent", "Dimension"):
            attr_name = elem.attrib.get("name", "").lower()
            if attr_name == "time" and elem.text:
                # Time values may be comma-separated or a range (start/end/period).
                # Return the last (most recent) value.
                time_text = elem.text.strip()
                if "," in time_text:
                    return time_text.rsplit(",", 1)[-1].strip()
                if "/" in time_text:
                    parts = time_text.split("/")
                    # For range notation the second element is the end time.
                    return parts[1].strip() if len(parts) >= 2 else parts[0].strip()
                return time_text
    return None


@st.cache_data(ttl=300)
def validate_layer(layer_id: str = "composite_reflectivity") -> bool:
    """Check if the radar layer endpoint is responding.

    Makes a small 1×1 pixel GetMap request and returns ``True`` if the
    server responds with an image content type, ``False`` otherwise.
    """
    cfg = _get_layer_config(layer_id)
    test_url = _build_getmap_url(
        cfg["workspace"], cfg["layer"],
        bbox="-100,38,-99,39", width=1, height=1,
    )
    try:
        resp = requests.get(test_url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        return "image" in content_type
    except requests.RequestException:
        return False
