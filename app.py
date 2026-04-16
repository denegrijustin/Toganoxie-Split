"""Toganoxie-Split – U.S. weather intelligence app (v2).

Presents live data across five tabs: Radar, Models, Point Forecast,
Alerts, and Stations.  All data comes from validated public sources
(NWS, Open-Meteo, NOMADS metadata, NOAA radar services, NEXRAD
station files).
"""

from __future__ import annotations

import datetime

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from services import nws_api, open_meteo, nomads, radar, stations
from utils.geospatial import (
    US_CITIES,
    US_STATES,
    city_state_to_lat_lon,
    haversine_distance,
)
from utils.labels import (
    VARIABLE_LABELS,
    label_for_variable,
    unit_for_variable,
    format_value,
)

# ── Defaults ──────────────────────────────────────────────────────────
DEFAULT_LAT, DEFAULT_LON = 39.1078, -95.1194  # Toganoxie, KS
DEFAULT_ZOOM = 5

# ── Page config ───────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(page_title="Toganoxie-Split Weather", layout="wide")
    st.title("🌩️ Toganoxie-Split Weather Intelligence")

    # ── Sidebar ───────────────────────────────────────────────────────
    advanced = st.sidebar.radio("Mode", ["Simple", "Advanced"], index=0) == "Advanced"
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Location")
    loc_method = st.sidebar.radio(
        "Set location by", ["City lookup", "Coordinates"], index=0
    )
    if loc_method == "City lookup":
        city_options = sorted(US_CITIES.keys())
        default_idx = city_options.index("toganoxie, ks") if "toganoxie, ks" in city_options else 0
        city_choice = st.sidebar.selectbox("City", city_options, index=default_idx)
        try:
            sel_lat, sel_lon = city_state_to_lat_lon(city_choice)
        except ValueError:
            sel_lat, sel_lon = DEFAULT_LAT, DEFAULT_LON
    else:
        sel_lat = st.sidebar.number_input("Latitude", value=DEFAULT_LAT, format="%.4f")
        sel_lon = st.sidebar.number_input("Longitude", value=DEFAULT_LON, format="%.4f")

    st.sidebar.caption(f"Selected: {sel_lat:.4f}, {sel_lon:.4f}")

    # Store in session state for cross-tab usage
    st.session_state["sel_lat"] = sel_lat
    st.session_state["sel_lon"] = sel_lon
    st.session_state["advanced"] = advanced

    # ── Tabs ──────────────────────────────────────────────────────────
    tab_radar, tab_models, tab_forecast, tab_alerts, tab_stations = st.tabs(
        ["🛰️ Radar", "📊 Models", "🌤️ Point Forecast", "⚠️ Alerts", "📡 Stations"]
    )

    with tab_radar:
        _render_radar_tab(sel_lat, sel_lon, advanced)

    with tab_models:
        _render_models_tab(sel_lat, sel_lon, advanced)

    with tab_forecast:
        _render_forecast_tab(sel_lat, sel_lon, advanced)

    with tab_alerts:
        _render_alerts_tab(sel_lat, sel_lon, advanced)

    with tab_stations:
        _render_stations_tab(sel_lat, sel_lon, advanced)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Radar tab
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_radar_tab(lat: float, lon: float, advanced: bool) -> None:
    st.subheader("Live Radar Map")

    # ── Layer controls ────────────────────────────────────────────────
    layers = radar.list_supported_layers()
    layer_names = {ly["id"]: ly["name"] for ly in layers}
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
    with col_ctrl1:
        sel_layer = st.selectbox(
            "Radar layer",
            list(layer_names.keys()),
            format_func=lambda k: layer_names[k],
        )
    with col_ctrl2:
        opacity = st.slider("Overlay opacity", 0.0, 1.0, 0.6, 0.05)
    with col_ctrl3:
        show_stations = st.checkbox("Show station pins", value=True)

    # ── Timestamp & status ────────────────────────────────────────────
    ts = radar.get_layer_timestamp(sel_layer)
    layer_ok = radar.validate_layer(sel_layer)
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if layer_ok:
            st.success(f"✅ Radar source active")
        else:
            st.warning("⚠️ Radar source may be unavailable")
    with status_col2:
        if ts:
            st.info(f"🕐 Layer time: {ts}")
        else:
            st.info("🕐 Timestamp not available")

    # ── Build map ─────────────────────────────────────────────────────
    m = folium.Map(location=[lat, lon], zoom_start=DEFAULT_ZOOM, tiles="CartoDB positron")

    # Radar WMS overlay
    if layer_ok:
        wms_url = radar.get_wms_tile_url(sel_layer)
        layer_cfg = radar.RADAR_LAYERS.get(sel_layer, {})
        folium.raster_layers.WmsTileLayer(
            url=f"https://opengeo.ncep.noaa.gov/geoserver/{layer_cfg.get('workspace', 'conus')}/ows?",
            layers=layer_cfg.get("layer", "conus_cref_qcd"),
            fmt="image/png",
            transparent=True,
            name=layer_names.get(sel_layer, "Radar"),
            opacity=opacity,
            overlay=True,
            control=True,
        ).add_to(m)

    # Station pins
    all_stations = stations.get_stations()
    if show_stations and all_stations:
        for s in all_stations:
            folium.CircleMarker(
                location=[s["lat"], s["lon"]],
                radius=3,
                color="#1f77b4",
                fill=True,
                fill_opacity=0.7,
                popup=f"{s['icao']} – {s['name']}, {s['state']}",
                tooltip=s["icao"],
            ).add_to(m)

    # Selected point marker
    folium.Marker(
        location=[lat, lon],
        popup=f"Selected: {lat:.4f}, {lon:.4f}",
        tooltip="Selected point",
        icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
    ).add_to(m)

    folium.LayerControl().add_to(m)
    map_data = st_folium(m, width=900, height=500, returned_objects=["last_clicked"])

    # ── Click handling ────────────────────────────────────────────────
    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lon = map_data["last_clicked"]["lng"]
        st.session_state["sel_lat"] = click_lat
        st.session_state["sel_lon"] = click_lon
        st.info(f"📍 Clicked point: {click_lat:.4f}, {click_lon:.4f}")

        nearest = stations.find_nearest_station(click_lat, click_lon, all_stations)
        if nearest:
            dist = haversine_distance(click_lat, click_lon, nearest["lat"], nearest["lon"])
            st.success(
                f"Nearest radar: **{nearest['icao']}** – {nearest['name']}, "
                f"{nearest['state']} ({dist:.1f} mi)"
            )

    # ── Selected point info ───────────────────────────────────────────
    nearest = stations.find_nearest_station(lat, lon, all_stations)
    if nearest:
        dist = haversine_distance(lat, lon, nearest["lat"], nearest["lon"])
        st.markdown(
            f"**Nearest radar station:** {nearest['icao']} – {nearest['name']}, "
            f"{nearest['state']} ({dist:.1f} mi away)"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Models tab
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_models_tab(lat: float, lon: float, advanced: bool) -> None:
    st.subheader("Model Comparison")

    # ── Model source selector ─────────────────────────────────────────
    source = st.radio("Model source", ["Open-Meteo", "NOMADS (metadata)"], index=0)

    if source == "Open-Meteo":
        _render_open_meteo_models(lat, lon, advanced)
    else:
        _render_nomads_models(lat, lon, advanced)


def _render_open_meteo_models(lat: float, lon: float, advanced: bool) -> None:
    """Open-Meteo model comparison with live charts."""

    # Validate models
    with st.spinner("Validating available models…"):
        valid_models = open_meteo.get_validated_models(lat, lon)

    if not valid_models:
        st.error("No Open-Meteo models returned data for this location.")
        return

    st.success(f"✅ {len(valid_models)} validated models available")

    # ── Controls ──────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        selected_models = st.multiselect(
            "Models to compare",
            valid_models,
            default=valid_models[:3],
        )
    with col2:
        if advanced:
            var_options = open_meteo.HOURLY_VARIABLES
        else:
            var_options = [
                "temperature_2m", "apparent_temperature", "dew_point_2m",
                "relative_humidity_2m", "wind_speed_10m", "wind_gusts_10m",
                "precipitation", "precipitation_probability", "cloud_cover",
                "cape",
            ]
        sel_var = st.selectbox(
            "Variable",
            var_options,
            format_func=lambda v: label_for_variable(v, advanced),
        )

    if not selected_models:
        st.warning("Select at least one model to compare.")
        return

    # ── Fetch comparison data ─────────────────────────────────────────
    with st.spinner("Fetching model data…"):
        comparison = open_meteo.get_model_comparison(
            lat, lon, models=selected_models, variables=[sel_var]
        )

    if not comparison:
        st.error("No model data returned.")
        return

    # ── Chart ─────────────────────────────────────────────────────────
    fig = go.Figure()
    label = label_for_variable(sel_var, advanced)
    unit = unit_for_variable(sel_var)

    for model_name, data in comparison.items():
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        values = hourly.get(sel_var, [])
        if times and values:
            display_name = model_name if advanced else model_name.replace("_", " ").title()
            fig.add_trace(go.Scatter(
                x=times, y=values, mode="lines", name=display_name,
            ))

    fig.update_layout(
        title=f"{label} Comparison at {lat:.2f}, {lon:.2f}",
        xaxis_title="Time",
        yaxis_title=f"{label} ({unit})" if unit else label,
        height=450,
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Value table ───────────────────────────────────────────────────
    if st.checkbox("Show data table", value=False, key="model_table"):
        table_data: dict[str, list] = {}
        max_len = 0
        times_list: list[str] = []
        for model_name, data in comparison.items():
            hourly = data.get("hourly", {})
            vals = hourly.get(sel_var, [])
            t = hourly.get("time", [])
            table_data[model_name] = vals
            if len(t) > max_len:
                max_len = len(t)
                times_list = t
        if times_list:
            df = pd.DataFrame(table_data, index=times_list[:max_len])
            df.index.name = "Time"
            st.dataframe(df.head(48), use_container_width=True)

    # ── Model status ──────────────────────────────────────────────────
    if advanced:
        with st.expander("Model validation status"):
            for m in open_meteo.AVAILABLE_MODELS:
                status = "✅" if m in valid_models else "❌"
                st.text(f"{status} {m}")


def _render_nomads_models(lat: float, lon: float, advanced: bool) -> None:
    """NOMADS model metadata and subset URL generation."""

    all_models = nomads.get_available_models()

    with st.spinner("Checking NOMADS availability…"):
        valid_ids = nomads.get_validated_models()

    if not valid_ids:
        st.warning("No NOMADS endpoints are currently reachable.")
        st.info("NOMADS servers may be temporarily unavailable. Try again later.")
        return

    st.success(f"✅ {len(valid_ids)} NOMADS model endpoints reachable")

    # ── Controls ──────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        sel_model = st.selectbox(
            "NOMADS Model",
            valid_ids,
            format_func=lambda mid: all_models[mid]["name"],
        )
    with col2:
        cfg = all_models[sel_model]
        fhr = st.slider(
            "Forecast hour",
            0,
            cfg["max_forecast_hour"],
            0,
            cfg["forecast_hour_step"],
        )

    # Model info
    date_str, run_hour = nomads.get_latest_run(sel_model)
    st.info(f"Latest estimated run: **{date_str} {run_hour:02d}Z**")

    if advanced:
        sel_vars = st.multiselect("Variables", cfg["variables"], default=cfg["variables"][:3])
        sel_levels = st.multiselect("Levels", cfg["levels"], default=cfg["levels"][:2])
    else:
        sel_vars = cfg["variables"][:3]
        sel_levels = cfg["levels"][:2]
        var_labels = [nomads.NOMADS_VARIABLE_LABELS.get(v, v) for v in sel_vars]
        lev_labels = [nomads.NOMADS_LEVEL_LABELS.get(l, l) for l in sel_levels]
        st.caption(f"Variables: {', '.join(var_labels)} | Levels: {', '.join(lev_labels)}")

    # ── Generate URL ──────────────────────────────────────────────────
    run_str = f"{date_str}/{run_hour:02d}"
    try:
        url = nomads.build_subset_url(
            sel_model, run_str, fhr,
            variables=sel_vars, levels=sel_levels,
            lat=lat, lon=lon,
        )
        st.markdown("**Subset URL:**")
        st.code(url, language="text")
    except ValueError as e:
        st.error(str(e))

    # ── Variable reference ────────────────────────────────────────────
    if advanced:
        with st.expander("Variable reference"):
            for var_key, var_label in nomads.NOMADS_VARIABLE_LABELS.items():
                st.text(f"{var_key}: {var_label}")

    # ── Model availability table ──────────────────────────────────────
    with st.expander("NOMADS model status"):
        rows = []
        for mid, mc in all_models.items():
            rows.append({
                "Model": mc["name"],
                "ID": mid,
                "Status": "✅ Available" if mid in valid_ids else "❌ Unreachable",
                "Max Fhr": mc["max_forecast_hour"],
                "Runs": ", ".join(f"{h:02d}Z" for h in mc["run_hours"][:4]),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Point Forecast tab
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_forecast_tab(lat: float, lon: float, advanced: bool) -> None:
    st.subheader("Point Forecast")
    st.caption(f"Location: {lat:.4f}, {lon:.4f}")

    # ── NWS Forecast ──────────────────────────────────────────────────
    st.markdown("### 🏛️ NWS Forecast")

    with st.spinner("Loading NWS data…"):
        meta = nws_api.get_point_metadata(lat, lon)
        forecast_periods = nws_api.get_forecast(lat, lon)
        hourly_periods = nws_api.get_hourly_forecast(lat, lon)

    if meta:
        loc_parts = []
        if meta.get("relativeLocation", {}).get("properties", {}).get("city"):
            city = meta["relativeLocation"]["properties"]["city"]
            state = meta["relativeLocation"]["properties"].get("state", "")
            loc_parts.append(f"{city}, {state}")
        if meta.get("gridId"):
            loc_parts.append(f"Grid: {meta['gridId']}")
        if loc_parts:
            st.info(f"📍 {' | '.join(loc_parts)}")
    else:
        st.warning("Could not resolve NWS point metadata. Location may be outside US coverage.")

    if forecast_periods:
        st.markdown("#### Extended Forecast")
        for p in forecast_periods[:6]:
            name = p.get("name", "")
            detail = p.get("detailedForecast", "")
            temp = p.get("temperature", "")
            temp_unit = p.get("temperatureUnit", "")
            wind_speed = p.get("windSpeed", "")
            wind_dir = p.get("windDirection", "")
            st.markdown(
                f"**{name}**: {temp}°{temp_unit} | Wind {wind_dir} {wind_speed}\n\n"
                f"{detail}"
            )
            st.markdown("---")
    else:
        st.warning("NWS forecast data not available for this location.")

    if hourly_periods:
        st.markdown("#### Hourly Forecast")
        hourly_df_data = []
        for p in hourly_periods[:24]:
            hourly_df_data.append({
                "Time": p.get("startTime", "")[:16],
                "Temp (°F)": p.get("temperature", ""),
                "Wind": f"{p.get('windDirection', '')} {p.get('windSpeed', '')}",
                "Short Forecast": p.get("shortForecast", ""),
            })
        if hourly_df_data:
            st.dataframe(pd.DataFrame(hourly_df_data), use_container_width=True, hide_index=True)

        # Hourly temp chart
        temps = [p.get("temperature") for p in hourly_periods[:24]]
        times = [p.get("startTime", "")[:16] for p in hourly_periods[:24]]
        valid_data = [(t, tmp) for t, tmp in zip(times, temps) if tmp is not None]
        if valid_data:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[d[0] for d in valid_data],
                y=[d[1] for d in valid_data],
                mode="lines+markers",
                name="NWS Hourly Temp",
            ))
            fig.update_layout(
                title="NWS Hourly Temperature",
                xaxis_title="Time",
                yaxis_title="Temperature (°F)",
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Open-Meteo Forecast ───────────────────────────────────────────
    st.markdown("### 🌐 Open-Meteo Forecast")

    with st.spinner("Loading Open-Meteo data…"):
        om_data = open_meteo.get_forecast(lat, lon)

    if not om_data:
        st.warning("Open-Meteo data not available.")
        return

    # Current conditions
    current = om_data.get("current", {})
    if current:
        st.markdown("#### Current Conditions")
        cur_cols = st.columns(4)
        display_vars = [
            ("temperature_2m", "🌡️"),
            ("apparent_temperature", "🌡️"),
            ("wind_speed_10m", "💨"),
            ("relative_humidity_2m", "💧"),
        ]
        for i, (var, icon) in enumerate(display_vars):
            val = current.get(var)
            if val is not None:
                lbl = label_for_variable(var, advanced)
                cur_cols[i % 4].metric(f"{icon} {lbl}", format_value(var, val))

    # Daily forecast
    daily = om_data.get("daily", {})
    if daily and daily.get("time"):
        st.markdown("#### Daily Summary")
        daily_rows = []
        for i, t in enumerate(daily["time"]):
            row: dict[str, object] = {"Date": t}
            for var in open_meteo.DAILY_VARIABLES:
                vals = daily.get(var, [])
                lbl = label_for_variable(var, advanced)
                row[lbl] = vals[i] if i < len(vals) else None
            daily_rows.append(row)
        if daily_rows:
            st.dataframe(pd.DataFrame(daily_rows), use_container_width=True, hide_index=True)

    # Hourly comparison chart
    hourly_om = om_data.get("hourly", {})
    if hourly_om and hourly_om.get("time"):
        st.markdown("#### Open-Meteo Hourly")
        om_times = hourly_om["time"][:48]
        om_temps = hourly_om.get("temperature_2m", [])[:48]
        if om_temps:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=om_times, y=om_temps, mode="lines", name="Open-Meteo Temp",
            ))
            fig.update_layout(
                title="Open-Meteo Hourly Temperature",
                xaxis_title="Time",
                yaxis_title="Temperature (°F)",
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

    if advanced:
        with st.expander("Raw Open-Meteo response"):
            st.json(om_data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Alerts tab
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_alerts_tab(lat: float, lon: float, advanced: bool) -> None:
    st.subheader("Active Weather Alerts")

    col1, col2 = st.columns(2)
    with col1:
        alert_mode = st.radio("Alert scope", ["By State", "By Point"], index=0)
    with col2:
        if alert_mode == "By State":
            state_code = st.selectbox(
                "State",
                sorted(US_STATES.keys()),
                index=sorted(US_STATES.keys()).index("KS") if "KS" in US_STATES else 0,
                format_func=lambda c: f"{c} – {US_STATES[c]}",
            )

    with st.spinner("Fetching alerts…"):
        if alert_mode == "By State":
            alerts = nws_api.get_alerts(state_code)
            source_label = f"State: {state_code}"
        else:
            alerts = nws_api.get_alerts_for_point(lat, lon)
            source_label = f"Point: {lat:.4f}, {lon:.4f}"

    st.caption(f"Source: NWS Alerts API | {source_label}")

    if not alerts:
        st.success("✅ No active alerts for this selection.")
        return

    st.warning(f"⚠️ {len(alerts)} active alert(s)")

    # Severity color mapping
    sev_colors = {
        "Extreme": "🔴", "Severe": "🟠", "Moderate": "🟡", "Minor": "🟢", "Unknown": "⚪",
    }

    for alert in alerts:
        event = alert.get("event", "Unknown Event")
        severity = alert.get("severity", "Unknown")
        icon = sev_colors.get(severity, "⚪")
        headline = alert.get("headline", "")
        effective = alert.get("effective", "")[:19] if alert.get("effective") else "N/A"
        expires = alert.get("expires", "")[:19] if alert.get("expires") else "N/A"
        description = alert.get("description", "")

        with st.expander(f"{icon} {event} ({severity})"):
            st.markdown(f"**{headline}**")
            st.markdown(f"**Effective:** {effective} | **Expires:** {expires}")
            if alert.get("senderName"):
                st.caption(f"Issued by: {alert['senderName']}")
            if description:
                st.text(description[:2000])
            if advanced and alert.get("instruction"):
                st.markdown("**Instructions:**")
                st.text(alert["instruction"][:1000])

    # Source freshness
    st.caption(f"Data fetched at {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stations tab
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_stations_tab(lat: float, lon: float, advanced: bool) -> None:
    st.subheader("NEXRAD Radar Stations")

    with st.spinner("Loading station data…"):
        all_stations = stations.get_stations()

    if not all_stations:
        st.error("Could not load station data.")
        return

    st.success(f"✅ {len(all_stations)} stations loaded")

    # ── Search ────────────────────────────────────────────────────────
    search_query = st.text_input("🔍 Search stations (ICAO, name, or state)")
    if search_query:
        filtered = stations.search_stations(search_query, all_stations)
    else:
        filtered = all_stations

    # ── Nearest station ───────────────────────────────────────────────
    nearest = stations.find_nearest_station(lat, lon, all_stations)
    if nearest:
        dist = haversine_distance(lat, lon, nearest["lat"], nearest["lon"])
        st.info(
            f"📡 Nearest to {lat:.2f}, {lon:.2f}: **{nearest['icao']}** – "
            f"{nearest['name']}, {nearest['state']} ({dist:.1f} miles)"
        )

    # ── Station table ─────────────────────────────────────────────────
    df = pd.DataFrame(filtered)
    if not df.empty:
        display_cols = ["icao", "name", "state", "lat", "lon", "elevation", "type"]
        available_cols = [c for c in display_cols if c in df.columns]
        col_labels = {
            "icao": "ICAO", "name": "Name", "state": "State",
            "lat": "Latitude", "lon": "Longitude",
            "elevation": "Elevation (ft)", "type": "Type",
        }
        display_df = df[available_cols].rename(columns=col_labels)
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400,
        )
    else:
        st.warning("No stations match your search.")

    # ── Station map ───────────────────────────────────────────────────
    st.markdown("#### Station Map")
    stn_map = folium.Map(location=[lat, lon], zoom_start=5, tiles="CartoDB positron")

    for s in filtered[:200]:  # Limit pins for performance
        color = "red" if nearest and s["icao"] == nearest["icao"] else "blue"
        folium.CircleMarker(
            location=[s["lat"], s["lon"]],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=f"<b>{s['icao']}</b><br>{s['name']}, {s['state']}<br>"
                  f"Elev: {s['elevation']} ft<br>Type: {s['type']}",
            tooltip=s["icao"],
        ).add_to(stn_map)

    # Mark selected point
    folium.Marker(
        location=[lat, lon],
        popup="Selected location",
        icon=folium.Icon(color="green", icon="crosshairs", prefix="fa"),
    ).add_to(stn_map)

    st_folium(stn_map, width=900, height=400)

    # ── Source info ───────────────────────────────────────────────────
    if advanced:
        with st.expander("Data source info"):
            st.markdown(
                "**Primary source:** NCEI NEXRAD Stations File\n\n"
                "**URL:** https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt\n\n"
                "**Fallback:** Hardcoded list of 15 major NEXRAD stations\n\n"
                f"**Loaded:** {len(all_stations)} stations"
            )


# ── Entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
