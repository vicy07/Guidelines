# C4 Architecture Artifact Standard

Analyse the whole solution from observable repository evidence and produce a synchronized
architecture artifact set. Do not collapse the technical design into one file.

## Required artifact placement

- Keep `docs/architecture.md` short and navigational.
- Keep `docs/technical-architecture.md` as the deep technical design source of truth.
- Store C4 and conceptual data-model diagrams as PlantUML source under
  `docs/architecture/diagrams/`.
- Store material decisions as ADRs under `docs/architecture/adr/`.
- Store architecture reviews and migration plans under `docs/architecture/`.

The downstream repository may use an equivalent documented layout, but the source files,
decision records, and links must remain durable and reviewable in that repository.

## Required content

1. Executive summary: purpose, value, scope, and technology stack.
2. C4 Context, Container, Component, and Deployment diagrams when applicable.
3. Conceptual data model using PlantUML ER or class diagrams when applicable.
4. Business capabilities mapped to business value and technical components when the
   repository contains sufficient product evidence.
5. Recovered user stories grouped by business capability when requirements evidence exists.
6. Boundaries, integrations, quality attributes, security/privacy, observability,
   deployment, risks, trade-offs, constraints, and architecture-to-requirement traceability.

## Diagram standards

- Use stable, explicit C4-PlantUML notation only. Avoid aliases, shortcuts, or experimental forms.
- For Context, Container, and Component diagrams, use:
  `!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml`
- For Deployment diagrams, use:
  `!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml`
- Allowed elements are `Person(...)`, `System(...)`, `System_Ext(...)`, `Container(...)`,
  `ContainerDb(...)`, `Component(...)`, `Rel(...)`, and `Deployment_Node(...)`.
- Do not use `DeploymentNode(...)`, `SystemDb(...)`, `SHOW_LEGEND()`, `LAYOUT_NEAT()`,
  undocumented macros, or undocumented aliases.
- Use unique lowercase underscore-separated aliases, for example
  `Container(api_service, "API", "Runtime", "...")`.
- Use `LAYOUT_WITH_LEGEND()` to display diagram legends.
- All diagrams must render in both PlantUML Online Server and offline `plantuml.jar` with
  default settings.

If data is missing or not found in the source, explicitly state `Evidence not available` in
the Markdown. Do not invent architecture, user stories, capabilities, technology choices,
or runtime behavior. If inference is needed, label it as a hypothesis.
