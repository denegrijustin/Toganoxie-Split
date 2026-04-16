# Contributing

## Main branch protection expectations
- `main` is production-ready and deployable at all times.
- Do not develop features directly on `main` after bootstrap.
- Merge to `main` only through pull requests.

## Feature branch naming
Use these branch names for planned work:
- `feature/product-architecture`
- `feature/nws-api`
- `feature/open-meteo`
- `feature/nomads-models`
- `feature/radar-services`
- `feature/radar-stations`
- `feature/geospatial-utils`
- `feature/units-labels`
- `feature/ui-streamlit`
- `feature/performance-caching`
- `feature/tests-qa`
- `feature/documentation`

## Pull request requirements
- Scope each PR to a single feature branch objective.
- Document source validation and assumptions.
- Include tests for new behavior.
- Update docs for any user-facing or workflow changes.

## Test requirements
- Run `pytest` locally before opening/merging PRs.
- Ensure startup/import smoke checks pass.
- Fail loudly for unverifiable external assumptions.

## Merge gates
- CI must pass.
- No fake or placeholder production data in user-facing paths.
- All imports must succeed.
- Sources shown in UI must be validated and traceable.

## Documentation update rules
- Keep README and source notes in sync with implemented capabilities.
- Document removed/unsupported sources and limitations.
