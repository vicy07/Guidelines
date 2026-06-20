# Shared Sonar Runner

Shared SonarQube runner logic for product repositories that use:
- local `sonar-project.properties`
- Python coverage uploaded from `coverage.xml`
- JavaScript coverage uploaded from `coverage/js/lcov.info`

## Consumption Model

Keep repository-specific details local:
- `sonar-project.properties`
- test globs
- coverage targets
- project key defaults

Move shared behavior here:
- Sonar token and host resolution
- coverage pre-run workflow
- scanner command construction
- coverage artifact validation

## Expected Product-Repo Wrapper

Each product repository keeps a thin `sonar.py` wrapper that:
1. resolves the `Guidelines` repository via `GUIDELINES_REPO` or a sibling `../Guidelines`
2. loads `shared-sonar/sonar_runner.py`
3. passes repo-local coverage commands and defaults into `SharedSonarConfig`

## Default Coverage Contract

- Python report path: `coverage.xml`
- JavaScript LCOV path: `coverage/js/lcov.info`

## Local Prerequisites

- `SONAR_TOKEN` available via `~/.sonar.env`, local `.sonar.env`, env var, or CLI arg
- `npx` on `PATH`
- repo-specific Python coverage dependency installed locally, for example `pytest-cov`
