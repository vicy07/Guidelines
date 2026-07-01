# Guidelines Repository Structure Standard

## Purpose

Define the canonical structure of this repository as a standards source for agentic development.
This repository governs how downstream product repositories should organize delivery artifacts, minimum engineering gates, and role-owned guidance.

## Scope Boundary

- This document describes the physical structure and navigation model of this repository.
- `Product-Repository-Blueprint.md` defines the downstream product-repository baseline.
- `Adoption-Guide.md` defines how to apply that baseline to new and existing projects.

## Required Root Structure

```text
<guidelines-repo>/
  Requirements/
  SWE/
  QA/
  SRE/
  docs/
  guidelines/
  shared-sonar/
  shared-trivy/
  shared-otel/
  shared-code-intel/
  scripts/
  tests/
  .github/
  README.md
  Repository.md
  Product-Repository-Blueprint.md
  Adoption-Guide.md
  AGENTS.md
  phases-index.md
  guidelines-index.yaml
```

## Top-Level Ownership

- `Requirements/` - shared requirements standards owned by `BA` with `PO` co-ownership.
- `SWE/` - architecture, implementation, and engineering-control standards.
- `QA/` - test strategy, evidence, and release-quality standards.
- `SRE/` - deployment readiness, operability, and incident standards.
- `Product-Repository-Blueprint.md` - canonical minimum downstream project baseline.
- `Adoption-Guide.md` - standard onboarding path for new and existing projects.
- `guidelines/` - shared principles, patterns, playbooks, and anti-patterns.
- `docs/` - small supporting repository-level documentation set.
- `shared-sonar/` - reusable SonarQube runner logic for product repositories.
- `shared-trivy/` - reusable Trivy runner logic for product repositories.
- `shared-otel/` - reusable OpenTelemetry starter pattern for product repositories.
- `shared-code-intel/` - reusable `SCIP + ast-grep + rg` code intelligence runner logic for product repositories.
- `scripts/` - repository validation and maintenance tooling.
- `tests/` - regression coverage for repository-owned code and helpers.

## Instruction Retrieval Path

1. Start with `README.md` for repository purpose and the normal entry points.
2. Use `Product-Repository-Blueprint.md` for downstream repository structure and minimum delivery requirements.
3. Use `Adoption-Guide.md` when applying these standards to a new or existing project.
4. Use `AGENTS.md`, `phases-index.md`, and `guidelines-index.yaml` when you need the repository's maintenance contract and dependency map.
5. Open the role-owned standards in `Requirements/`, `SWE/`, `QA/`, and `SRE/` for role-specific rules.

## Governance Files

- `AGENTS.md` - execution contract and precedence rules.
- `phases-index.md` - lifecycle phase to role map.
- `guidelines-index.yaml` - machine-readable ownership and dependency index.
- `Repository.md` - structure and navigation contract for this repository.
- `Product-Repository-Blueprint.md` - downstream project baseline.
- `Adoption-Guide.md` - onboarding and migration guidance.
- `docs/architecture/code-intelligence.md` - code-intelligence baseline and downstream implementation contract.

## Definition of Ready

This repository is structurally ready when:

- root files and folders match this document,
- `README.md`, `Repository.md`, `Product-Repository-Blueprint.md`, and `Adoption-Guide.md` describe the same baseline,
- `docs/architecture/code-intelligence.md` and `shared-code-intel/` describe the same code-intelligence baseline,
- `phases-index.md` and `guidelines-index.yaml` point to real files and active roles,
- normative files contain required metadata fields,
- validation passes with `npm run validate-guidelines`.
