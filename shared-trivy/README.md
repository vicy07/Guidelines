# Shared Trivy Runner

Shared Trivy runner logic for product repositories that want a consistent security gate without copying the same CLI wiring into every repo.

For repositories that want a single multi-scanner entrypoint, prefer consuming this runner through `shared-audits`.

## Consumption Model

Keep repository-specific details local:

- `audits/config/trivy.yaml`
- target paths and image references
- report destinations
- suppression ownership records

Move shared behavior here:

- Trivy binary resolution
- local and global env loading
- default filesystem and image scan command construction
- consistent severity, scanner, timeout, and cache wiring
- `--show-config` inspection for local troubleshooting

## Expected Product-Repo Integration

Each product repository should:

1. keep `audits.py` and repo-local `audits/` scanner wiring
2. keep Trivy settings in `audits/config/trivy.yaml`
3. consume `shared-audits/` as the primary local entrypoint
4. let `shared-audits` call Docker-backed Trivy execution for filesystem and image scans

Root `trivy.py` entrypoints are not part of this baseline model.

## Expected Product-Repo Files

- `audits/config/trivy.yaml`
- optional `.trivyignore` when accepted findings must be suppressed

Recommended `audits/config/trivy.yaml` baseline:

```yaml
severity:
  - HIGH
  - CRITICAL
scanners:
  - vuln
  - misconfig
  - secret
format: table
exit-code: 1
timeout: 10m
```

## Default Scan Contract

- `python audits.py trivy scan` scans the repository filesystem from the repo root.
- `python audits.py trivy image <image-ref>` scans a deployable container image when the repository produces one.
- `python audits.py trivy config` prints resolved non-secret config and exits without running a scan.

## Local Prerequisites

- Docker installed
- Docker daemon running
- repo-local dependencies or build artifacts already prepared if the product repository depends on them for scanning

## Runtime Behavior

- the shared runtime passes repo-local `audits/config/trivy.yaml` when present
- the shared runtime passes repo-local `.trivyignore` when present
- Trivy runs through Docker and can persist its vulnerability database through a Docker volume cache
- the shared runtime defaults to `HIGH,CRITICAL` severity and `vuln,misconfig,secret` scanners unless the product repository overrides them
- the shared runtime returns the Trivy process exit code directly so CI and release workflows can fail deterministically
