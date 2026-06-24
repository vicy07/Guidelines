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
  agents/
  docs/
  execution/
  runtime/
  guidelines/
  shared-sonar/
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
- `shared-sonar/` - reusable SonarQube runner logic for product repositories.
- `execution/`, `runtime/`, `agents/`, `docs/`, `guidelines/` - supporting assets for structured agent workflows and reusable patterns.
- `scripts/` - repository validation and maintenance tooling.
- `tests/` - regression coverage for repository-owned code and helpers.

## Instruction Retrieval Path

1. Start with `AGENTS.md` for execution rules and instruction precedence.
2. Use `phases-index.md` to identify the current lifecycle phase and active roles.
3. Use `guidelines-index.yaml` to resolve the files that apply and the dependencies that must stay aligned.
4. Use `Product-Repository-Blueprint.md` for downstream repository structure and minimum delivery requirements.
5. Use `Adoption-Guide.md` when applying these standards to a new or existing project.
6. Open the role-owned standards in `Requirements/`, `SWE/`, `QA/`, and `SRE/` for role-specific rules.

## Governance Files

- `AGENTS.md` - execution contract and precedence rules.
- `phases-index.md` - lifecycle phase to role map.
- `guidelines-index.yaml` - machine-readable ownership and dependency index.
- `Repository.md` - structure and navigation contract for this repository.
- `Product-Repository-Blueprint.md` - downstream project baseline.
- `Adoption-Guide.md` - onboarding and migration guidance.

## Definition of Ready

This repository is structurally ready when:

- root files and folders match this document,
- `README.md`, `Repository.md`, `Product-Repository-Blueprint.md`, and `Adoption-Guide.md` describe the same baseline,
- `phases-index.md` and `guidelines-index.yaml` point to real files and active roles,
- normative files contain required metadata fields,
- validation passes with `npm run validate-guidelines`.
