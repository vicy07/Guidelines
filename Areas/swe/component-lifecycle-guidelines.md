# Component Lifecycle, License, and EOL Audit Standard

Version: 1.1.0
Owner: SWE Lead
Last Updated: 2026-08-01

## Purpose

Define the mandatory component-inventory, license, criticality, end-of-life (EOL), and lifecycle-risk contract for downstream product repositories.

## Scope

The audit covers all components needed to build, run, operate, or recover the product:

- direct and transitive libraries, packages, frameworks, runtimes, base images, operating systems, and build tools,
- third-party APIs, SaaS products, managed services, identity providers, payment providers, data feeds, and other external dependencies,
- first-party architectural components such as applications, services, workers, data stores, queues, gateways, scheduled jobs, and deployment/runtime platforms.

Test-only or development-only components remain in scope but may receive lower criticality when their failure cannot affect build integrity, release safety, security, compliance, or recovery.

## Required Downstream Artifacts and Entry Points

Every downstream repository must provide:

- `audits/config/components.yaml` for license/lifecycle data sources, review intervals, thresholds, and documented exceptions,
- `audits/scanners/components.py` for repository-specific component discovery and license/lifecycle-source adapters,
- `audits/sbom/components.cdx.json` as the tracked, machine-readable current component and lifecycle-risk record,
- `python audits.py components scan` to refresh and evaluate the SBOM,
- `python audits.py components check` to validate the committed SBOM without silently refreshing license or lifecycle evidence,
- inclusion of the component check in `python audits.py all`, CI, scheduled monitoring, and release readiness.

The SBOM must use CycloneDX JSON. The repository may choose the currently supported CycloneDX schema version, but it must validate the file against that declared schema. Generated reports may live under `reports/audits/`; the current enriched SBOM must remain in `audits/sbom/components.cdx.json` and must be committed when its inventory or lifecycle assessment changes.

## Component Identity and Coverage

Each component must have a stable `bom-ref` and, when applicable, a Package URL (PURL), CPE, vendor identifier, or canonical service identifier. Dependency relationships must be represented explicitly.

The SBOM must distinguish these component classes:

- `library` - direct or transitive software dependency,
- `third-party` - externally operated API, SaaS, managed service, platform, or data dependency,
- `architecture` - first-party logical or deployable component,
- `runtime` - language runtime, operating system, base image, database engine, broker, or other execution substrate,
- `build` - compiler, package manager, CI action, generator, or other release-producing tool.

Inventory discovery must combine package/lockfile and image discovery with the documented architecture and integration inventory. Package scanners alone are insufficient because they cannot prove coverage of SaaS and first-party architecture boundaries.

## Required License, Lifecycle, and Risk Fields

Every in-scope component must record the following CycloneDX fields or namespaced component properties:

- component class,
- owner,
- license expression using valid SPDX identifiers or expressions when available; otherwise an explicit `proprietary`, `custom`, `unknown`, or `not-applicable` value with rationale,
- license type: `permissive`, `weak-copyleft`, `strong-copyleft`, `network-copyleft`, `proprietary-commercial`, `public-domain`, `custom`, `unknown`, or `not-applicable`,
- license evidence source and `last-checked` timestamp,
- criticality: `Critical`, `High`, `Medium`, or `Low`,
- lifecycle status: `supported`, `maintenance`, `eol-scheduled`, `eol`, or `unknown`,
- EOL date when published, otherwise `Evidence not available`,
- evidence source and `last-checked` timestamp,
- next review date,
- risk level: `Critical`, `High`, `Medium`, or `Low`,
- concise risk rationale,
- remediation or replacement plan, owner, and target date when action is required.

Use the native CycloneDX `licenses` field for SPDX identifiers/expressions when the schema supports the required representation. Use the `guidelines:` namespace for custom CycloneDX properties, for example `guidelines:license-type`, `guidelines:license-evidence-source`, `guidelines:criticality`, `guidelines:lifecycle-status`, and `guidelines:risk-level`. Absence of license evidence must be stored as `unknown`; package metadata alone must not be treated as proof when it conflicts with the distributed source, image, binary, or vendor terms. Absence of published lifecycle information must be stored as `unknown`; it must never be inferred as `supported`.

Lifecycle evidence must prefer the component owner's published lifecycle/support policy, followed by the authoritative package registry or maintained ecosystem lifecycle data. First-party components must reference the repository's own approved support or retirement decision. Secondary aggregators may aid discovery but must not silently override authoritative evidence; conflicting sources require owner review.

## License Compatibility and Risk

License review must happen during solution design, before a component or architecture option is approved, and must be refreshed when the component version, build or linking model, modification status, packaging, deployment, distribution channel, commercial use, or service-exposure model changes.

For each component, evaluate the actual intended use and record material obligations or restrictions, including when applicable:

- source-code or corresponding-source disclosure,
- attribution, copyright, license-text, and notice-file preservation,
- redistribution, modification, static/dynamic linking, combined-work, or derivative-work conditions,
- patent grants, patent retaliation, trademark limits, and warranty or liability disclaimers,
- network-use/source-offer obligations,
- commercial-use, field-of-use, user-count, geography, environment, or redistribution restrictions,
- compatibility with other licenses and with the product's proprietary or open-source distribution model.

