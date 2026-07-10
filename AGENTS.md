# OpenCode Pipeline для @beeline/design-system-react

## Source Of Truth

- Runtime config: `opencode.json`.
- Agent prompts: `.opencode/agents/<slug>.md`.
- Shared rules: `.opencode/rules/01-design-system-first.md`, `.opencode/rules/02-mcp-protocol.md`, `.opencode/rules/03-pipeline-transitions.md`, `.opencode/rules/04-ai-builder-updates.md`.
- State template: `docs/specs/pipeline-state.yaml`.

### Delivery Model

- **Installer / updater:** `install.sh` / `update.sh` (Unix) and `install.cmd` / `update.cmd` (Windows) вызывают **`yellowbe-opencode-pipeline.mjs`** (или через `npx @beeline/yellowbe-opencode-pipeline`).
- **Публикуемый CLI:** bin **`yellowbe-opencode-pipeline`** → `yellowbe-opencode-pipeline.mjs` (реализация в **`cli.mjs`**) — команды `install`, `update`, `diff`, `doctor`, `rollback`, **`check-update`** (сравнение `lock.pipelineVersion` с `dist-tags.latest` в npm Registry), **`safe-update`** (`npx …@latest diff`, затем `update`, если нет конфликтов).
- **Managed files:** `opencode.json`, `.opencode/`, `AGENTS.md`, `docs/specs/pipeline-state.yaml` (см. `pipeline.manifest.json`).
- **Lock:** `docs/specs/opencode-pipeline.lock.json`.
- **Backups:** `.opencode-pipeline/backups/<timestamp>/`.
- **MCP:** безопасный merge только allowlisted серверов из `mcp.json` фрагмента пакета (те же id, что у Roo-пайплайна).
- **Корпоративный TLS (remote MCP):** Node не обязан доверять только OS trust store. Перед запуском OpenCode задайте `NODE_EXTRA_CA_CERTS` на абсолютный путь к `.opencode-pipeline/certs/ca-bundle.pem` (создаётся при `install`; `update` управляемые файлы обновляет, но **не** перезаписывает CA bundle — при необходимости снова выполните `install`). Команды см. в выводе `doctor` и в [README.md](README.md).
- **RooCode customModes:** не синхронизируются этим CLI (ставка `skipped` в отчёте); конфигурация агентов — через проектный `opencode.json`.
- **AI Builder (актуальность доставки):** состояние и политика в `docs/specs/pipeline-state.yaml` → ключ **`ai_builder`**; оркестратор выполняет проверку обновлений только на **границе пользовательского хода** и по правилам в **`04-ai-builder-updates.md`**, не на каждом переходе между stage agents.

OpenCode MVP uses `pipeline-orchestrator` as the default primary agent. All delivery stages are callable worker/subagents; the orchestrator invokes them via `Task` / `@<slug>`, reads `stage_result`, updates `pipeline-state.yaml`, and continues the graph without manual agent switching.

## Agent Set

| Slug | OpenCode mode | Purpose |
|------|---------------|---------|
| `pipeline-orchestrator` | `primary` | Единая точка входа: автоматически запускает stage agents, проверяет артефакты и ведёт `pipeline-state.yaml`. |
| `request-analyst` | `subagent` | Лёгкий входной stage: выбирает `analysis_mode`, `quality_profile`, `design_input`, обновляет pipeline-state и возвращает next stage orchestrator-у. |
| `request-analyst-product` | `subagent` | Product/app аналитика: hub `spec.md` + `spec-chunk-{N}.md`. |
| `request-analyst-marketing` | `subagent` | Marketing/landing аналитика: hub `spec.md` + `spec-chunk-{N}.md`, messaging и матрица в hub. |
| `project-setup` | `subagent` | Инициализация или валидация проекта и подготовка окружения перед следующим этапом пайплайна. |
| `designer` | `subagent` | UI/UX на Beeline DS: hub + `design-spec-chunk-{N}.md`, scratchpad hub/chunk, JSON, DQG. |
| `ui-coder` | `subagent` | React/TS на Beeline DS: hub+chunk артефакты, `implementation-chunk-{N}.md`, код/тесты, build/devtools loop. |
| `ui-tester` | `subagent` | Визуальная и a11y-проверка UI через browser/devtools на 375 / 768 / 1440. |
| `coder` | `subagent` | Бизнес-логика: API, hooks, stores, валидация, замена типизированных UI-заглушек. |
| `reviewer` | `subagent` | Код-ревью: spec compliance, DS compliance, build/type/lint checks, tests и rework routing. |
| `mcp-researcher` | `subagent` | Служебный helper для scoped DS discovery: собирает MCP evidence bundle, пишет research-артефакт и не участвует в основном графе. |
| `tester` | `subagent` | Финальный QA: test plan, unit/component/e2e tests, coverage и bugs report. |


## Handoff Graph

