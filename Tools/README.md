# Tools

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-07-05

## Purpose

This folder groups reusable tooling and lower-level execution helpers for downstream repositories.

## Scope

- `audits/` - multi-scanner orchestration helpers
- `sonar/` - lower-level SonarQube runner logic
- `trivy/` - lower-level Trivy runner logic
- `otel/` - OpenTelemetry starter runtime
- `code-intel/` - lower-level AST-first code-intelligence runtime

## Usage Rule

Treat `Tools/` as a reusable runtime layer.
Keep repo-local wrappers, configs, and product-specific entrypoints in downstream repositories.
