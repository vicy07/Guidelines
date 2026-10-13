# Guidelines и AI-Governance: пересмотр процесса разработки

Version: 1.0.0
Owner: Repository Maintainer
Last Updated: 2026-10-13

## Область и воспроизводимость

Запрос: оценить актуальность двух baseline, убрать тяжёлые сканы из каждого
CI и пересмотреть агентный governance как часть общего dev-процесса.
Это анализ правил и локальные исправления; эксплуатационный аудит продуктов
и проверка их текущих уязвимостей в область не входят.

Проверены локальные checkout, исходно без незакоммиченных изменений:

- Guidelines: `38c02ea3b3e73e6a15c7ec577dfc0b25c3e324bb`, commit date
  `2026-09-21T07:12:04+03:00`.
- AI-Governance: `15a908f1e92252546f715719ed100fc2ed4624eb`, commit date
  `2026-09-21T07:12:04+03:00`.

Анализ выполнен 2026-10-13 агентом в ролях SWE/QA/SRE, с оценкой влияния на
BA/PO/UX. Фазы: Solution Design → Implementation → Verification. Роли здесь
обозначают ответственность; отдельные агенты не запускались.

Прочитаны entry points, phase/index contracts, Blueprint, Adoption, затронутые
role profiles, требования, UX, SWE/security/lifecycle, QA и SRE стандарты,
shared runner documentation, выбранные реализации runner, CI и governance
installer/reporting/tests. Это не построчное ревью всего tooling-кода.
Сентябрьские изменения подтверждены git history: утверждение «не менялись
полгода» к текущему checkout неприменимо. Сравнение с конкретной исторической
версией не выполнено: исходный SHA пользователя не указан.

## Основной вывод

Сохраняются полезные основы: ответственность ролей, требования и traceability,
короткая архитектурная навигация, отдельный технический дизайн, incremental
adoption, evidence-based RCA, rollback и пакетная проверка гипотез.

Главная проблема — рост обязательного инструментального baseline без явной
модели применимости и стоимости. Обязательный контроль, наличие интеграции и
частота запуска местами смешаны. Для небольших задач это создаёт работу,
которая не добавляет соразмерной уверенности. Замеры длительности, стоимости,
flake rate и влияния правил на downstream-проекты: `Evidence not available`.
Поэтому ускорение пока является ожидаемым эффектом, а не измеренным результатом.

## Находки и решения

P1 — высокий приоритет для корректности или стоимости процесса; P2 — следующий
этап упрощения. Это приоритеты изменений baseline, а не CVSS уязвимости.

