# SRE Operations Guidelines

Version: 1.9.0
Owner: SRE Lead
Last Updated: 2026-10-14

## Metadata (required)

- Version
- Owner
- Last Updated
- Related Architecture Version
- Related QA Execution Version

## Required Sections

1. Reliability Objectives
2. Observability Baseline
3. Release Readiness Gates
4. Rollback Strategy
5. Runtime Configuration Controls
6. Capacity and Performance Controls
7. Operations Checklist

## Rules

- Apply `guidelines/playbooks/delivery-policy.md` for release identity and
  completion boundaries. Verify the promoted revision/artifact and applicable
  recovery readiness; GitHub Release creation is not a release gate.

- Reliability objectives must be explicit and measurable.
- Define diagnostics for the selected profile from
  `Areas/requirements/repository-profiles.md`: build/publication evidence for
  docs-only, host-controlled hooks for library/CLI, operational signals for
  service/web, and verified correlation/alerts for critical systems. Document
  an OTLP contract only when export is used.
- Critical systems require correlated logs, metrics, tracing and owned alerts
  before release; a missing signal needs an explicitly reviewed compensating
  control and verification under the profile contract.
- Every release path must include rollback readiness.
- Production application releases must originate from committed Git state and run through the repository's documented Git-based delivery workflow.
- Agents and operators must not publish application code directly through a hosting-platform CLI, UI, or API. This prohibition includes direct deploy, redeploy, upload, and code-replacing service mutations (for example, `railway up` or an equivalent platform command).
- Hosting-platform tools may be used read-only for diagnostics, logs, status, and post-deploy verification. Runtime configuration changes and emergency operations require their own documented, auditable path and must not be used to bypass Git-based code delivery.
- Release readiness must include fresh Trivy filesystem evidence and scanning
  of deployable images by immutable digest before promotion. Select filesystem
  scans by relevant risk trigger, approved schedule, or missing/stale release
  evidence; do not require a full scan before every merge. Follow
  `guidelines/playbooks/ci-verification-policy.md` for evidence and gate rules.
- Release readiness must include the component lifecycle/EOL gate, and scheduled monitoring must refresh the tracked downstream SBOM at least weekly and on inventory, architecture, runtime, or external-provider changes.
- Release readiness and CI must provide a reproducible code-intelligence path
  for `code-intel.py`, preferably through a containerized shared runtime, when
  indexed artifacts are required. Use incremental updates or matching cached
  artifacts where valid; a full rebuild is not required on every CI event.
- Runtime configuration changes must be auditable.
- Release records must link the accepted goal, owning Issues/PRs, exact version,
  immutable revision/artifact digest, environment, required acceptance boundary,
  verification evidence and rollback procedure. Preserve that record in the
  owning repository's existing release/runbook location; do not add duplicate
  documentation solely to satisfy a filename convention.
- Record release verification and notification delivery separately. A verified
  release with a failed notification requires notification recovery, not another
  deployment. A production-scoped Issue remains open until its acceptance
  evidence exists, or a linked delivery Issue explicitly owns that work.
- Notification handover must name an exact maintained entrypoint, execution
  host/directory, no-send health check, runtime configuration owner, authorized
  destination source, receipt/journal location and retry/reconciliation path.
  Keep credentials and private recipient values out of product repositories.
  Cross-repository agent behavior and the personal Telegram adapter are governed
  by AI-Governance; its current homelab implementation is documented at
  `https://github.com/vicy07/homelab/blob/main/docs/release-notifications.md`.
- Notification transport must preserve UTF-8 text through file/stdin, JSON and
  HTTP. Verify API acceptance, message ID, destination and returned text before
  marking sent. A durable product/version/environment journal prevents concurrent
  or repeated delivery; ambiguous outcomes require reconciliation before retry.
  Operator-observed reconciliation must retain its evidence source and must
  not be presented as an API-confirmed receipt.
- SRE documentation must publish exact OTLP client-facing endpoint patterns for external, in-cluster, and local runtime paths when those paths exist.
- Frontend applications document applicable client diagnostics/correlation and
  data-minimization controls; static content requires no client tracking.
- Library/CLI diagnostics must work without a collector or OTLP exporter;
  document optional host instrumentation and useful failure behavior.
