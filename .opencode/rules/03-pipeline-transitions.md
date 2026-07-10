# Протокол переходов OpenCode Pipeline

> OpenCode не использует RooCode `switch_mode`. В MVP happy path управляется `pipeline-orchestrator`: он вызывает stage agents через `Task` / `@<slug>`, проверяет артефакты, обновляет `pipeline-state.yaml` и сам выбирает следующий этап. Текстовая строка `Переключись на OpenCode agent <slug>` остаётся как audit/fallback, но не требует ручного действия пользователя. Служебный `mcp-researcher` вызывается через `Task` / `@mcp-researcher` и не является основным этапом графа.

Этот документ фиксирует все переходы между этапами конвейера, условия переключения, формат передачи данных и правила обратной связи.

## Схема пайплайна

```
Пользователь
    │
    ▼
┌────────────────────────┐
│ pipeline-orchestrator  │  default_agent; автоматический запуск stage agents
└───────────┬────────────┘
            │ Task / @request-analyst
            ▼
┌──────────────────────┐
│  request-analyst     │  Вход: сырое ТЗ / bugs / уточнения
│  → analysis/profile  │  Выход: routing + pipeline-state
└──────┬───────────────┘
       │
       ├─── проект не готов ──► ┌─────────────────┐
       │                        │  project-setup   │
       │                        └────────┬────────┘
       │                                 │
       ├── analysis_mode=product ────────┤
       │                                 ▼
       │                     ┌────────────────────────────┐
       │                     │ request-analyst-product    │
       │                     │ → spec.md hub + spec-chunk-* │
       │                     └────────────┬───────────────┘
       │                                  │
       └── analysis_mode=marketing ───────┤
                                          ▼
                            ┌────────────────────────────┐
                            │ request-analyst-marketing  │
                            │ → spec.md hub + spec-chunk-* │
                            └────────────┬───────────────┘
                                         │
                                         ▼
                            ┌──────────────────────┐
                            │  designer            │  Вход: spec hub + spec-chunk-*
                            │  → design-spec hub   │  Выход: design-spec.md hub +
                            │  + design-spec-chunk │    design-spec-chunk-* +
                            │                      │    user-scenarios.json +
                            │                      │    scratchpad hub + chunk
                            └──────────┬───────────┘
                                       │
                                       ▼
                  ┌────────────────────────────────────┐
                  │ pipeline-orchestrator              │
                  │ UI intent lock-in gate             │
                  │ → docs/specs/ui-implementation-brief.md
                  └──────────┬─────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  ui-coder            │  Вход: ui-implementation-brief + design/spec hub/chunk
                  │                      │  (после lock-in; без design-verifier)
                  │  → src/ + tests      │  Выход: src/ + tests + implementation-chunk-*
                  │  + chrome-devtools   │  Итеративно: код→тест→fix (max 3)
                  └──────────┬───────────┘
                             │
                     ┌───────┴───────┐
                     ▼               ▼
              ┌────────────┐  ┌───────────┐
              │ ui-tester  │  │  coder    │  (если нужна бизнес-логика)
              │ profile-gate│  └─────┬─────┘
              └─────┬──────┘        │
                    └───────┬───────┘
                            ▼
                  ┌──────────────────────┐
                  │  reviewer            │  DS-compliance, React patterns,
                  │                      │  coverage > 80%
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  tester              │  Vitest + RTL + Playwright
                  │  → test report       │  Coverage > 80%
                  └──────────┬───────────┘
                             │
                             ▼
                        ✅ ЗАВЕРШЕНО
```

**Внутри agent-а `pipeline-orchestrator`:** это единственная happy-path точка входа. Он запускает `request-analyst` и следующие stage agents через `Task` / `@<slug>`, проверяет `stage_result`, обновляет orchestrator-поля в `pipeline-state` и продолжает граф без ручного переключения OpenCode agent-а. Подробности: `.opencode/agents/pipeline-orchestrator.md`.

