# toganoxie-split

U.S.-only weather intelligence app bootstrap in Python 3.11 + Streamlit.

## Project purpose
Provide a reliable base for a RadarOmega-inspired (non-branded) weather workflow app with radar, model comparison, point forecast inspection, station tools, and alerts.

## Supported data sources (planned adapters)
- NWS API (`api.weather.gov`)
- Open-Meteo Forecast API
- NOAA NOMADS GRIB subset endpoints
- NOAA/NCEP radar and overlay endpoints
- NOAA radar station metadata services

> This bootstrap does **not** claim full source integration yet.

## Setup instructions
1. Create and activate a Python 3.11 environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run instructions
```bash
streamlit run app.py
```

## Deployment notes
- CI workflow runs on push to `main` and on pull requests.
- Production deployment should only use code merged through validated PRs.

## Current limitations
- Service adapters are scaffolded and intentionally minimal.
- External source calls are not fully implemented in bootstrap.
- UI is a startup shell for branch-based feature expansion.

## Architecture summary
- `app.py`: Streamlit shell and mode controls
- `services/`: source-specific adapters (NWS/Open-Meteo/NOMADS/Radar/Stations)
- `utils/`: geospatial, units, and label helpers
- `tests/`: import/startup and module smoke coverage

## Future enhancements
Follow the merge order:
1. `feature/product-architecture`
2. `feature/nws-api`
3. `feature/open-meteo`
4. `feature/radar-stations`
5. `feature/radar-services`
6. `feature/geospatial-utils`
7. `feature/units-labels`
8. `feature/nomads-models`
9. `feature/ui-streamlit`
10. `feature/performance-caching`
11. `feature/tests-qa`
12. `feature/documentation`
