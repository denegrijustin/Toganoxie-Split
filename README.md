# toganoxie-split

U.S.-only weather intelligence app built with Python 3.11 + Streamlit.

Provides a RadarOmega-inspired (non-branded) weather workflow with live radar overlays, model comparison, point forecasts, NWS alerts, and radar station tools — all backed by validated public APIs.

## Features

### 🛰️ Radar Tab
- Live radar map using folium with NOAA/NCEP WMS overlays
- Three radar products: Composite Reflectivity, Base Reflectivity, Base Velocity
- NEXRAD station pins with clickable metadata
- Overlay opacity slider and layer toggle
- Click-to-select point with nearest station lookup
- Source timestamp and health indicator

### 📊 Models Tab
- **Open-Meteo mode**: Compare up to 10 validated models (GFS, HRRR, ECMWF, GEM, ICON, MeteoFrance, JMA, NBM, GEFS, etc.)
- Interactive Plotly charts for any hourly variable
- Plain-English variable labels in Simple mode, raw names in Advanced mode
- Data table export
- Model validation status display
- **NOMADS mode**: Browse GFS, HRRR, RAP, NAM, NBM model metadata
- Subset URL generation for GRIB filter access
- Variable and level selectors
- Latest run estimation

### 🌤️ Point Forecast Tab
- NWS extended forecast with detailed periods
- NWS hourly forecast table and temperature chart
- Open-Meteo current conditions with metric cards
- Open-Meteo daily summary table
- Open-Meteo hourly temperature chart
- Raw JSON view in Advanced mode

### ⚠️ Alerts Tab
- Active NWS alerts by state or point
- Severity color coding (Extreme, Severe, Moderate, Minor)
- Alert details with headline, description, effective/expiration times
- Instructions display in Advanced mode
- Clean empty-state when no alerts exist
- Fetch timestamp display

### 📡 Stations Tab
- Full NEXRAD station database (150+ stations)
- Searchable by ICAO, name, or state
- Interactive station map with clickable markers
- Nearest station utility with distance
- Station metadata: ICAO, name, state, coordinates, elevation, type
- Fallback to hardcoded list if primary source fails

## Data Sources

| Source | Usage | Status |
|--------|-------|--------|
| [NWS API](https://api.weather.gov) | Point forecasts, hourly forecasts, alerts | ✅ Live |
| [Open-Meteo](https://open-meteo.com/en/docs) | Model comparison, current/hourly/daily data | ✅ Live |
| [NOAA NOMADS](https://nomads.ncep.noaa.gov) | Model metadata, subset URL generation | ✅ Metadata |
| [NOAA/NCEP Radar](https://opengeo.ncep.noaa.gov/geoserver/) | WMS radar overlay tiles | ✅ Live |
| [NCEI NEXRAD Stations](https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt) | Radar station metadata | ✅ Live |

## Validated Models

### Open-Meteo (live data via API)
- `gfs_seamless` – GFS Seamless
- `gfs_global` – GFS Global
- `hrrr_conus` – HRRR CONUS
- `ecmwf_ifs025` – ECMWF IFS 0.25°
- `gem_seamless` – GEM Seamless
- `icon_seamless` – ICON Seamless
- `meteofrance_seamless` – Météo-France Seamless
- `jma_seamless` – JMA Seamless
- `ncep_nbm_conus` – NBM CONUS
- `ncep_gefs025` – GEFS 0.25°

Models are validated at runtime; only models that return data are shown in the UI.

### NOMADS (metadata + subset URLs)
- GFS (Global Forecast System)
- HRRR (High-Res Rapid Refresh)
- RAP (Rapid Refresh)
- NAM (North American Mesoscale)
- NBM (National Blend of Models)

NOMADS endpoints are checked for reachability; unavailable models are hidden.

## Setup

1. Create and activate a Python 3.11+ environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
streamlit run app.py
```

## Tests

```bash
pytest
```

All tests run offline with mocked HTTP calls. No network access required.

## Architecture

```
app.py                    # Streamlit UI – 5 tabs with live data rendering
services/
  nws_api.py              # NWS API adapter (point, forecast, alerts)
  open_meteo.py           # Open-Meteo adapter (forecast, model comparison)
  nomads.py               # NOMADS model registry and URL builder
  radar.py                # Radar WMS overlay adapter
  stations.py             # NEXRAD station metadata adapter
utils/
  geospatial.py           # Location lookup, distance, state codes
  labels.py               # Variable labels and formatting
  units.py                # Unit conversions (°C→°F, m/s→mph, etc.)
tests/                    # 71 tests covering all modules
```

## Simple vs Advanced Mode

- **Simple mode**: Plain-English labels, common variables, clean charts
- **Advanced mode**: Raw variable names, model run times, raw API responses, full variable/level selectors

## Caching

All API responses are cached using `@st.cache_data` with appropriate TTLs:
- Point metadata: 10 minutes
- Forecasts: 15 minutes
- Alerts: 5 minutes
- Model validation: 30 minutes
- Radar layers: 5 minutes
- Radar timestamps: 2 minutes
- Station data: 24 hours
- NOMADS availability: 15 minutes

## Known Limitations

- Location lookup uses a built-in dictionary of ~25 US cities; arbitrary city names are not geocoded
- NOMADS integration provides metadata and subset URL generation; full GRIB2 download/parse requires `eccodes` runtime support
- Radar WMS overlays depend on NOAA/NCEP GeoServer availability
- Station list parsing from NCEI file uses fixed-width column positions; format changes may require parser updates
- Map click handling requires page rerun in Streamlit

## CI

GitHub Actions workflow runs on push to `main` and on pull requests:
- Import smoke checks for all modules
- Full pytest suite (71 tests)

## Deployment Notes

- CI workflow runs on push to `main` and on pull requests
- Production deployment should only use code merged through validated PRs