Classify license risk as `Critical`, `High`, `Medium`, or `Low` and record the rationale, affected artifact or delivery model, required compliance action, decision owner, and target date. `unknown`, `custom`, non-standard, source-available, or conflicting license evidence requires explicit review; it must not be silently treated as permissive. Where a license conclusion could materially affect distribution rights, source disclosure, commercial use, or contractual obligations, record review by an authorized legal or compliance owner. An automated scanner or AI review may identify evidence and risks but must not claim legal approval.

## Criticality Classification

Assign the highest applicable level:

| Criticality | Required interpretation |
|---|---|
| Critical | Loss or compromise can stop a critical user journey, breach a security/privacy/compliance boundary, corrupt or expose irreplaceable data, or make recovery objectives unattainable; no safe timely workaround exists. |
| High | Loss or compromise causes major product or operational degradation, weakens an important security boundary, or threatens release/recovery; only a limited or costly workaround exists. |
| Medium | Failure affects a non-critical capability or internal workflow and has a tested workaround within accepted service objectives. |
| Low | Failure has minor, isolated impact and a simple tested workaround; it does not affect security, compliance, build integrity, or recovery. |

Criticality must be based on actual use, transitive blast radius, data sensitivity, privilege, availability, integrity, compliance, recovery, and substitutability. Popularity, package type, or direct-versus-transitive status alone must not determine criticality.

## Lifecycle Exposure

Classify lifecycle exposure as follows:

| Exposure | Condition |
|---|---|
| Critical | Component is EOL/unsupported, or authoritative lifecycle evidence is unavailable for a `Critical` component. |
| High | EOL is within 90 days, or evidence is unavailable for a `High` component. |
| Medium | EOL is more than 90 days but within 12 months, the component is maintenance-only, or evidence is unavailable for a `Medium` component. |
| Low | Supported for more than 12 months, or evidence is unavailable only for a `Low` component with documented owner review. |

Determine overall lifecycle risk from this matrix:

| Component criticality \ Lifecycle exposure | Low | Medium | High | Critical |
|---|---|---|---|---|
| Critical | Medium | High | Critical | Critical |
| High | Low | Medium | High | Critical |
| Medium | Low | Medium | Medium | High |
| Low | Low | Low | Medium | Medium |

A documented compensating control may reduce the matrix result only when it demonstrably reduces likelihood or impact. A reduction requires an owner, evidence, expiry/review date, and replacement or containment plan in the SBOM.

## Mandatory Gates and Monitoring

- CI must fail when the SBOM is missing, invalid, stale beyond the configured review interval, or no longer matches detected dependencies and documented architecture components.
- CI must fail when an in-scope component lacks the required license expression/value, license type, or license evidence, unless a documented time-bounded exception applies.
- CI and release readiness must fail for unresolved `Critical` or `High` license risk, incompatible license combinations, or unmet obligations that affect the artifact being built, deployed, or distributed.
- CI and release readiness must fail for an EOL/unsupported `Critical` or `High` component.
- CI and release readiness must fail for a `Critical` component whose EOL is within 90 days and has no approved migration completed before the EOL date.
- Unknown lifecycle evidence for `Critical` or `High` components must fail the gate until an owner records authoritative evidence or a time-bounded exception.
- Other `High` or `Critical` risk findings require a remediation owner and target date; expired exceptions fail the gate.
- Scheduled monitoring must run at least weekly and whenever the inventory, architecture, component version, build/linking/packaging model, distribution model, runtime/base image, or external-provider contract changes.
- Scheduled monitoring must refresh evidence, update `audits/sbom/components.cdx.json`, retain a dated audit report, and create a reviewable change or alert when license, lifecycle, or risk state changes.
- A passing vulnerability scan does not satisfy this audit: a component may be vulnerability-free and still have incompatible or restrictive terms, be unsupported, or be approaching EOL.

## Ownership Boundaries

- SWE owns inventory completeness, stable component identity, architecture/dependency relationships, license evidence and technical-use classification, initial criticality, and remediation design.
- SRE owns monitoring cadence, authoritative lifecycle-source operation, alerting, runtime/platform component coverage, and release enforcement.
- QA owns gate verification, missing/conflicting-license scenarios, stale/drift scenarios, exception-expiry tests, and evidence that risk transitions produce the required failure or alert.
- BA and PO validate business-impact, intended-use, commercial-use, and distribution assumptions for components mapped to critical user journeys or regulatory obligations.
- An authorized legal or compliance owner approves interpretations that materially affect distribution rights, source-disclosure duties, commercial use, or contractual obligations; AI and scanner output is evidence, not approval.

Cross-role decisions must record who approved license compatibility and criticality, who owns remediation, and which evidence supports each classification.

## Quality Checklist

- Libraries, third-party dependencies, runtimes/build tools, and architectural components are all represented.
- Direct and transitive relationships are present and stable across refreshes.
- Every component has owner, criticality, lifecycle status, evidence freshness, and risk rationale.
- Every component has a license expression/value, license type, evidence source, and current compatibility/risk assessment for its actual use.
- Architecture decisions identify license obligations and restrictions before component adoption.
- `unknown` is visible and gated according to criticality.
- Scheduled and change-triggered monitoring refresh the tracked SBOM.
- CI tests missing, unknown, conflicting, or incompatible license data plus invalid, stale, drifted, EOL, near-EOL, and expired-exception states.
- Remediation records name an owner and target date.