Happy path starts with `pipeline-orchestrator`, which runs the graph below automatically. Rows show logical stage transitions, not manual user switches.

### Визуальная схема (основной поток)

Детальные ветвления и условия — в таблице ниже и в `.opencode/rules/03-pipeline-transitions.md`. Пунктир: helper вне основного графа.

```
┌────────────┐    ┌─────────────────────────────┐
│Пользователь├───►│ 0. Pipeline orchestrator     │
└────────────┘    │    Task / @slug + state      │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ 1. Аналитик-роутер           │
                  │    request-analyst           │
                  └──────────────┬───────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
                   ▼                           ▼
        ┌────────────────────┐      ┌────────────────────┐
        │ 2. Настройка       │      │ сразу к аналитикам │
        │    проекта         │      │ (если проект ОК)   │
        │  project-setup     │      └─────────┬──────────┘
        └─────────┬──────────┘                  │
                  │                           │
                  └─────────────┬───────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
   ┌───────────────────────┐         ┌───────────────────────┐
   │ 1a. Аналитик продукта │         │ 1b. Аналитик лендингов│
   │  → spec.md + chunks   │         │  → spec.md + chunks   │
   └───────────┬───────────┘         └───────────┬───────────┘
               │                                 │
               └────────────────┬────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        ┌────────────────────┐    ┌────────────────────┐
        │ 3. Дизайнер        │    │ обход дизайна      │
        │ → design-spec hub  │    │ (простая задача)   │
        │ + scenarios JSON   │    └──────────┬─────────┘
        │ + scratchpad       │               │
        └─────────┬──────────┘               │
                  │                        │
                  └────────────┬───────────┘
                               ▼
                  ┌──────────────────────────────┐
                  │ 3.5 Orchestrator lock-in     │
                  │ → ui-implementation-brief.md │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ 4. UI Coder                  │
                  │   → src/ + tests             │
                  │   → implementation-chunk-*   │◄──── browser / devtools
                  └──────────────┬─────────────┘      (итеративно, max 3)
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
            ┌─────────────┐           ┌─────────────┐
            │ UI Tester   │           │ 5. Coder    │
            │ (по профилю │           │  (логика)    │
            │  качества)  │           └──────┬──────┘
            └──────┬──────┘                  │
                   │                         │
                   └────────────┬────────────┘
                                ▼
                  ┌──────────────────────────────┐
                  │ 6. Reviewer                  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ 7. Тестировщик               │
                  │   → test report              │
                  └──────────────────────────────┘

  designer / ui-coder / reviewer ···► mcp-researcher  (helper DS bundle, не stage графа)
```

### Обратные связи (кратко)

```
UI Tester    ──(вердикт rejected, max 3)──► UI Coder
Reviewer     ──(rejected, max 3)──────────► Designer / UI Coder / Coder
Tester       ──(critical bugs, max 2)────► request-analyst
Designer     ──(уточнение spec)──────────► request-analyst
UI Coder     ──(проблема design-spec)────► Designer
```

| From | To | Condition |
|------|----|-----------|
| `request-analyst` | `project-setup` | project is not initialized and `analysis_mode` is known |
| `request-analyst` | `request-analyst-product` | product/app track selected |
| `request-analyst` | `request-analyst-marketing` | marketing/landing track selected |
| `project-setup` | `request-analyst-product` / `request-analyst-marketing` / `request-analyst` | project ready, route by `analysis_mode` and existing artifacts |
| `request-analyst-product` | `designer` / `pipeline-orchestrator` | spec hub + `spec-chunk-*` ready (или legacy монолит), depending on design need |
| `request-analyst-marketing` | `designer` / `pipeline-orchestrator` | spec hub + `spec-chunk-*` ready (или legacy), depending on design need |
| `designer` | `pipeline-orchestrator` | design hub + `design-spec-chunk-*`, JSON, scratchpad hub/chunk ready, DQG passed (legacy: монолит) |
| `pipeline-orchestrator` | `ui-coder` | UI intent lock-in пройден, `docs/specs/ui-implementation-brief.md` актуален |
| `pipeline-orchestrator` | `designer` / `request-analyst-*` | lock-in провален: конфликт артефактов или не заполнены обязательные секции brief |
| `ui-coder` | `ui-tester` / `reviewer` / `designer` / `coder` | implementation complete, profile visual gate needed, design issue, or business logic needed |
| `ui-tester` | `coder` / `reviewer` / `ui-coder` | visual approval or rejection loop |
| `coder` | `reviewer` / `ui-coder` | logic complete or UI adjustment needed |
| `reviewer` | `tester` / `designer` / `ui-coder` / `coder` | approved or rework routed by issue type |
| `tester` | done / `request-analyst` | passed or critical bugs found |


## Data Contracts