**Внутри agent-а `request-analyst`:** это лёгкий роутер. Он определяет `analysis_mode` (`product` / `marketing`), начальный `quality_profile` (`lean` / `product` / `hardened`) и `design_input` (`generative` / `reference_static` / `structured_mcp`), обновляет `pipeline-state` и возвращает orchestrator-у следующий stage: либо `project-setup`, либо нужный специализированный аналитический agent. Подробности: `.opencode/agents/request-analyst.md`.

**Внутри agent-а `request-analyst-product`:** фазы **A → D HQG**; после HQG — hub **`docs/specs/spec.md`** и **`docs/specs/spec-chunk-{N}.md`** на каждый chunk. Подробности: `.opencode/agents/request-analyst-product.md`.

**Внутри agent-а `request-analyst-marketing`:** тот же цикл; hub + per-chunk spec-файлы; матрица контента в hub. Подробности: `.opencode/agents/request-analyst-marketing.md`.

**Внутри agent-а `designer`:** по chunk — **R → S → V (DQG)**; пишет **`docs/specs/design-spec-chunk-{N}.md`**, поддерживает hub **`design-spec.md`**; **`user-scenarios.json`**; hub **`design-scratchpad.md`** + **`design-scratchpad-chunk-{N}.md`**. Handoff **`### UI Coder — краткий handoff`** в chunk-файле. Legacy: монолитные spec/design без `*-chunk-*`. Подробности: `.opencode/agents/designer.md`.

**Reference `design-verifier`:** временно **не** включён в `opencode.json` (экономия токенов). Чеклист **DVG** и прежний поток остаются в `.opencode/rules/design-verifier-disabled-reference.md` как справочник для возможного повторного включения.

**Helper `mcp-researcher`:** служебный on-demand helper, а не отдельный шаг графа. Его вызывают `designer`, `ui-coder` и `reviewer` через `Task / @mcp-researcher`, когда нужен пакетный DS research bundle; `pipeline-orchestrator` может вызвать его только для диагностики blocked MCP / DS bundle. Helper пишет `docs/specs/mcp-research/*.md`, может обновить helper-поля в `pipeline-state`, завершает работу через короткий subagent result, но не заменяет основной handoff и не обрабатывает chunks вместо stage agents. Если helper вернул `partial` / `blocked`, основной agent не должен трактовать такой bundle как готовый к коду без повторного helper-вызова или явного controlled fallback.

## Таблица переходов

