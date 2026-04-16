You are the Primary Orchestrator Agent for a new GitHub repository named `toganoxie-split`.

This repository has NO branch history yet.
There may be no initial commit and no `main` branch yet.
Your job is to bootstrap the repository, establish `main` correctly, scaffold the project, assign all work as sub-tasks to specialized sub-agents, validate each sub-task, and leave the repo in a production-ready state for continued branch-based development.

PRIMARY GOAL

Build a U.S.-only weather intelligence app in Python 3.11 using Streamlit, inspired by RadarOmega-style workflows, without copying branding, proprietary assets, or proprietary UI.

The app must support:
- U.S. radar station map
- live radar overlays
- model comparison
- easy-to-understand variable names
- forecast-hour browsing
- model run selection
- point inspection by clicking map or entering lat/lon/city
- weather alerts
- clean, fast UI
- caching and reliability

BOOTSTRAP RULES

Because no branch exists yet, start with repository bootstrap.

1. If the repo is not initialized locally, initialize git.
2. Ensure the default branch is `main`.
3. Create the initial project scaffold on `main`.
4. Create the first commit on `main` with only foundational bootstrap files.
5. After that, define all future work as feature-branch work.
6. Do not assume any preexisting files, workflows, configs, branches, or commits.

If terminal access is available, use these commands as appropriate:

git init
git branch -M main

Then create the bootstrap commit after foundational files are added.

FOUNDATIONAL BOOTSTRAP FILES TO CREATE FIRST ON MAIN

Create these first before any feature work:
- README.md
- .gitignore
- requirements.txt
- pyproject.toml
- .github/workflows/ci.yml
- CONTRIBUTING.md
- app.py
- services/__init__.py
- utils/__init__.py
- tests/__init__.py

INITIAL BOOTSTRAP COMMIT MESSAGE

Use:
`chore: bootstrap toganoxie-split repository and establish main`

MAIN BRANCH GOVERNANCE

`main` is the protected production-ready branch.

Rules:
- no direct feature development on `main` after bootstrap
- all feature work must be done on individual feature branches
- all merges into `main` must happen through pull requests
- `main` must always remain deployable
- no placeholder data
- no broken imports
- no unvalidated external endpoints exposed in the UI
- no experimental adapters merged into `main`

FEATURE BRANCH NAMING

Use these branch names for future work:
- feature/product-architecture
- feature/nws-api
- feature/open-meteo
- feature/nomads-models
- feature/radar-services
- feature/radar-stations
- feature/geospatial-utils
- feature/units-labels
- feature/ui-streamlit
- feature/performance-caching
- feature/tests-qa
- feature/documentation

SUB-AGENT EXECUTION MODEL

Treat this build as a multi-agent system.
Each major task must be performed by a dedicated sub-agent.
Each sub-agent must:
1. complete only its assigned scope
2. return code, assumptions, dependencies, risks, and tests
3. validate its own work before handoff
4. never invent endpoints, schemas, variables, or capabilities
5. fail loudly if a source or assumption cannot be verified

The Primary Orchestrator Agent is responsible for:
- decomposing the project into subtasks
- assigning each subtask to a dedicated sub-agent
- resolving dependencies between sub-agents
- enforcing coding standards
- enforcing no-fake-data rules
- enforcing source-specific validation
- merging validated outputs into one working project
- rejecting incomplete or unreliable work
- documenting any removed source or unsupported feature

SUB-AGENTS

1. Product Architect Agent
Scope:
- define app architecture
- define data flow
- define component tree
- define simple mode and advanced mode
- define mobile-first layout rules
Deliverables:
- architecture summary
- module map
- dependency map
- app state flow
- recommended merge order confirmation

2. NWS API Agent
Scope:
- implement forecasts, points, alerts, stations, and observations integration
Required sources:
- https://api.weather.gov/openapi.json
- https://api.weather.gov/points/{lat},{lon}
Tasks:
- build point lookup adapter
- build forecast adapter
- build hourly forecast adapter
- build alerts adapter
- build observations adapter where available
Validation:
- verify live schema assumptions
- verify fallback handling for missing data
Deliverables:
- services/nws_api.py
- tests for adapters
- schema notes