| ID | Приоритет | Доказательство и проблема | Решение / статус | Ответственность |
|---|---|---|---|---|
| G01 | P1 | Blueprint §CI/Trivy и SRE Rules требовали сканирование перед merge, тогда как audit-reporting-standard запрещает неявный полный аудит | Исправлено: отдельная CI policy, fast/change/schedule/release scopes, согласованы потребители | QA — scope/gates; SWE — selection; SRE — cadence |
| G02 | P1 | Blueprint §SonarQube требовал gate для main/release, не определяя частоту и условия reuse | Исправлено: Sonar не unconditional PR/push step; расписание, явные risk triggers, свежие candidate evidence | QA/SRE |
| G03 | P1 | Lifecycle standard §Mandatory Gates and Monitoring не отделял network refresh от дешёвого `eol check` | Исправлено: committed-state validation в CI; refresh по изменениям inventory и минимум еженедельно | SWE/SRE/QA |
| G04 | P1 | Blueprint §Code Intelligence и implementation-guidelines требуют `SCIP + ast-grep + rg`, graph/chunks и retrieval pipeline для любого репозитория | Реализуется в Guidelines #12: явные basic/indexed modes, profile selection, rationale и миграция; простой поиск/language tooling допустимы без custom pipeline | SWE; QA проверяет эффективность |
| G05 | P1 | `Tools/code-intel/runtime/cli.py`: `build_query_results` ищет подстроки; `run_embeddings` создаёт записи с `embedding: None` | Уточнено в #12: semantic retrieval optional, shared embeddings/query документируют null vectors и substring lookup; внешний provider/eval остаётся отдельной capability, работающий vector search не заявляется | SWE/QA |
| G06 | P2 | Blueprint §Observability и implementation-guidelines требуют logs/metrics/traces и OTLP даже для CLI/library/static web | Реализуется в #12: четыре runtime/risk profiles; OTLP только при выбранном export, library/CLI без автоматического collector/exporter; critical signals/alerts сохраняются | SRE/SWE; BA/PO/UX для client data |
| G07 | P2 | use-cases-standard содержит обязательные Trainer/Client sections; user-flows требует cancellation/payment failure; UX правила исходят из booking/attendance | Убрать предметную область из общего контракта, сохранить её только как подписанный пример; actors и flows выбирать из mission. В этом изменении не переписывались | BA/PO; UX |
| G08 | P2 | Blueprint §Visible Release Traceability и UX Content Rules требуют постоянный commit footer на каждом primary screen | Рассмотреть version/build info в About/support для применимых продуктов вместо универсального footer. Это изменение product/UX policy, поэтому нынешнее правило сохранено | UX/BA/PO; SWE/SRE |
| G09 | P1 | Governance имел batching, но не определял явные trust/action boundaries для issues, logs, retrieved content и external writes | Исправлено: Authority, Trust, and Scope; входные данные не меняют полномочия; локальный прогресс не зависит от неавторизованной внешней записи | Repository Maintainer/SWE |
| G10 | P1 | Governance ограничивал expensive stage «at most one run», что можно прочитать как запрет необходимого повторного запуска | Исправлено: Verification Selection and Evidence разрешает обоснованный rerun и связывает governance с CI policy | QA/SRE |
| G11 | P2 | Governance фиксировал 100M/day, а session_report имеет defaults 5M/session и 100M/day; точная allowance не следует из rollout text estimate | Уточнено: internal configurable estimate, threshold только при доступных данных. Подбор чисел под реальные workloads и качество estimator остаются отдельной задачей | Repository Maintainer |
| G12 | P2 | Governance README заявляет vendor-neutral scope, но `.codex/AGENTS.md` содержит Codex-specific usage и персональный homelab Telegram bot; machine adapter содержит абсолютные host paths | Разделить portable process contract, runtime adapters и personal installation/notification profile. Сейчас разделение ролей двух AGENTS существует: `.codex` — workflow, `codex` — installable pointer; это не две копии одного документа | Repository Maintainer/SRE |
| G13 | P2 | `validate-guidelines.yml` выполняет только OTEL/Sonar tests; AI-Governance `.github/workflows` содержит только release-retention, без test CI | Исправляется в Guidelines #10 и AI-Governance #37: полный быстрый helper suite и отдельный pytest CI, без scanner bundle. Дешёвый suite запускается целиком; impact selection добавлять только при измеренной необходимости. Metadata validation не доказывает семантическую непротиворечивость правил | SWE/QA |
| G14 | P1 | Trivy adapter default `aquasec/trivy:latest`; workflow action refs используют version tags | Pin инструментов/образов и обновление по reviewable change; cache отдельно от version pin. Для reused evidence записывать фактические versions/digests. Runtime defaults здесь не менялись | SWE/SRE |
| G15 | P2 | QA bug checklist требует два воспроизведения; incident closure требует уже verified preventive actions | Для разрушительных/редких сбоев принимать достаточную evidence без повторного воздействия; отделить завершение mitigation от tracked prevention follow-up | QA/SRE |

## Новая модель CI

Нормативный источник:
[`ci-verification-policy.md`](../../guidelines/playbooks/ci-verification-policy.md).

- Обычный PR/push: быстрые применимые lint/type/build/tests/smoke и локальная
  проверка committed config/SBOM. Полные audit/Sonar/Trivy, network EOL refresh,
  полный index rebuild и тяжёлые E2E/performance suites не запускаются по умолчанию.
- Изменение lockfile/dependency/image/IaC/auth/sensitive data: релевантная
  дополнительная проверка по заранее описанному trigger. Нет автоматического
  перехода к `audits.py all`.
- Approved schedule: Sonar и full filesystem/security scans; стартовая частота
  weekly, чаще для повышенного риска. EOL refresh остаётся минимум weekly.
- Релиз: свежая evidence нужного кандидата, gate thresholds, image digest,
  rollback/smoke. Запускать недостающее или инвалидированное; не принимать
  stale/skipped evidence за passed.
- Полный аудит: только явный запрос/утверждённое расписание, один общий отчёт.

Частота weekly — предлагаемая командная политика, не требование Sonar/GitHub.
New-code quality gate не означает, что scanner физически анализирует только diff.

## Внешние источники для проверки выводов

Проверены 2026-10-13; локальные SHA выше остаются источником применённого baseline.

