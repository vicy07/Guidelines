# Shared Trivy Runner

Shared Trivy runner logic for product repositories that want a consistent security gate without copying the same CLI wiring into every repo.

For repositories that want a single multi-scanner entrypoint, prefer consuming this runner through `shared-audits`.

## Consumption Model

Keep repository-specific details local:

- `trivy.yaml`
- target paths and image references
- report destinations
- suppression ownership records

Move shared behavior here:

- Trivy binary resolution
- local and global env loading
- default filesystem and image scan command construction
- consistent severity, scanner, timeout, and cache wiring
- `--show-config` inspection for local troubleshooting

## Expected Product-Repo Wrapper

Each product repository keeps a thin `trivy.py` wrapper that:

1. resolves the `Guidelines` repository via `GUIDELINES_REPO` or a sibling `../Guidelines`
2. loads `shared-trivy/trivy_runner.py`
3. passes repo-local defaults into `SharedTrivyConfig`

## Expected Product-Repo Files

- `trivy.yaml`
- optional `.trivyignore` when accepted findings must be suppressed

Recommended `trivy.yaml` baseline:

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

- `python trivy.py fs` scans the repository filesystem from the repo root.
- `python trivy.py image <image-ref>` scans a deployable container image when the repository produces one.
- `python trivy.py --show-config` prints resolved non-secret config and exits without running a scan.

## Local Prerequisites

- `trivy` on `PATH`
- repo-local dependencies or build artifacts already prepared if the product repository depends on them for scanning

## Runtime Behavior

- The shared runner passes repo-local `trivy.yaml` when present.
- The shared runner passes repo-local `.trivyignore` when present.
- The shared runner defaults to `HIGH,CRITICAL` severity and `vuln,misconfig,secret` scanners unless the product repository overrides them.
- The shared runner returns the Trivy process exit code directly so CI and release workflows can fail deterministically.
