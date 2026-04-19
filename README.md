# AI Delivery Control Plane

This repository is an AI Delivery Control Plane for role-based software delivery.
It combines legacy guideline standards with executable contracts, prompts, schemas, and orchestration flows.

## Positioning

- Legacy guidance remains available in `Requirements/`, `SWE/`, `QA/`, and `SRE/`.
- New executable control-plane assets live in `guidelines/`, `execution/`, `agents/`, `runtime/`, and `docs/`.
- The repository supports deterministic handoffs between `BA`, `SWE`, `QA`, and `SRE`.

## How Agents Use This Repo

1. Load runtime definitions from `runtime/phases.yaml` and `runtime/orchestration.yaml`.
2. Validate artifacts with schemas in `execution/schemas/`.
3. Execute role-specific contracts from `agents/*.md`.
4. Use prompts in `execution/prompts/` to produce structured outputs.
5. Follow reusable guidance from `guidelines/` and role standards from legacy folders.

## How Humans Use This Repo

1. Define or refine delivery standards in `guidelines/` and legacy role folders.
2. Evolve schemas and orchestration contracts in `execution/` and `runtime/`.
3. Review role boundaries and responsibilities in `agents/`.
4. Use `docs/architecture.md` and `docs/execution-model.md` for system-level understanding.

## Quick Start

1. Open `runtime/phases.yaml` to confirm the active role by phase.
2. Open `runtime/orchestration.yaml` to view end-to-end delivery flow.
3. Validate requirement payload shape with `execution/schemas/requirement.schema.json`.
4. Use `execution/prompts/swe_implement_feature.md` for SWE task generation.
5. Review end-to-end example in `execution/examples/feature-flow.md`.
6. Run validation: `node scripts/validate-guidelines.mjs`.

## Repository Map

- `guidelines/` - principles, patterns, playbooks, anti-patterns
- `execution/` - schemas, prompts, flows, examples
- `agents/` - BA/SWE/QA/SRE contracts
- `runtime/` - phase and orchestration definitions
- `docs/` - architecture and execution model
- `Requirements/`, `SWE/`, `QA/`, `SRE/` - backward-compatible standards
