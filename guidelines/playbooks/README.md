# Delivery Playbooks

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-04-19

## Purpose

Store executable, role-aware playbooks that can be run by agents or humans.

## Scope

- `audit-reporting-standard.md` defines the opt-in, single-file audit contract
  for an explicitly assigned Audit Operator or a named human running locally.

## Playbook Contract

Each playbook should include:
- Trigger condition
- Inputs
- Execution steps
- Required outputs
- Exit criteria
- Escalation rules