| Artifact | Created By | Consumed By | Notes |
|----------|------------|-------------|-------|
| `docs/specs/pipeline-state.yaml` | `pipeline-orchestrator` + all stage agents | all agents | request id, analysis mode, quality profile, design input, risk acceptance, active/next stage, last stage result, chunk, iteration counters, blockers |
| `docs/specs/spec.md` | `request-analyst-product`, `request-analyst-marketing` | `designer`, `ui-coder`, `tester` | hub: мета, контекст, индекс chunks |
| `docs/specs/spec-chunk-{N}.md` | `request-analyst-product`, `request-analyst-marketing` | `designer`, `ui-coder`, `tester` | экраны и chunk-scoped tasks |
| `docs/specs/design-spec.md` | `designer` | `ui-coder`, `reviewer` | hub: оглавление chunk-файлов, сводка ds_gaps |
| `docs/specs/design-spec-chunk-{N}.md` | `designer` | `ui-coder`, `reviewer` | Phase R/S/V, DQG, wireframes, mapping, UI Coder handoff |
| `docs/specs/user-scenarios.json` | `designer` | `ui-coder`, `tester` | machine-readable scenarios, minimum 3 per task |
| `docs/specs/design-scratchpad.md` | `designer` | `ui-coder`, `reviewer` | hub: индекс, task-level риски |
| `docs/specs/design-scratchpad-chunk-{N}.md` | `designer` | `ui-coder`, `reviewer` | rationales, матрица, решения по chunk |
| `docs/specs/ui-implementation-brief.md` | `pipeline-orchestrator` | `ui-coder`, `reviewer` | канонический lock-in артефакт перед реализацией UI; фиксирует интегральный intent и source_map |
| `docs/specs/implementation-chunk-{N}.md` | `ui-coder` | `reviewer`, `tester` | DS registry, отклонения, self-check, coverage (канонический отчёт по chunk) |
| `docs/specs/mcp-research/*.md` | `mcp-researcher` | `designer`, `ui-coder`, `reviewer` | scoped DS evidence bundle; не handoff и не chunk-processing artifact |

## Profile-Aware Routing Contract

`pipeline-orchestrator` treats `analysis_mode`, `quality_profile` and `design_input` as three independent decisions:

| Field | Values | Purpose |
|-------|--------|---------|
| `analysis_mode` | `product` / `marketing` | Which specialized analyst creates `spec.md` and chunks. |
| `quality_profile` | `lean` / `product` / `hardened` | How deep visual QA, review and tests must be. |
| `design_input` | `generative` / `reference_static` / `structured_mcp` | How designer uses or formalizes source design. |

Policy summary:

- `lean`: build/typecheck and focused smoke are allowed, but UI surfaces still need visual smoke for the key screen/CTA/form.
- `product`: keep the normal `reviewer` → `tester` tail; require unit/component tests for changed behavior.
- `hardened`: do not shorten `ui-tester`, `reviewer` or `tester`; require e2e happy+negative, error/recovery/focus states and explicit `risk_acceptance` for any downgrade.
- `reference_static`: designer may use a shortened formalization path, but must preserve reference fidelity checklist and DS mapping.
- `structured_mcp`: MCP/frame evidence must be recorded; partial/blocked MCP requires explicit `design_input_fallback`, not silent generative redesign.
- Если есть UI surface, перед `ui-coder` всегда обязателен orchestrator lock-in: проверка входных артефактов + обновление `docs/specs/ui-implementation-brief.md`.
- Если `designer` был пропущен, orchestrator всё равно обязан заполнить brief; при нехватке оснований перехода к `ui-coder` — re-route в `request-analyst-*` (или `designer`) вместо «кодить по сырым chunk-данным».

## OpenCode Differences From RooCode

- `customModes` became OpenCode `agent` entries and `.opencode/agents/*.md` files.
- RooCode `groups` became OpenCode `permission` rules in `opencode.json`: операции, которые раньше были `ask`, выставлены в `allow`, чтобы не блокировать поток подтверждениями; у оркестратора и shell-capable stages по-прежнему `deny` на `git push*` и `rm *`, у аналитиков/дизайнера/mcp-researcher — без произвольного `bash`/`Task` (как в графе пайплайна).
- RooCode `modeApiConfigs` is not copied. Use OpenCode global `model`, provider config, or per-agent `model` overrides.
- RooCode `switch_mode` became OpenCode-native orchestration: `pipeline-orchestrator` invokes worker stage agents via `Task` / `@<slug>`. The explicit handoff line `Переключись на OpenCode agent <slug>` is now fallback / audit trail, not the primary UX.
- RooCode `new_task` / `attempt_completion` became OpenCode `Task` / `@mcp-researcher` helper invocation and short subagent result for scoped DS evidence only.

## Disabled Reference

`design-verifier` is not an active agent in this port. Keep `.opencode/rules/design-verifier-disabled-reference.md` only as reference for a future DVG re-enable.