| Из | В | Условие | Артефакт передачи |
|----|---|---------|-------------------|
| pipeline-orchestrator | request-analyst | Новая пользовательская задача, bugs re-entry или explicit resume без активного stage | User brief + `pipeline-state.yaml` |
| request-analyst | project-setup | Проект не инициализирован; `analysis_mode` уже определён | `pipeline-state.yaml` |
| request-analyst | request-analyst-product | Выбран трек `product` | `pipeline-state.yaml` |
| request-analyst | request-analyst-marketing | Выбран трек `marketing` | `pipeline-state.yaml` |
| project-setup | request-analyst-product | Проект готов, `analysis_mode: product`, spec.md ещё нет | `pipeline-state.yaml` |
| project-setup | request-analyst-marketing | Проект готов, `analysis_mode: marketing`, spec.md ещё нет | `pipeline-state.yaml` |
| project-setup | request-analyst | Проект готов, `analysis_mode` ещё не определён | `pipeline-state.yaml` |
| project-setup | designer | Проект готов, `spec.md` уже есть, но `design-spec.md` ещё нет | `spec.md` |
| project-setup | pipeline-orchestrator | Проект готов, дальше нужен выбор по готовности spec/design и lock-in gate | `pipeline-state.yaml` + найденные артефакты |
| request-analyst-product | designer | spec hub + `spec-chunk-*` готовы, задача с UI-дизайном | `spec.md` + `spec-chunk-*.md` (обзор design_task в hub) |
| request-analyst-product | pipeline-orchestrator | spec готов; orchestrator решает: `designer` или lock-in перед `ui-coder` | `spec.md` + `spec-chunk-*.md` |
| request-analyst-marketing | designer | spec hub + chunk-файлы готовы, задача с UI-дизайном | `spec.md` + `spec-chunk-*.md` |
| request-analyst-marketing | pipeline-orchestrator | spec готов; orchestrator решает: `designer` или lock-in перед `ui-coder` | `spec.md` + `spec-chunk-*.md` |
| designer | pipeline-orchestrator | hub `design-spec.md`, `design-spec-chunk-*`, `user-scenarios.json`, scratchpad hub + `design-scratchpad-chunk-*`, **DQG** пройден | design hub/chunk + JSON + scratchpad hub/chunk + spec hub/chunk; legacy — монолиты |
| pipeline-orchestrator | ui-coder | UI surface есть, lock-in пройден: `ui-implementation-brief.md` существует и заполнены обязательные секции | `ui-implementation-brief.md` + spec/design artifacts + `pipeline-state.yaml` |
| pipeline-orchestrator | designer | lock-in провален из-за пробелов/конфликтов в дизайн-решениях | `pipeline-state.yaml` + conflict notes |
| pipeline-orchestrator | request-analyst-product / request-analyst-marketing | lock-in провален из-за конфликтов или недостатка требований в spec | `pipeline-state.yaml` + conflict notes |
| designer | request-analyst | Нужно уточнение по spec.md или переанализ | Вопросы |
| ui-coder | ui-tester | Chunk реализован, self-check пройден, UI surface требует visual smoke/profile gate (`quality_profile: lean` с UI, `product` visual-heavy, всегда `hardened`) | Код в `src/` + **`docs/specs/implementation-chunk-{N}.md`** + dev server URL / route |
| ui-coder | reviewer | Chunk реализован, self-check пройден, build/type/lint/test checks OK, visual gate не нужен или уже пройден | Код в `src/` + **`docs/specs/implementation-chunk-{N}.md`** (тот же контент, что Implementation Report) + при необходимости сверка с `user-scenarios.json` |
| ui-coder | designer | Проблема в design-spec.md | Описание проблемы |
| ui-coder | coder | Нужна бизнес-логика | Типизированные заглушки |
| ui-tester | coder | approved, но в `spec.md`/коде ещё остались типизированные logic stubs или явно нужен logic handoff | `ui_test_result` + заметка о незавершённой логике |
| ui-tester | reviewer | approved, UI готов и отдельный logic handoff не нужен | `ui_test_result` |
| ui-tester | ui-coder | rejected, iteration < 3 | Issues list |
| coder | reviewer | Все заглушки заменены, build/type/lint checks OK | Код |
| reviewer | tester | approved | `review_result` |
| reviewer | designer | rejected, проблемы дизайна | Issues + `rework_assignments` |
| reviewer | ui-coder | rejected, проблемы вёрстки/DS | Issues + `rework_assignments` |
| reviewer | coder | rejected, проблемы логики | Issues + `rework_assignments` |
| tester | (завершено) | passed | `test_report` |
| tester | request-analyst | failed + critical bugs, `iteration_critical_bug_reentry < 2` | `bugs_found` |

## Формат handoff (передачи данных)

В orchestrated MVP текущий stage-agent не требует от пользователя ручного переключения. Он обязан завершить артефакт, вернуть `stage_result`, а `pipeline-orchestrator` решает следующий запуск. Для debug/fallback stage-agent может дополнительно оставить старую строку `Переключись на OpenCode agent <slug>`.

При handoff на следующий OpenCode stage текущий stage-agent обязан:

1. Завершить свой артефакт (routing / spec hub + `spec-chunk-*` / design hub + `design-spec-chunk-*` / scratchpad hub+chunk / `implementation-chunk-*` / `src/`).
2. Обновить **`docs/specs/pipeline-state.yaml`** (или `.json` с теми же полями): актуализировать `last_mode`, `analysis_mode`, при смене chunk — `current_chunk`, при циклах обратной связи — `iteration_ui` / `iteration_review` (и при необходимости `iteration_design_verify`), при блокировках — `blockers`.
3. Вернуть orchestrator-у короткий `stage_result`:

