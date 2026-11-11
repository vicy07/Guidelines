# Cost-Aware Web Hosting and Monitoring

Version: 1.0.0
Owner: SRE Lead
Last Updated: 2026-11-11

## Purpose and Ownership

Prevent public content, monitoring and background traffic from creating avoidable
application or database runtime costs. Static landing separation is mandatory;
sleep behavior follows the product's availability and recovery requirements.
This policy supplements, and does not waive, the selected repository profile.

- SWE owns deployment/routing boundaries, client behavior and dependency traffic.
- SRE owns runtime mode, monitoring configuration, wake sources and cost evidence.
- QA owns network isolation, idle/cold-start and migration acceptance evidence.
- PO/BA own availability, latency and cost trade-offs. Critical-system security,
  recovery and alert coverage cannot be removed merely to reduce spending.

## Trigger and Inputs

Apply to new hosted web designs, baseline adoption, landing/app migrations, and
changes to monitoring, healthchecks, telemetry, jobs, routing or sleep settings.
Inputs are the architecture, selected profile, SLOs, deployed IaC/configuration,
DNS/routing, monitor/scheduler/exporter configuration and available usage records.
Do not start a full audit or change another repository's production implicitly.

## Mandatory Static Landing Boundary

Every web product with a public landing must serve that landing as a separate
static deployment on a CDN/static host, independently of application logic and
the application database. A monorepo and shared source assets are allowed;
separate folders or routes on the same billed application runtime do not satisfy
the boundary. Public landing visits, crawlers and cache misses must not execute
the backend. Products without a landing record this applicability explicitly;
they need not invent one. This separation also applies to always-on backends.

- Serve landing HTML, assets, robots, public release/build metadata and unknown
  paths from the static host. Build metadata must be embedded during the build,
  not fetched from the application merely to render a footer/status line.
- Do not bootstrap the app, fetch session/auth/API state, perform backend
  prefetch/preconnect checks, or redirect automatically based on backend state.
  An explicit Open application/Sign in action may navigate to the app origin.
- Do not use an application origin fallback, catch-all proxy, or blanket redirect
  of unknown paths to the app. Enumerate necessary legacy routes individually;
  keep scanner paths and static 404s on the static host. Robots directives are
  crawler hints, not a control that prevents backend wake-ups.
- Build and publish an allowlisted static artifact through the documented
  Git-based delivery workflow. Exclude secrets, local state and private app pages.
  Static landing requests must not invoke SSR, edge Functions or application
  telemetry pipelines. Verify any optional external assets/analytics for
  privacy, necessity and backend isolation; they are not baseline requirements.
- Record origins, DNS/TLS, auth callback/token-exchange URIs, cookie scope,
  logout/session expiry, deep links, browser storage and notification callbacks.
  Preserve query strings and required HTTP methods across approved redirects.
  Do not weaken cookie, CORS, CSRF or authentication controls to make a split work.
- Prefer a suitable free/static tier for small landings after checking its
  current limits and terms. Cloudflare Pages is an option, not a required vendor
  or a promise that application, DB, storage or domain registration is free.

## Runtime Mode and Wake-Source Inventory

Declare each component as `scale-to-zero`, `always-on` or `finite-job` in existing
architecture/SRE documentation. Prefer scale-to-zero when supported by latency,
availability, security and recovery objectives. Record a reason and cost owner
for always-on operation. A platform sleep toggle is configuration evidence, not
proof that a deployed container actually sleeps.

Inventory all producers that can reach or keep a component active, including
external monitors, platform probes, collectors, CI, browser tabs, DB clients,
jobs and backup agents. Record target, purpose, owner, cadence, timeout/retry
limits, wake/keep-awake behavior, approved runtime window and evidence. Treat
unknown behavior as unverified, not as non-waking.

| Producer | Default for scale-to-zero components | Required boundary |
| --- | --- | --- |
| Uptime HTTP/HEAD/TCP probes, synthetic transactions, pull metric scraping | No recurring calls to a sleeping app or DB | Use verified non-waking signals, or an approved monitoring exception |
| Deployment/startup readiness | Bounded during launch/promotion | Prove provider lifecycle behavior; no perpetual warm-up loop |
| OTLP exporters, heartbeat metrics, SDK telemetry, remote config polling | No synthetic idle traffic to prove presence | Export real activity; stop/bound empty exports, retries and periodic packets |
| DB pools, keepalives, SELECT 1 loops, queue consumers | No idle polling solely to retain readiness | Validate connection/idle behavior for the actual provider and dependencies |
| Browser notification/session polling, refresh, prefetch | None on landing; no needless hidden/inactive-tab polling in app | Bound active-use behavior, pause/back off on inactivity and resume safely |
| Cron, imports, notifications, backups, network security scans | Named bounded work windows, then exit/idle | Retain required security/recovery coverage; batch work and cap retries |

An outbound packet, private service call or DB connection can prevent sleep even
when public network graphs appear empty. A scheduled caller must have a real
business, security or recovery purpose; do not create keep-warm jobs to conceal
cold-start behavior. Authenticated app domains can still receive direct bot
traffic after landing separation: consider edge filtering without blocking
legitimate auth, notification or security flows.

