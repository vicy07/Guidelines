# AI Delivery Control Plane Architecture

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

## Overview

This repository provides a control-plane architecture for role-based AI delivery.
It preserves legacy guideline domains while adding executable runtime contracts.

## Core Layers

- `guidelines/`: durable principles, patterns, playbooks, and anti-patterns.
- `execution/`: schemas, prompts, flows, and executable examples.
- `agents/`: role contracts for `BA`, `SWE`, `QA`, and `SRE`.
- `runtime/`: phase and orchestration models.
- `docs/`: architectural and execution documentation.

## Control Plane Pipeline

1. `BA` emits a requirement artifact.
2. `SWE` emits implementation tasks and code outputs.
3. `QA` emits test evidence.
4. `SRE` emits deployment status.

## Backward Compatibility

- Existing `Requirements`, `SWE`, `QA`, and `SRE` guideline folders remain intact.
- Existing governance files remain authoritative for repository policy.
- New runtime artifacts extend, not replace, current standards.
