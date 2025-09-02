Analyse whole solution and generate one file: architecture.md

Executive summary for the application (Purpose, value, technology stack)
Set of C4 architecture diagrams (Context, Container, Component, Deployment), use PlantUML as code with legend in each diagram
Diagram of the Conceptual Data Model (using PlantUML ER or class diagrams)
List the business capabilities in a table (avoid any empty lines between rows and headers):
Capability
Business Value
Technical Component
Recover user stories and group them by business capabilities
🛠 Diagram Standards (strictly follow):

Use stable, explicit C4-PlantUML notation only. Avoid all aliases, shortcuts, or experimental forms.
For each type of diagram, use the correct PlantUML include:
For Context, Container, and Component diagrams:
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
For Deployment diagrams:
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml
Allowed diagram elements:
Person(...), System(...), System_Ext(...)
Container(...), ContainerDb(...)
Component(...), Rel(...)
Deployment_Node(...)
Disallowed / unstable constructs (never use):
DeploymentNode(...), SystemDb(...), SHOW_LEGEND(), LAYOUT_NEAT()
Any C4 aliases or undocumented macros
Always provide unique, lowercase, underscore-separated aliases for all elements:
✅ Container(api_service, "API", ...)
❌ Container(API, ...)
Use LAYOUT_WITH_LEGEND() to display diagram legends (not SHOW_LEGEND()).
All diagrams must render successfully in both:
PlantUML Online Server
Offline plantuml.jar with default settings
If data is missing or not found in the source, explicitly state: "Evidence not available" in the Markdown.
Do not invent or assume anything. Base the output only on observable facts, available code, and explicit configuration. If inference is needed, clearly indicate it as a hypothesis.