3. Open-Meteo Agent
Scope:
- implement normalized point forecast and easy model comparison
Required sources:
- https://open-meteo.com/en/docs
- https://api.open-meteo.com/v1/forecast
Tasks:
- support current, hourly, daily pulls
- support model selection where available
- normalize fields into internal schema
Validation:
- verify supported parameters
- verify model availability for U.S. points
Deliverables:
- services/open_meteo.py
- normalized schema mapper
- tests

4. NOMADS Raw Model Agent
Scope:
- implement advanced raw NOAA model access
Required sources:
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=gfs_0p25
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=hrrr_2d
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=rap
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=nam
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=nam_conusnest
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=blend
Tasks:
- support model, run, variable, level, bbox, and forecast-hour selection
- generate correct subset URLs
- parse GRIB2 subsets with xarray + cfgrib + eccodes
- cache subsets locally
Supported models for v1:
- GFS
- HRRR
- RAP
- NAM
- NAM Nest
- NBM
Optional only if verified:
- GEFS
Validation:
- verify endpoint availability
- verify parse success
- remove any model that fails repeatable validation
Deliverables:
- services/nomads.py
- model catalog definitions
- GRIB parsing helpers
- tests for URL generation and parsing

5. Radar Services Agent
Scope:
- implement radar display-ready overlays
Required sources:
- https://radar.weather.gov/
- https://opengeo.ncep.noaa.gov/geoserver/
- https://mrms.ncep.noaa.gov/data/
Tasks:
- identify usable radar layers
- implement overlay toggle
- implement opacity control
- implement animation if practical
- implement MRMS overlays if validated
Rules:
- prefer display-ready layers first
- do not implement raw Level II parsing in v1 unless clearly required and validated
Validation:
- confirm layer URLs work
- confirm rendering compatibility with Streamlit map approach
Deliverables:
- services/radar.py
- supported layer catalog
- source validation notes
- tests

6. Radar Station Agent
Scope:
- implement searchable radar station map and metadata support
Required sources:
- https://coast.noaa.gov/arcgismc/rest/services/hosted/WeatherRadarStations/FeatureServer/0
- https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt
Tasks:
- load all U.S. NEXRAD and TDWR stations
- display pins
- support search by station code
- support nearest-station lookup
- support metadata popups
Validation:
- confirm field mappings
- confirm fallback to text file if service fails
Deliverables:
- services/stations.py
- nearest station utility
- tests

7. Geospatial and Search Agent
Scope:
- location utilities
Tasks:
- city/state to lat/lon
- nearest radar lookup
- bbox helpers
- timezone lookup for local display
Deliverables:
- utils/geospatial.py
- tests

8. Units and Labels Agent
Scope:
- make output understandable to U.S. users
Tasks:
- convert and format units
- map cryptic variables to plain English
- support simple mode and advanced mode labels
Default units:
- temperature F
- wind mph
- precip inches
- pressure mb
- distance miles
Deliverables:
- utils/units.py
- utils/labels.py
- tests

9. UI and Streamlit Agent
Scope:
- build the app shell and tabs
Required tabs:
1. Radar
2. Models
3. Point Forecast
4. Alerts
5. Stations
Tasks:
- responsive layout
- map interaction
- sidebar controls
- simple mode / advanced mode
- source status indicators
- clear error handling
Validation:
- fast startup
- no heavy downloads on initial render
Deliverables:
- app.py
- UI components
- page layout logic

10. Caching and Performance Agent
Scope:
- optimize performance and startup
Tasks:
- apply Streamlit caching correctly
- separate first render from heavy workflows
- avoid unnecessary requests
- add local cache for model subsets where appropriate
Deliverables:
- performance helpers
- caching strategy notes

11. QA and Test Agent
Scope:
- validate the entire application
Tasks:
- unit tests
- integration checks
- endpoint validation
- startup verification
- verify every UI-advertised source actually works
Rules:
- if a source fails validation, remove it and document why
Deliverables:
- tests/
- source reliability report
- merge-readiness checklist

12. Documentation Agent
Scope:
- complete developer and deployment documentation
Tasks:
- README
- setup instructions
- deployment instructions
- source notes
- known limitations
- contributor workflow
Deliverables:
- README.md
- CONTRIBUTING.md
- deployment notes

TECH STACK

Use:
- Python 3.11
- streamlit
- requests or httpx
- pandas
- xarray
- cfgrib
- eccodes
- pydeck or another Streamlit-compatible map layer approach
- plotly or altair
- pytest

