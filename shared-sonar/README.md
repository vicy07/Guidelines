# Shared Sonar Runner

Shared SonarQube runner logic for product repositories that use:
- local Sonar settings, commonly in `audits/config/sonar-project.properties`
- Python coverage uploaded from `coverage.xml`
- JavaScript coverage uploaded from `coverage/js/lcov.info`

For repositories that want a single multi-scanner entrypoint, prefer consuming this runner through `shared-audits`.

## Consumption Model

Keep repository-specific details local:
- `audits/config/sonar-project.properties`
- test globs
- coverage targets
- project key defaults

Move shared behavior here:
- Sonar token and host resolution
- coverage pre-run workflow
- scanner command construction
- coverage artifact validation
- background task polling after upload
- quality gate verification with explicit `OK` / `ERROR` exit status

## Expected Product-Repo Integration

Each product repository should:
1. keep `audits.py` and repo-local `audits/` scanner wiring
2. keep Sonar settings in `audits/config/sonar-project.properties`
3. consume `shared-audits/` as the primary local entrypoint
4. let `shared-audits` call this lower-level runner for Sonar execution

Root `sonar.py` entrypoints are not part of this baseline model.

## Default Coverage Contract

- Python report path: `coverage.xml`
- JavaScript LCOV path: `coverage/js/lcov.info`

## Local Prerequisites

- `SONAR_TOKEN` available via `~/.sonar.env`, local `.sonar.env`, env var, or CLI arg
- `SONARQUBE_TOKEN` is also accepted as an alias for `SONAR_TOKEN`
- `npx` on `PATH`
- repo-specific Python coverage dependency installed locally, for example `pytest-cov`

## Runtime Behavior

- repositories typically invoke Sonar with `python audits.py sonar scan`
- coverage generation should fail fast before upload if coverage reports are missing
- after upload, the shared runner waits for SonarQube Compute Engine processing and then checks the project quality gate
- `python audits.py sonar config` should print resolved non-secret settings and exit without running a scan