```yaml
stage_result:
  status: done | blocked | needs_user | rejected
  stage: "<slug>"
  artifact_paths:
    - docs/specs/...
  next_agent: "<slug>" | done | null
  blockers: []
  quality_gate:
    name: string
    passed: boolean
  ui_intent_lock:
    required: boolean
    status: pending | locked | not_applicable
    artifact_path: docs/specs/ui-implementation-brief.md | ""
    files_read: string[]
    conflicts: []
  policy:
    analysis_mode: product | marketing | null
    quality_profile: lean | product | hardened | null
    design_input: generative | reference_static | structured_mcp | null
    risk_acceptance_required: boolean
  summary: string
```

Для перехода в `ui-coder` при UI surface обязательно `ui_intent_lock.status: locked`.

Если `designer` пропущен, orchestrator всё равно обязан:
- заполнить `docs/specs/ui-implementation-brief.md` на основе `spec.md` + `spec-chunk-*`;
- отметить в `ui_intent_lock.conflicts` и/или notes, какие assumptions приняты из-за отсутствия design-артефактов;
- при недостатке данных вернуть маршрут в `request-analyst-*` (или `designer`), а не запускать `ui-coder` по сырым chunk-файлам.

4. Опционально указать fallback-инструкцию: **«Переключись на OpenCode agent {slug}»**. Orchestrator может извлечь из неё `next_agent`, если старый stage-agent ещё не вернул structured result.
5. Кратко пояснить причину перехода и статус артефакта.

### Поля `pipeline-state` (контракт)

| Поле | Назначение |
|------|------------|
| `request_id` | ID задачи, как в Мета `spec.md` |
| `analysis_mode` | Какой специализированный аналитик должен продолжать работу: `product` или `marketing` |
| `quality_profile` | Глубина инженерной проверки: `lean`, `product` или `hardened`; влияет на visual QA, reviewer и tester |
| `design_input` | Источник дизайна: `generative`, `reference_static` или `structured_mcp`; влияет на режим работы designer и допустимость прямого перехода к ui-coder |
| `design_input_artifacts` | Список путей/ссылок на скрины, PDF, Pixso/MCP frames и покрытие breakpoints/flow |
| `design_input_fallback` | Явный fallback источника дизайна с причиной, если structured MCP или reference неполны |
| `risk_acceptance` | Явное принятие риска человеком: downgrade профиля или принятие результата после лимита итераций |
| `current_chunk` | Номер активного chunk (1-based) или `null` |
| `iteration_ui` | Счётчик итераций ui-tester → ui-coder при `rejected` (0…3) |
| `iteration_review` | Счётчик итераций reviewer → исполнители при `rejected` (0…3) |
| `iteration_design_verify` | Зарезервировано под цикл design-verifier → designer (0…3); при отключённом agent-е обычно не инкрементируется |
| `iteration_critical_bug_reentry` | Счётчик возвратов tester → request-analyst при critical bugs (0…2) |
| `last_mode` | Slug последнего agent-а |
| `orchestrator_status` | `idle`, `running`, `blocked` или `done` — состояние автоматического controller-а |
| `active_stage` | Stage, который orchestrator сейчас запустил или проверяет |
| `next_agent` | Следующий stage, выбранный orchestrator-ом; `done` означает завершение |
| `last_stage_result` | Краткий результат последнего stage для восстановления контекста |
| `canonical_artifacts.ui_implementation_brief` | Канонический путь lock-in артефакта (`docs/specs/ui-implementation-brief.md`) |
| `ui_intent_lock.status` | Статус lock-in: `pending`, `locked` или `not_applicable` |
| `ui_intent_lock.files_read` | Какие файлы orchestrator прочитал перед решением о запуске `ui-coder` |
| `ui_intent_lock.conflict_resolution_notes` | Как разрешены конфликты между spec/design/scratchpad |
| `last_helper_mode` | Последний helper-agent, вызванный через `Task / @mcp-researcher` (`mcp-researcher` или пусто) |
| `latest_mcp_research_artifact` | Путь к последнему актуальному `docs/specs/mcp-research/*.md` |
| `blockers` | Список строк — что мешает продолжить (пусто = нет) |

### Политика `quality_profile`