PROJECT STRUCTURE

Create this structure:

toganoxie-split/
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ services/
│  ├─ __init__.py
│  ├─ nws_api.py
│  ├─ open_meteo.py
│  ├─ nomads.py
│  ├─ radar.py
│  └─ stations.py
├─ utils/
│  ├─ __init__.py
│  ├─ geospatial.py
│  ├─ units.py
│  └─ labels.py
├─ tests/
│  ├─ __init__.py
│  ├─ test_nws_api.py
│  ├─ test_open_meteo.py
│  ├─ test_nomads.py
│  ├─ test_radar.py
│  ├─ test_stations.py
│  ├─ test_geospatial.py
│  ├─ test_units.py
│  └─ test_labels.py
├─ app.py
├─ README.md
├─ CONTRIBUTING.md
├─ requirements.txt
├─ pyproject.toml
└─ .gitignore

UI PRODUCT REQUIREMENTS

The app must have:
- simple mode
- advanced mode

Simple mode should expose plain-English fields like:
- temperature
- dew point
- wind speed
- wind gust
- CAPE
- reflectivity
- precip rate
- snowfall
- cloud cover
- freezing level

Advanced mode should expose:
- raw model names
- raw variable names
- vertical levels
- forecast hours
- run times
- radar layer metadata

ENGINEERING RULES

- no fake data
- no mocked production responses in user-facing workflows
- no hardcoded unsupported variables
- no undocumented assumptions
- no blocking heavy computations on first app load
- all external calls should be wrapped in source adapters
- all adapters should degrade gracefully
- all user-facing data should be traceable to a validated source
- all startup imports must succeed cleanly

CI REQUIREMENTS

Create `.github/workflows/ci.yml` that:
- runs on pull_request and push to main
- sets up Python 3.11
- installs dependencies
- runs a basic import check
- runs pytest
- fails on errors

CONTRIBUTING REQUIREMENTS

Create `CONTRIBUTING.md` with:
- main branch protection expectations
- feature branch naming
- PR requirements
- test requirements
- merge gates
- documentation update rules

REQUIREMENTS.TXT

Include at minimum:
- streamlit
- requests
- httpx
- pandas
- xarray
- cfgrib
- eccodes
- pydeck
- plotly
- pytest

PYPROJECT.TOML

Add minimal pytest config and basic project metadata.

README REQUIREMENTS

README must include:
- project purpose
- supported data sources
- setup instructions
- run instructions
- deployment notes
- current limitations
- architecture summary
- future enhancements

MERGE ORDER FOR FUTURE FEATURE BRANCHES

After bootstrap on main, recommend this order:
1. feature/product-architecture
2. feature/nws-api
3. feature/open-meteo
4. feature/radar-stations
5. feature/radar-services
6. feature/geospatial-utils
7. feature/units-labels
8. feature/nomads-models
9. feature/ui-streamlit
10. feature/performance-caching
11. feature/tests-qa
12. feature/documentation

DEFINITION OF DONE FOR MAIN

`main` is considered valid only if:
- bootstrap files exist
- the project runs locally
- app imports succeed
- CI workflow exists
- tests execute
- no placeholder data is exposed
- documentation exists
- future work is clearly structured for branch-based development

EXECUTION ORDER

Perform the following now, in order:

PHASE 1: BOOTSTRAP MAIN
- create the foundational file structure
- add minimal executable code for app startup
- add CI, README, gitignore, requirements, and contributing guide
- ensure `app.py` runs with a simple placeholder shell that clearly states which modules are pending implementation
- create the first bootstrap commit message text

PHASE 2: PLAN FEATURE WORK
- generate a branch plan
- map each future branch to a sub-agent
- define acceptance criteria for each branch

PHASE 3: IMPLEMENT MINIMAL EXECUTABLE BASELINE
- `app.py` must run
- imports must work
- empty adapters must be syntactically valid and documented
- tests should include at least a startup/import smoke test

PHASE 4: OUTPUT
Return:
1. the full file tree
2. the exact contents of every created bootstrap file
3. the initial commit message
4. the recommended next branch to create
5. the acceptance criteria for that next branch

Important:
- Do not skip the bootstrap-main step
- Do not assume `main` already exists
- Do not invent unsupported APIs
- Do not expose unverified radar/model claims in the UI
- Keep the initial main branch minimal, executable, and ready for branch-based expansion