## Health and Monitoring Rules

1. Separate process liveness from dependency readiness. A liveness handler must
   be cheap and must not query the DB, queue or external APIs. Readiness may
   check required dependencies with bounded timeouts when readiness is needed.
   Even a dependency-free HTTP handler can wake a dormant application.
2. Keep bounded startup/deployment checks and approved on-demand diagnosis.
   Establish whether a platform healthcheck is deployment-only or recurring
   from current provider documentation and effective runtime configuration.
   Do not remove deployment safety just because an external uptime probe is
   expensive, or assume that every setting called healthcheck is non-waking.
3. For expected-idle components prefer platform lifecycle/error events,
   already-collected logs/metrics and control-plane status. Verify that the
   monitoring path does not itself call the application or connect to its DB.
   Monitor static landing/DNS/TLS separately, with equally verified wake effects.
   An available landing or sleeping container does not prove API/DB health.
4. Model `running`, `expected idle`, `failed` and `unknown/stale evidence`
   separately. Evaluate errors/latency on real activity, failures to start,
   unexpected restarts and missed approved job deadlines. Silence during
   expected idle is not an outage or proof of health. A finite job's missing
   completion is a failure signal without a recurring request to that job.
5. Recurring active monitoring that would wake a sleeping component requires
   PO/BA and SRE approval of the coverage/SLO reason, target, cadence, bounded
   retries, cost allowance, owner and review/expiry point. If continuous
   availability is required, declare and budget always-on operation explicitly.
   Record compensating controls and coverage gaps when changing existing alerts;
   never silently disable critical security, recovery or availability coverage.

Monitoring configuration, alert rules, IaC, scheduler entries and telemetry SDK
settings must be reconciled together through their owning reviewed Git paths.
Disabling an alert while retaining its probe does not eliminate the traffic;
removing a probe while retaining a missing-heartbeat alert creates false alarms.
Treat a documented cold start separately from a sustained incident; bounded
retries must preserve idempotency and must not hide genuine dependency failures.

## Execution and Verification

1. Establish the runtime modes, static boundary and wake inventory before
   choosing monitors. Map provider defaults and external/shared configuration,
   not only product code. Preserve the original route/config for rollback.
2. Implement the split and remove unintended idle traffic in one coherent
   reviewed batch. Use provider-specific settings in IaC; read back the effective
   deployed state. A setting that applies only to newly created containers
   requires a deployment before runtime acceptance.
3. In a clean browser inspect landing requests, including an existing-session
   case, idle timers and any service worker. Verify no backend connections or
   background session checks; test static unknown paths and explicit app entry.
   Test real auth, cookie persistence, logout/session expiry and approved legacy
   callbacks. Record browser-origin storage/session migration limitations.
4. Observe an agreed quiet interval longer than the provider's idle-detection
   window plus sampling margin, using verified non-waking lifecycle/log/resource
   evidence. Keep the intended monitors enabled; account for test tabs/polling
   and real users. Do not poll health, SSH into the app or query its DB to check
   whether it slept. Record contaminating traffic and repeat only when needed.
5. Confirm expected sleep and no unexplained wake/keep-awake sources. Perform
   one approved cold-start canary and record startup/recovery latency, bounded
   retries and useful diagnostics; then confirm return to expected idle.
   If signals or a quiet window are unavailable, report Evidence not available
   and retain the unmet acceptance item rather than claiming idle-cost success.
6. Compare attributable usage over comparable post-change periods. Record
   elapsed running time, memory/CPU, requests/egress, storage, scheduled work,
   provider minimums/credits and residual costs where applicable. Separate
   measured savings, qualified estimates and an unproven target. Deployment
   success, a sleep flag or a free landing does not prove a monthly cost target.

## Required Outputs and Exit Criteria

Use existing architecture, QA and SRE/runbook/release records for the runtime
modes, static routing, wake inventory, approved exceptions, configured owners,
dated provider behavior, verification evidence and rollback. No duplicate empty
document set is required. Release gates must cover static isolation and
app/auth migration; cost/sleep outcomes remain open until their declared
observation criteria have evidence. Structural baseline validation alone cannot
prove network isolation or runtime sleep. Existing products migrate through an
owned reviewed adoption plan; this policy does not mutate their configuration.

## Escalation

If required reliability/security coverage conflicts with sleep, PO/BA and SRE
must approve the runtime mode and budget, with QA verifying the selected
controls. If the platform cannot support the required behavior, record the
constraint and a bounded exception/migration plan; do not claim compliance by
renaming a dynamic landing static or turning off essential monitoring.

## Provider References

Checked 2026-11-11; recheck when the provider/runtime contract changes.

- [Railway Serverless](https://docs.railway.com/deployments/serverless): outbound
  and dependency traffic affects idleness; verify the deployed container setting
  and cold-start behavior instead of assuming a toggle is sufficient.
- [Railway Healthchecks](https://docs.railway.com/deployments/healthchecks):
  the documented probe runs during deployment, not as continuous monitoring;
  retain that readiness safeguard separately from external uptime checks.
- [Cloudflare Pages pricing](https://developers.cloudflare.com/pages/functions/pricing/):
  distinguish static asset hosting from Functions and the application's costs.