- SRE handover must publish the exact Trivy entrypoints, thresholds, and suppression-record location used by the release path.
- SRE handover must publish the EOL scan/check entrypoints, lifecycle data sources, SBOM location, freshness threshold, alert path, and exception-expiry handling.
- In indexed mode, handover publishes implemented entrypoints, artifact
  location, cache/update model and revision-association rules. Basic navigation
  does not require index execution in CI or at release.
- If evidence is missing, state `Evidence not available`.

## Quality Checklist

- Reliability objectives are defined and owned.
- Alerting coverage exists for critical user-impact paths.
- Profile-required diagnostic coverage and any selected OTLP configuration are documented.
- Indexed execution/artifact freshness is documented when selected; basic
  navigation does not require generated index artifacts in CI or release automation.
- Trivy scan coverage and release thresholds are documented for applicable artifact types.
- Lifecycle/EOL coverage includes libraries, third-party services, runtimes/build tools, and first-party architecture components, with current risk state persisted in the SBOM.
- Rollback and recovery paths are validated.
- Production release evidence identifies the Git commit and the Git-based workflow that published it; no direct platform publication was used.
- Release readiness decision includes operational risk notes.
- Release/notification statuses are independent, evidence identifies the
  checked artifact/environment, and notification failures have an owner and
  recovery step without concealing successful release verification.
- Notification runbook provides an exact command and no-send doctor; QA has
  checked Cyrillic/emoji round trips, duplicates and ambiguous-response recovery.

## Release and Notification Ownership

- PO/BA own the user outcome, scope and acceptance boundary.
- SWE owns implementation, immutable artifact identity and delivery links.
- QA owns acceptance evidence and notification correctness/failure checks.
- SRE owns publish/deploy verification, rollback readiness, runtime notification
  configuration, journal persistence and recovery. Runtime SSH trust and secrets
  must be provisioned through the owner's established path.

Use the existing release record or the
`https://github.com/vicy07/AI-Governance/blob/main/templates/release.md`
starting point. `published`, `verified` and notification `sent` represent
different evidence. A release failure blocks promotion; a notification failure
leaves an explicit delivery obligation. A successful API response is not proof
that the user read the message.

## OTLP Endpoint Handover Pattern

When a repository or platform exposes an OpenTelemetry Collector, document client configuration in env form, not only as prose.

Recommended handover blocks:

External OTLP/HTTP:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com
```

Internal Docker or service-mesh OTLP/HTTP:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
```

Internal gRPC:

```dotenv
OTEL_SERVICE_NAME=my-service
OTEL_SERVICE_VERSION=
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

Signal-specific OTLP/HTTP fallback:

```dotenv
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otel-collector.example.com/v1/traces
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://otel-collector.example.com/v1/metrics
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=https://otel-collector.example.com/v1/logs
```

Required operator note:

- If the SDK follows the OTLP/HTTP specification, `OTEL_EXPORTER_OTLP_ENDPOINT` should be the base URL and the SDK will append `/v1/traces`, `/v1/metrics`, and `/v1/logs`.

## Trivy Release Gate Handover Pattern

Recommended release-gate entrypoints:

Filesystem baseline:

```text
python audits.py trivy scan
```

Deployable container image baseline:

```text
python audits.py trivy image ghcr.io/example/service:${GIT_SHA}
```

Required operator notes:

- Default repository thresholds should fail on `HIGH` and `CRITICAL` findings unless an approved repository-specific policy says otherwise.
- Accepted suppressions must be traceable to an owner, ticket, and review/expiry point.
- If a repository does not ship a deployable image, document that boundary explicitly in the release path.

## Code Intelligence Handover Pattern

Recommended repository entrypoints:

```text
python code-intel.py index
python code-intel.py graph
```

Required operator notes:

- This pattern applies to indexed mode. `SCIP + ast-grep + rg` is the shared
  reference runtime; select tools by actual language coverage and document
  fallbacks. Basic mode needs no custom index runtime.
- The preferred execution model is a containerized shared runtime rather than a manual host installation path.
- Generated artifacts should include commit or revision identity in `code-intel/index/manifest.json` so downstream automation can detect stale indexes.
