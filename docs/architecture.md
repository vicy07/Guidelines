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

## Repository Layers

- `AGENTS.md`, `phases-index.md`, `guidelines-index.yaml` - operating contract and navigation layer.
- `Requirements/`, `SWE/`, `QA/`, `SRE/` - role-owned standards layer.
- `Product-Repository-Blueprint.md`, `Adoption-Guide.md` - downstream adoption layer.
- `guidelines/` - reusable guidance patterns and anti-patterns.
- `shared-sonar/` - reusable engineering tooling layer.

## Primary Flow

For most consumers, the intended path is:

1. read the operating contract,
2. adopt the downstream project blueprint,
3. add the minimum artifacts and delivery gates,
4. reuse shared tooling where it reduces duplication.

## Simplicity Rule

Repository navigation should stay understandable to a human reader without requiring a specialized execution model.
Machine-friendly structure is welcome, but it must remain secondary to clarity.