- [GitHub: scan frequency](https://docs.github.com/en/code-security/reference/code-scanning/workflow-configuration-options): event-based checks и scheduled checks решают разные задачи, включая новые findings без source changes. Это обоснование комбинированной модели, не рекомендация отключить targeted security.
- [GitHub: dependency review](https://github.com/actions/dependency-review-action): проверка изменения зависимостей в PR — пример целевого контроля вместо полного scanner bundle. Доступность зависит от конфигурации GitHub; конкретный action не навязывается всем проектам.
- [SonarQube 2026.1: new code](https://docs.sonarsource.com/sonarqube-server/2026.1/user-guide/about-new-code): new-code policy относится к оценке качества изменений; не обещает runtime экономию анализа.
- [GitHub: concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency): можно отменять superseded CI runs; release operations требуют отдельного выбора поведения.
- [OWASP: prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/): внешнее содержимое может влиять на инструкции; trust boundaries и least privilege нужны для agent process.

Приведённые рекомендации о профилях baseline и приоритетах — инженерная оценка
этого репозитория. Источники не доказывают универсальную оптимальность одной
частоты сканов или обязательного/необязательного AST-стека.

## Проверки безопасности и ограничения анализа

| Область | Метод | Статус | Причина / влияние / follow-up |
|---|---|---|---|
| Согласованность Guidelines | mixed | passed | Локальная validation и review затронутых contracts; это не сертификат полного compliance downstream |
| Lifecycle/EOL inventory обоих репозиториев | tool/runner | not-run | Запрос на анализ правил; текущий SBOM/network inventory не проверялся. SRE проводит отдельную проверку при необходимости; security clearance не выдан |
| Trivy filesystem | tool/runner | not-run | Полный scanner audit не входит в локальную правку документации; SWE/SRE запускает при отдельном запросе или применимом gate |
| Trivy image | tool/runner | not-run | Deployable images не собраны и не сканировались; `Tools/code-intel` содержит container runtime. Перед его публикацией SRE проверяет конкретный digest |
| Security rules | AI review | passed | Проверены trust, authorization, evidence reuse и известные supply-chain gaps; отсутствие уязвимостей кода не утверждается |
| GDPR/privacy operational compliance | AI review | not-run | Product data inventory/flows, lawful basis, retention/deletion/DSR, processors/transfers/cookies/consent не представлены. `Evidence not available`; BA/PO/privacy owner рассматривает по конкретному продукту. Юридическая сертификация не выполнялась |
| Tests / metadata | tool/runner | passed | Команды и результаты — ниже |

## Валидация и изменённые файлы

Выполнено 2026-10-13:

- `npm run validate-guidelines` — exit 0; 21 normative files, 77 indexed files,
  39 references, 5 phases.
- `/tmp/guidelines-review-venv/bin/python -m pytest -q` в Guidelines — exit 0,
  **67 passed** (3.86 s).
- Та же команда в AI-Governance — exit 0, **16 passed** (5.49 s).
- `git diff --check` в обоих checkout — exit 0.
- Diff review: частоты согласованы в Blueprint, adoption, QA/SRE/lifecycle и
  runner documentation; normative metadata обновлена, policy и report indexed.

Исходный системный Python не содержал pytest. Тестовые зависимости обоих
репозиториев установлены в изолированный `/tmp/guidelines-review-venv`;
requirements/lockfiles проектов не менялись. Новые тесты, проверяющие лишь
формулировки документации, не добавлялись.

Runtime scanner интеграции и downstream workflows не запускались: меняются правила исполнения,
а не конкретные продуктовые pipelines. Production/deploy evidence отсутствует
и для этого результата не требуется.

Изменены в Guidelines:

- `guidelines/playbooks/ci-verification-policy.md` — новый нормативный policy.
- `Product-Repository-Blueprint.md`, `Adoption-Guide.md`, `README.md` — применение и частоты.
- `Areas/qa/test-strategy.md`, `Areas/sre/sre-operations-guidelines.md`, `Areas/swe/component-lifecycle-guidelines.md` — роли, gates, refresh/check boundaries.
- `Tools/audits/README.md`, `Tools/sonar/README.md`, `Tools/trivy/README.md` — runner cadence.
- `guidelines/playbooks/README.md`, `guidelines-index.yaml`, `CHANGELOG.md` — discoverability, dependencies и версии.
- `docs/reviews/2026-10-13-development-process-review.md` — этот общий анализ.

Изменены в AI-Governance:

- `.codex/AGENTS.md` — authority/trust, verification/evidence и budget interpretation.
- `README.md` — связь с CI policy и описание границ полномочий.

## Порядок дальнейшей модернизации

1. SWE/QA/SRE: применить CI policy к каждому продукту с собственными triggers,
   evidence age, schedule/alert ownership и замерами p50/p95. Текущий Guidelines
   workflow не запускает Sonar/Trivy/full audits; выдуманное удаление scanner jobs
   из него не требуется. Изменения чужих pipelines не выполнены этим review.
2. SWE/QA: определить profiles (docs, library/CLI, service/web, critical system),
   applicability и миграцию code-intel/observability; проверить реальную пользу
   retrieval на задачах и failure cases. BA/PO/UX пересматривают domain leakage
   и footer вместе с product outcomes.
3. Maintainer/SRE: отделить portable governance от personal host/bot adapters,
   закрепить tooling versions и добавить быстрый test CI в AI-Governance.
4. QA/Maintainer: оценивать эффект по feedback time, flaky reruns, escaped
   defects и времени до verified delivery; не по числу документов/агентов/сканов.

## Итоговое решение и handoff

Решение: `conditional` для широкого rollout baseline. Локальные исправления
CI/governance готовы к review; необоснованная универсальность остальных
требований и измерение downstream эффекта остаются follow-up. На момент первоначального review изменения были локальными; machine-wide
инструкции не переустановлены.

Правило AI-Governance о GitHub Issue для каждой задачи конфликтует с отсутствием
авторизации внешних сообщений в текущем runtime. Выполнены доступные локальные
изменения и handoff; Issue/комментарии не создавались. До внешней доставки
Maintainer связывает результат с разрешённым tracking/PR workflow.

Продолжение 2026-10-13: пользователь явно разрешил commit/PR/merge.
Созданы owning-repository work items: [Guidelines #8](https://github.com/vicy07/Guidelines/issues/8)
и [AI-Governance #35](https://github.com/vicy07/AI-Governance/issues/35).
Первоначальное ограничение внешних записей больше не блокирует эту доставку.

Learning capture:

- lesson: наличие scanner integration не задаёт частоту его исполнения;
  evidence reuse требует явной свежести и invalidation.
- system improvement: единый CI policy и согласованные role-owned consumers.
- verification: metadata/reference validation, тесты обоих репозиториев и diff review.


Продолжение G13: `.github/workflows/validate-guidelines.yml` теперь устанавливает
объявленные test dependencies и запускает весь быстрый pytest suite. Новый
`.github/workflows/test.yml` в AI-Governance запускает его test suite. В обоих
workflow: PR + main push, read-only permissions, immutable Action SHAs,
dependency caches, timeout и отмена superseded PR checks. Существующий required
job Guidelines `validate` сохранён. Первые реальные CI результаты подтверждают
дублирование PR/feature-push у прежнего workflow (оба checks для #9); новая
настройка исключает feature-push duplicate. Замеры общего выигрыша пока не сняты.


Продолжение G04/G06 — Guidelines #12: добавлен нормативный
`Areas/requirements/repository-profiles.md`, шаблон adoption и behavioral
checker tests. Product profiles сохраняют восемь документов; basic mode
записывается кратко без custom tooling. Docs-only scope использует README.
Явный indexed mode требует static entrypoint/config/documentation, а generated
indexes остаются runtime outputs. Checker проверяет форму/наличие, не доказывает
классификацию риска, runtime telemetry или retrieval accuracy. Старые lock files
сохраняют прежнюю документную проверку; stronger local controls требуют migration.

Роли текущей фазы Solution Design → Implementation → Verification:
BA/PO — применимость и business risk; SWE — mode/tooling и checker;
QA — behavioral tests и evidence limits; SRE — diagnostic/alert obligations.
Изменение касается baseline, не продуктового поведения; use-case/UX стандарты
не переписывались. Машинные инструкции и downstream проекты не переустановлены.


Валидация G04/G06 (2026-10-13): `npm run validate-guidelines` — exit 0,
22 normative / 78 indexed / 44 references / 5 phases; полный локальный pytest —
**93 passed** (31.91 s), включая **26 новых behavioral cases**;
`node --check scripts/check-product-baseline.mjs` и `git diff --check` — exit 0.
Во время изменения checker найдены и закрыты реальные обходы empty AGENTS/lock
file; регрессионные проверки подтверждают отказ strict mode. Проверка presence
также отвергает directory вместо файла. Runtime indexer/telemetry не менялись,
поэтому scanner, collector и semantic-provider integration tests не запускались.

Файлы продолжения #12: `Areas/requirements/repository-profiles.md`,
`Areas/requirements/code-intelligence-standard.md`, `Areas/requirements/README.md`,
`Areas/swe/architecture-guidelines.md`, `Areas/swe/implementation-guidelines.md`,
`Areas/qa/test-strategy.md`, `Areas/sre/sre-operations-guidelines.md`,
`Product-Repository-Blueprint.md`, `Adoption-Guide.md`, `README.md`, `Repository.md`,
`docs/architecture/code-intelligence.md`, `Tools/code-intel/README.md`,
`Tools/otel/README.md`, `templates/governance-baseline.yaml`,
`scripts/check-product-baseline.mjs`, `tests/test_product_baseline_checker_behavior.py`,
`guidelines-index.yaml`, `CHANGELOG.md` и этот общий отчёт.

Оставшийся риск: выбор профиля и достаточность signals/navigation проверяются
по продуктовой evidence, а не автоматически по расширениям файлов. Downstream
migration и измерение эффективности остаются отдельной delivery. Общий
portable governance/personal-adapter split этим изменением не выполнялся.
