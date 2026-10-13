# Delivery Playbooks

Version: 1.2.0
Owner: Repository Maintainer
Last Updated: 2026-10-14

## Purpose

Store executable, role-aware playbooks that can be run by agents or humans.

## Scope

- `delivery-policy.md` defines merge readiness, shared Definition of Done,
  releasable `main`, and release identity without GitHub Releases.

- `ci-verification-policy.md` defines fast CI, risk triggers, approved schedules,
  release evidence reuse, and feedback-cost controls.

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