| Профиль | Минимум | Сокращения | Нельзя сокращать |
|---------|---------|------------|------------------|
| `lean` | build/typecheck, sanity CTA/form, один visual smoke для UI surface | полный регресс, расширенный e2e | DS compliance, первый экран/CTA, явные ошибки форм |
| `product` | unit/component tests, RTL для изменённого поведения, reviewer → tester | полный e2e на все edge cases | основные состояния UI, ошибки/API, acceptance criteria |
| `hardened` | visual QA на 375/768/1440, e2e happy+negative, recovery/error/focus, regression | почти ничего без human sign-off | ui-tester, reviewer, tester, negative/recovery checks |

Если задача содержит платежи, KYC, договоры, роли/доступы, персональные данные или юридически значимое действие, `quality_profile` должен быть `hardened`, либо в `risk_acceptance.profile_downgrade` должна быть явная причина и `approved_by`.

### Политика `design_input`

| Источник | Поведение |
|----------|-----------|
| `generative` | `designer` выполняет полный R→S→V цикл: DS mapping, wireframes, states, DQG |
| `reference_static` | `designer` формализует референс: фиксирует эталоны, fidelity checklist, DS mapping и допущения; творческий цикл можно сократить, но не убрать mapping |
| `structured_mcp` | Сначала MCP evidence / imported frames; `designer` делает быстрый skeleton + DS mapping. Если MCP неполон — заполнить `design_input_fallback`, `blockers` / `risks`, не превращать молча в `generative` |

### Пример handoff (Роутер → Аналитик лендингов)

```
## Результат маршрутизации

Трек анализа определён: `marketing`
Состояние пайплайна обновлено: `docs/specs/pipeline-state.yaml` (`analysis_mode`, `last_mode`, blockers)

Причина выбора:
- один conversion-focused surface
- в запросе акцент на hero / CTA / proof

**→ Переключись на OpenCode agent request-analyst-marketing**
```

### Пример handoff (Аналитик → Дизайнер)

```
## Результат анализа

Спецификация готова: `docs/specs/spec.md` (hub) + `docs/specs/spec-chunk-1.md`, `spec-chunk-2.md`
Состояние пайплайна обновлено: `docs/specs/pipeline-state.yaml` (`request_id`, `analysis_mode`, `current_chunk`, счётчики и т.д.)

Содержит:
- 3 экрана в 2 chunks (детали в chunk-файлах)
- design_task / frontend_task: обзор в hub, детали по chunk в `spec-chunk-*`

**→ Переключись на OpenCode agent designer**
Spec.md полный, задача требует проектирования UI.
```

### Пример handoff (Дизайнер → UI Coder)

```
## Результат дизайна

Design-spec hub: `docs/specs/design-spec.md`; chunk: `docs/specs/design-spec-chunk-1.md`
Сценарии: `docs/specs/user-scenarios.json`
Scratchpad: `docs/specs/design-scratchpad.md` + `docs/specs/design-scratchpad-chunk-1.md`

Chunk 1 обработан (внутри agent-а: Phase R → Phase S → Phase V):
- Phase R/S/V записаны в **`design-spec-chunk-1.md`** ✅
- user-scenarios.json: минимум 3 сценария на задачу ✅
- scratchpad chunk + hub актуальны ✅
- DQG V1–V9 в **`design-spec-chunk-1.md`** ✅
- **UI Coder — краткий handoff** в конце **`design-spec-chunk-1.md`** ✅
- Для `marketing` / `landing`: primary conversion, critical proof blocks и AIDA переданы в handoff ✅
- Component mapping: 8 DS-компонентов ✅
- Строка Page layout (контейнер / max-width) в mapping ✅
- Wireframes: 3 breakpoints ✅
- Nielsen score: 4.2/5.0 ✅
- DS gaps: 0

**→ Переключись на OpenCode agent ui-coder**
DQG пройден, дизайн готов к реализации Chunk 1 (отдельный agent design-verifier в пайплайне отключён).
```

### Пример helper-brief (UI Coder → MCP Researcher)

Это **не** handoff по основному графу, а служебный helper-вызов через `Task / @mcp-researcher`:

```yaml
consumer: ui-coder
scope: "Chunk 1 DS bundle for billing form"
request_id: TASK-2026-042
chunk: 1
analysis_mode: product
surface_type: app
questions_to_answer:
  - "Какие ключевые props у TextField, Select и InlineAlert нужны для текущего chunk?"
  - "Есть ли nested API или guideline caveats, которые важно учесть до JSX?"
required_components:
  - TextField
  - Select
  - InlineAlert
required_outputs:
  - component_name
  - import_path
  - nested
  - key_props
  - guidelines
artifact_hint: "docs/specs/mcp-research/chunk-1-ui-coder.md"
reuse_existing_artifact: true
```

### Пример возврата helper-а

```markdown
## MCP Research Result

- artifact_path: `docs/specs/mcp-research/chunk-1-ui-coder.md`
- coverage_status: ready
- components_checked: 3
- gaps: 0

Ключевые выводы:
- `TextField` и `Select` подтверждены для chunk
- спорных nested API нет
- для `InlineAlert` зафиксированы key props и guideline caveats
```

### Пример handoff (UI Coder → Reviewer)

```
## Результат реализации Chunk 1

Код и тесты в `src/`, build OK.

Implementation Report: `docs/specs/implementation-chunk-1.md` (или путь в проекте)
- DS Usage Registry — заполнен
- Отклонения от design-spec — нет (или таблица с причинами)
- Self-check: layout checklist ✅, grep цветов ✅
- Для `marketing` / `landing`: primary conversion, proof / CTA hierarchy, reading order и desktop composition check зафиксированы ✅

**→ Переключись на OpenCode agent reviewer**
```

## Обратные связи (Feedback Loops)

### Цикл 1: UI Тестировщик → UI Coder

| Параметр | Значение |
|----------|---------|
| Триггер | verdict == "rejected" |
| Макс. итераций | 3 |
| Передаваемые данные | Issues list (critical, major, minor) + DS compliance |
| Эскалация | После 3-й итерации → уведомление пользователя |

### Цикл 2: Reviewer → Designer / UI Coder / Coder

| Параметр | Значение |
|----------|---------|
| Триггер | verdict == "rejected" |
| Макс. итераций | 3 |
| Маршрутизация | По типу issues (дизайн / вёрстка / логика) |
| Передаваемые данные | Issues + rework_assignments |
| Эскалация | После 3-й итерации → уведомление пользователя |

### Цикл 2a (опционально): Design Verifier → Designer

| Параметр | Значение |
|----------|----------|
| Статус | Только если agent `design-verifier` снова включён в `opencode.json` |
| Триггер | verdict == "rejected" |
| Макс. итераций | 3 (`iteration_design_verify`) |
| Передаваемые данные | Issues из `design-verification.md` |
| Эскалация | После 3-й итерации → уведомление пользователю + `blockers` |

### Цикл 3: Тестировщик → Аналитика

| Параметр | Значение |
|----------|---------|
| Триггер | verdict == "failed" + critical bugs |
| Макс. итераций | 2 |
| Передаваемые данные | bugs_found |
| Эскалация | После 2-й итерации → уведомление пользователя |

## Правила эскалации

1. Каждый цикл обновляет соответствующий счётчик в `docs/specs/pipeline-state.yaml`: `iteration_ui`, `iteration_review` или `iteration_design_verify`.
2. При достижении максимума итераций — выход из цикла, уведомление пользователя.
3. Уведомление содержит: историю итераций, нерешённые проблемы, рекомендации.
4. Пользователь решает: продолжить, изменить требования или принять текущий результат.
5. Для `quality_profile: hardened` принятие результата после лимита итераций допустимо только при `risk_acceptance.result_after_iteration_limit: true`, непустых `reason` и `approved_by`.

## Общие правила для всех агентов

- Язык ответа: русский
- Каждый stage-agent завершает ответ `stage_result`; явное указание следующего agent-а в тексте допустимо только как fallback / audit trail
- Артефакты записываются в файлы через OpenCode edit/write tools, не только в чат
- Chunk-by-chunk: обрабатывать по 1-2 экрана за итерацию (лимит контекста Qwen3)
- Если агент не может выполнить задачу — уведомить пользователя с объяснением
