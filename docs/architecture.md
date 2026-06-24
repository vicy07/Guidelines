# Guidelines Repository Architecture

Version: 1.1.0
Owner: Repository Maintainer
Last Updated: 2026-06-24

## Overview

This repository is organized around a small practical baseline for agentic development.
The primary experience is:

1. governance and navigation,
2. role-owned standards,
3. downstream product-repository structure,
4. minimum delivery requirements.

Structured execution assets remain available as supporting material for teams that want schema-driven handoffs between roles.

## Repository Layers

- `AGENTS.md`, `phases-index.md`, `guidelines-index.yaml` - operating contract and navigation layer.
- `Requirements/`, `SWE/`, `QA/`, `SRE/` - role-owned standards layer.
- `Product-Repository-Blueprint.md`, `Adoption-Guide.md` - downstream adoption layer.
- `shared-sonar/` - reusable engineering tooling layer.
- `execution/`, `runtime/`, `agents/` - optional structured-execution layer.

## Primary Flow

For most consumers, the intended path is:

1. read the operating contract,
2. adopt the downstream project blueprint,
3. add the minimum artifacts and delivery gates,
4. reuse shared tooling where it reduces duplication.

## Optional Advanced Flow

If a team wants machine-validated role handoffs, it can additionally use:

- `execution/schemas/` for artifact shape,
- `agents/*.md` for role contracts,
- `runtime/*.yaml` for phase and orchestration definitions,
- `execution/examples/` for reference chains.

## Compatibility Rule

The optional execution layer may extend the repository, but it must not redefine the repository's purpose.
The repository remains a guidelines source first and an execution-assets host second.
