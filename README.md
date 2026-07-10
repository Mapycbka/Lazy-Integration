# Lazy Integration

Утилита для автоматизации формирования конфигурационного файла интегрируемой базовой станции Huawei. Считывает данные из Design Input (ДИ) и Transport Sheet (ТС), строит GSM/LTE-сущности по бизнес-правилам и записывает их в копию шаблона, не изменяя оригинал.

> **EN** — Desktop utility that automates generation of a Huawei base-station configuration workbook. Reads Design Input (DI) and Transport Sheet (TS), derives GSM/LTE entities by business rules, and writes them into a copy of the template, leaving the original untouched.

---

## Содержание / Table of contents

- [Назначение / Purpose](#назначение--purpose)
- [Быстрый старт / Quick start](#быстрый-старт--quick-start)
- [Интерфейс / Interface](#интерфейс--interface)
- [Входные данные / Input files](#входные-данные--input-files)
- [Как работает генерация / Generation pipeline](#как-работает-генерация--generation-pipeline)
- [Бизнес-правила / Business rules](#бизнес-правила--business-rules)
- [Транспортные параметры / Transport parameters](#транспортные-параметры--transport-parameters)
- [Диалог выбора плат/портов / Board & port dialog](#диалог-выбора-платпортов--board--port-dialog)
- [Устойчивость к названиям / Alias tolerance](#устойчивость-к-названиям--alias-tolerance)
- [Работа с шаблоном / Template handling](#работа-с-шаблоном--template-handling)
- [Запуск из исходников / Run from source](#запуск-из-исходников--run-from-source)
- [Сборка exe / Build exe](#сборка-exe--build-exe)
- [Структура проекта / Project structure](#структура-проекта--project-structure)
- [Зависимости / Dependencies](#зависимости--dependencies)
- [Логи / Logs](#логи--logs)
- [Примечание о посторонних файлах / Note on unrelated files](#примечание-о-посторонних-файлах--note-on-unrelated-files)

---

## Назначение / Purpose

При интеграции новой базовой станции инженер получает два Excel-файла:

- **ДИ** — Design Input: параметры 2G и 4G секторов, имена RRU, диапазоны, TxRx-режимы.
- **ТС** — Transport Sheet: IP-адреса, VLAN и шлюзы для транспортных интерфейсов.

На основе этих данных нужно заполнить конфигурационный шаблон Huawei — Excel-книгу с 11 листами, где каждый лист имеет строго определённый набор колонок. Заполнение вручную занимает значительное время и сопровождается ошибками. Lazy Integration автоматизирует этот процесс.

> **EN** — On integration, an engineer receives two Excel files: the Design Input (2G/4G sector parameters, RRU names, bands, TxRx modes) and the Transport Sheet (IP/VLAN/gateways). These must be mapped onto an 11-sheet Huawei configuration template with fixed columns per sheet. Lazy Integration automates that mapping.

---

## Быстрый старт / Quick start

1. Запустите `Lazy Integration.exe` (собранный билд) или `run_windows.bat` / `run_macos.command` из исходников.
2. Нажмите **«Загрузить файл ДИ»** и выберите Excel-книгу с листами `2G_BTS_Data` и `4G_Data`. После выбора автоматически определится **BSC**.
3. (Опционально) нажмите **«Загрузить файл ТС»** и выберите книгу с листом `ip-план`. Либо отметьте **«Пропустить загрузку ТС-параметрики»** — тогда транспортные IP/VLAN останутся пустыми.
4. Заполните **«Параметры формирования»**: тип площадки, регион, тип BBU (шаблон подставится автоматически), при необходимости — версии ПО BTS/BSC, номер слота платы, порты платы, порт транспортной платы.
5. Нажмите **«Сформировать файл»**. Если в ДИ более одной LTE-цепочки — откроется диалог выбора платы/порта для каждой цепочки.
6. После сообщения «Формирование завершено» нажмите **«Сохранить результат»** и выберите папку.

> **EN** — Launch the app, load the DI file (BSC is detected automatically), optionally load the TS file or tick "skip TS", fill in the form parameters (slot/ports formats like `1-2`, `0,1,2`), press **Generate**, then **Save result**. If several LTE chains exist, a board/port dialog appears.

---

## Интерфейс / Interface

Главное окно (`gui/main_window.py`) состоит из шести секций.

### 1. Файлы / Files

| Элемент | Описание / Description |
|---------|------------------------|
| Загрузить файл ДИ | Excel-книга с листами `2G_BTS_Data` и `4G_Data` (плюс `Конфигурация сайта`) |
| Загрузить файл ТС | Excel-книга с листом `ip-план` (можно пропустить) |
| Пропустить загрузку ТС-параметрики | Генерация только по ДИ; транспортные поля остаются пустыми |

После выбора ДИ приложение автоматически проверяет структуру и извлекает имя BSC.

### 2. Интегрируемая станция / Integrated station

Отображается **BSC NAME** — имя контроллера, к которому привязана станция. Значение извлекается из столбца `BSC NAME` листа `2G_BTS_Data`. Если столбец отсутствует или пуст — показывается «—».

### 3. Параметры формирования / Generation parameters

| Параметр | Описание |
|----------|----------|
| Тип площадки | `12mbb` — Центр, `13mbb` — Северо-Запад |
| Регион | Определяется типом площадки (см. таблицу ниже) |
| Тип BBU | `3900` или `5900` |
| Шаблон | Выбирается автоматически из `templates/<регион>/<BBU>/` |
| Софт BTS | Версия ПО BTS (опционально) |
| Софт BSC | Версия ПО BSC (опционально) |
| Номер слота платы | Форматы: `1-2`, `1 2`, `1,2` |
| Используемые порты платы | Те же форматы |
| Порт транспортной платы | `0` или `1` |

**Региональная привязка:**

| 12mbb (Центр) | 13mbb (Северо-Запад) |
|----------------|----------------------|
| Владимир | Архангельск |
| Иваново | Великий Новгород |
| Калуга | Калининград |
| Кострома | Мурманск |
| Рязань | Петрозаводск |
| Смоленск | Псков |
| Тверь | Санкт-Петербург |
| Тула | Череповец-Вологда |
| Ярославль | |

### 4. Кнопки действий / Actions

- **Сформировать файл** — запускает генерацию (доступна, когда заполнены обязательные поля).
- **Сохранить результат** — сохраняет рабочую копию в выбранную папку.
- **Очистить temp** — удаляет промежуточные файлы `*_generated_*.xlsx` из папки `temp/`.

### 5. Статус / Status

Текстовая строка с текущим состоянием: ожидание, формирование, завершено, ошибка.

### 6. Логи выполнения / Execution log

Поле с прокруткой, куда выводятся все сообщения о ходе генерации. Дублируются в файл `logs/app.log`.

---

## Входные данные / Input files

### ДИ / Design Input

Обязательные листы (ищутся по алиасам, см. [Устойчивость к названиям](#устойчивость-к-названиям--alias-tolerance)):

| Каноническое имя | Алиасы |
|------------------|--------|
| `2G_BTS_Data` | `2G BTS Data`, `2G BTS`, `2G` |
| `4G_Data` | `4G Data`, `LTE Data`, `LTE`, `4G` |
| `Конфигурация сайта` | `конфигурация сайта`, `Конфиг сайта`, `Site Configuration`, `site configuration` |

Из листа `Конфигурация сайта` извлекается NE Name; из `2G_BTS_Data` — BSC NAME; из `4G_Data` — `eNodeBID`.

### ТС / Transport Sheet

Транспортный лист ищется по алиасам: `ip-план`, `ip план`, `ip-plan`, `ip_plan`, `ipplan`, `IP-план`, `IP план`, `IP PLAN`, `ip plan`, `IP plan`, `IP-Plan`, `ИД БС-ТС`, `Заявка РЦМ`, `IP BTS`, `IP BS`.

Строка заголовков определяется автоматически: проверяются первые 8 строк, выбирается та, где больше всего совпадений с ожидаемыми заголовками.

### Форматы слотов и портов / Slot & port formats

- Диапазон: `1-2`, `0-2`
- Через запятую: `1,2`, `0,1,2`
- Через пробел: `1 2`, `0 1 2`

Дубликаты удаляются, порядок пользователя сохраняется.

---

## Как работает генерация / Generation pipeline

```
ДИ + ТС + параметры формы
        │
        ▼
  Валидация входных данных
        │
        ▼
  Чтение листов ДИ (2G_BTS_Data, 4G_Data, Конфигурация сайта)
        │
        ▼
  Построение GSM- и LTE-записей
        │
        ▼
  Построение RRU-профилей, назначение Chain No.
        │
        ▼
  Построение секторов и Sector Equipment
        │
        ▼
  Чтение ТС (или пропуск, или ручной ввод)
        │
        ▼
  Выбор плат/портов для LTE-цепочек (интерактивный диалог)
        │
        ▼
  Создание рабочей копии шаблона
        │
        ▼
  Замена NE Name по всей книге
        │
        ▼
  Замена версий ПО BTS/BSC (если выбраны)
        │
        ▼
  Заполнение 11 листов шаблона
        │
        ▼
  Очистка внешних ссылок из формул
        │
        ▼
  Готовый файл в temp/
```

### Листы шаблона и их источники / Template sheets & sources

| Лист шаблона | Откуда берутся данные |
|---|---|
| **NE Version** | `Ne Name(name@OSS)` из листа `Конфигурация сайта` |
| **Auto Deployment** | NE Name |
| **GSM Cell** | `2G_BTS_Data`: CI, Cell Name, LAC, NCC, BCC, RAC, BCCH Frequency, Power |
| **GTRXGROUP** | CI → TRX Group ID, Sector Equipment ID |
| **LTE Cell** | `4G_Data`: Local Cell ID, Cell Name, TAC, Band, EARFCN, Bandwidth, PCI, RSP, PB, TxRxmode |
| **Base Station Transport Data** | ТС: OMCH, ABIS, S1 (IP, GW, VLAN) + DI-derived: eNodeB ID, ADJNODE, SCTPLNK |
| **BBP(NODE)** | Слоты и порты платы из формы |
| **RRUCHAIN(NODE)** | Уникальные RRU → Chain No., Head Slot/Port |
| **RRU(NODE)** | Уникальные RRU → Chain No., Subrack No., Rx/TX channels |
| **SECTOR(NODE)** | Секторы из 2G+4G → Sector ID, Sector Antenna |
| **SECTOREQM(NODE)** | Sector Equipment ID, Sector ID, Sector Equipment Antenna |

---

## Бизнес-правила / Business rules

### NE Name

Извлекается из листа `Конфигурация сайта` (алиасы: `Ne Name(name@OSS)`, `NE Name`, `NodeB Name`, `eNodeB Name`). Записывается на лист `NE Version`, затем старое имя ищется по всем листам шаблона и заменяется на новое.

### BSC NAME

Извлекается из листа `2G_BTS_Data` (алиасы: `BSC NAME`, `BSC Name`, `BSC_NAME`, `Bsc Name`, `BSC`). Отображается в интерфейсе сразу после выбора файла ДИ. В шаблон не записывается — помогает инженеру убедиться, что выбран правильный файл.

### Chain No. (RRUCHAIN)

Каждому уникальному RRU назначается `*Chain No.` по таблице, зависящей от типа площадки, региона и диапазона. Сначала проверяются региональные переопределения (`CHAIN_NO_RULES_BY_REGION`), затем — общие правила по типу площадки (`CHAIN_NO_RULES`).

**12mbb (Центр):**

| Диапазон | Chain No. |
|----------|-----------|
| 900 | 90 |
| 1800 | 180 |
| 2100 | 210 |
| 2600 | 240 |
| 2600 TDD | 230 |
| 1800/2100 | 200 |
| 1800/2100/2600 | 200 |

**13mbb (Северо-Запад):**

| Диапазон | Chain No. |
|----------|-----------|
| 800 | 80 |
| 900 | 120 |
| 1800 | 140 |
| 2100 | 60 |
| 2600 | 150 |
| 2600 TDD | 180 |
| 1800/2100 | 200 |
| 1800/2100/2600 | 200 |

**Переопределение для Калининграда (13mbb):**

| Диапазон | Chain No. |
|----------|-----------|
| 1800 | 130 |
| 2100 | 140 |
| 2600 | 160 |
| 1800/2100 | 200 |
| 1800/2100/2600 | 200 |

Если на одном базовом Chain No. оказывается несколько RRU, каждому следующему прибавляется 1. RRU сортируются по номеру антенны (`RetName`), чтобы `chain_no` совпадал с порядком секторов.

### Определение диапазона RRU

Диапазон определяется по столбцу `Band (HW)` в ДИ. Если значение пусто или неоднозначно, диапазон берётся по модели RRU из справочника `RRU_MODEL_TO_BAND` (например, `RRU5909` → `1800`, `RRU3908` → `900`). Комбинации диапазонов одного RRU объединяются: `{1800, 2100}` → `1800/2100`, `{1800, 2100, 2600}` → `1800/2100/2600`.

### TxRx-режим и Shared 2T2R Split

Если один RRU обслуживает несколько 2T2R-секторов одновременно в 2G и 4G, он автоматически переводится в режим `4T4R` (rx=4, tx=4). Порты антенн распределяются между подсекторами:

| Подсектор | Порты антенны |
|-----------|---------------|
| 1-й shared split | `R0A, R0B` |
| 2-й shared split | `R0A, R0C` |
| 3-й shared split | `R0B, R0D` |
| 4-й shared split | `R0C, R0D` |

Для 2G на общем 4T4R-RRU без split используется поднабор `R0A, R0C`. Для отдельного 2T2R-RRU — стандартные `R0A, R0B`, для 4T4R — `R0A, R0B, R0C, R0D`.

### Sector Equipment ID

Формат: `{префикс}{chain_no:03d}{суффикс}`, где:

- префикс `2` для 2G, `4` для 4G;
- `chain_no` — номер цепочки RRU;
- суффикс: `0` по умолчанию; `1` для диапазона 2100 на multi-band RRU `1800/2100`; номер split-подсектора при shared 2T2R.

### Номер сектора (RetName)

Если в ДИ заполнен столбец `RetName` с номером антенны (`a1`, `a2`, `a3`), номер сектора определяется по нему. Иначе — из суффикса имени ячейки (`CellName_1`, `CellName_2`).

### Замена версий ПО

- **BTS** — сохраняется префикс модели (например, `BTS3900_5900`), заменяется только часть `V100R...`. Паттерн: `BTS[0-9_ ]+V100R\d{3}C\d{2}SPC\d{3}`.
- **BSC** — полная замена значения по паттерну `BSC\d+V100R\d{3}C\d{2}SPC\d{3}`.

Дубликаты после замены (например, `A;A`) автоматически удаляются.

---

## Транспортные параметры / Transport parameters

### Чтение из ТС

Из ТС в шаблон переносятся (маппинг `TRANSPORT_COLUMN_MAPPINGS`):

| Источник (ТС) | Цель (шаблон) | Обработка |
|---|---|---|
| MGT IP | OMCH | Извлекается только IPv4-адрес |
| MGT GW | OMCH NH | Извлекается только IPv4-адрес |
| MGT Vlan VRF oam | OMCH Vlan | Извлекается только номер VLAN |
| GSM VLAN_ID VRF 2G | ABIS Vlan | Извлекается только номер VLAN |
| GSM IP_ID | ABIS | Извлекается только IPv4-адрес |
| GSM GW | ABIS NH | Извлекается только IPv4-адрес |
| LTE IP_ID | S1 | Извлекается только IPv4-адрес |
| LTE GW | S1 NH | Извлекается только IPv4-адрес |
| LTE VLAN_ID VRF 4G | S1 Vlan | Извлекается только номер VLAN |

### DI-derived поля (при пропуске ТС)

Если ТС пропущен, транспортные IP/VLAN остаются пустыми, но вычисляемые поля заполняются:

| Поле | Значение |
|------|----------|
| `*Name`, `*BTS Name`, `*eNodeB Name` | NE Name |
| `*eNodeB ID` | Из столбца `eNodeBID` листа `4G_Data` |
| `ADJNODE (ID)` | Последняя группа цифр из NE Name без ведущих нулей |
| `SCTPLNK(BSC) (ID1)` | ADJNODE + `"0"` |
| `Port` | Значение из поля «Порт транспортной платы» |

### Обработка ошибок ТС

При проблемах с ТС (отсутствует лист, нет нужных колонок, пустые данные) приложение предлагает три варианта:

1. **Заполнить вручную** — открывается диалог со всеми полями `Base Station Transport Data`.
2. **Пропустить ТС** — DI-derived поля заполняются, IP/VLAN остаются пустыми.
3. **Отмена** — генерация прерывается.

---

## Диалог выбора плат/портов / Board & port dialog

Если в ДИ найдено более одной LTE-цепочки, перед генерацией открывается диалог (`RRUChainPortDialog`), где для каждой цепочки нужно выбрать:

- **Плата** (Slot No.) — из списка, введённого в форме.
- **Порт** (Head Port No.) — из списка портов, введённого в форме.

Для одной LTE-цепочки назначения происходят автоматически (первый слот + первый порт).

---

## Устойчивость к названиям / Alias tolerance

Приложение не требует точного совпадения имён листов и заголовков. Все варианты написания собраны в алиасы в `core/constants.py`:

- **Листы ДИ:** `2G_BTS_Data`, `2G BTS Data`, `2G BTS`, `2G` — все приведут к одному результату.
- **Листы ТС:** `ip-план`, `ip план`, `ip-plan`, `IP-Plan`, `ИД БС-ТС`, `Заявка РЦМ`, `IP BTS`, `IP BS` и другие.
- **Заголовки колонок:** `BSC NAME`, `BSC Name`, `BSC_NAME`, `BSC` — и т.д.
- **Листы шаблона:** `GSM Cell`, `GSM_CELL`, `GSMCell`.

Поиск идёт по нормализованным именам: без учёта регистра, пробелы/дефисы/подчёркивания игнорируются.

---

## Работа с шаблоном / Template handling

- При генерации создаётся **копия** шаблона в папке `temp/`. Оригинал никогда не изменяется.
- Имя файла: `{NE_Name}_generated_{дата_время}.xlsx`.
- Если данных из ДИ больше, чем строк в шаблоне — недостающие строки **клонируются** с сохранением стилей, высоты, merged cells и формул.
- Если данных меньше — **лишние строки удаляются**.
- Для файлов `.xlsm` макросы сохраняются (`keep_vba=True`).
- После сохранения из формул удаляются внешние ссылки вида `[1]`, которые openpyxl может создать ошибочно.

---

## Запуск из исходников / Run from source

### Windows

```bat
run_windows.bat
```

Или вручную:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

### macOS

```bash
./run_macos.command
```

Скрипты запуска (`scripts/run_windows.ps1`, `scripts/run_macos.sh`) сами создают `.venv`, ставят зависимости и запускают `main.py`.

---

## Сборка exe / Build exe

```bat
build_windows_exe.bat
```

Создаёт `dist/Lazy Integration.exe` — один файл с встроенными шаблонами и логами. Python на целевой машине не нужен. Иконка приложения берётся из `app.ico`. PyInstaller-спецификация сохранена в `Lazy Integration.spec`.

---

## Структура проекта / Project structure

```
main.py                              Точка входа: создаёт QApplication и главное окно

gui/                                 Графический интерфейс (PySide6)
  main_window.py                     Главное окно: файлы, BSC, параметры, логи, кнопки
  widgets.py                         FilePickerRow, StatusBarWidget, LogViewer
  dialogs.py                         RRUChainPortDialog, TransportIssueChoiceDialog,
                                     TransportManualInputDialog

core/                                Бизнес-логика
  constants.py                       Алиасы листов и заголовков, регионы, Chain No.,
                                     маппинги ТС, справочник RRU_MODEL_TO_BAND
  excel_loader.py                    Открытие и чтение Excel-книг (ДИ, ТС, шаблон);
                                     извлечение NE Name и BSC NAME
  validators.py                      Валидация формы, проверка обязательных листов,
                                     парсинг портов/слотов
  transforms.py                      Band → Frequency band, Bandwidth → CELL_BW,
                                     TxRx → каналы, Chain No. по региону, Sector Equipment ID
  sector_builder.py                  Построение GSM/LTE-записей из строк ДИ
  rru_builder.py                     Построение RRU-цепочек, секторов, оборудования;
                                     логика shared 2T2R split
  row_cloner.py                      Клонирование строк шаблона с форматированием
  template_writer.py                 Запись данных в шаблон по заголовкам
  mapping_engine.py                  Оркестратор: связывает все компоненты вместе

models/                              Data-классы
  app_state.py                       UserInputState (состояние формы, включая bsc_name),
                                     GenerationArtifacts (пути к результатам)
  di_models.py                       GSMCellRecord, LTECellRecord, RRUChainRecord,
                                     RRURecord, SectorRecord, SectorEquipmentRecord,
                                     ProcessedDataBundle
  template_models.py                 SheetWriteConfig

services/                            Сервисы
  replace_service.py                 Глобальные замены: NE Name по книге,
                                     BTS/BSC версии ПО с дедупликацией
  mapping_service.py                 Альтернативный оркестратор (pandas-based)
  excel_loader.py                    Сервис чтения Excel
  template_manager.py                Управление шаблонами
  logger_service.py                  Сервис логирования

config/                              Конфигурация
  branches.py                        Список филиалов
  mappings.py                        Маппинг колонок ТС→шаблон, паттерны ПО BTS/BSC
  settings.py                        Пути к каталогам, размеры окна
  software_options.py                Списки версий BTS/BSC ПО

utils/                               Утилиты
  excel_utils.py                     Поиск строки заголовков, копирование стилей ячеек
  text_utils.py                      Нормализация заголовков, извлечение IPv4/VLAN,
                                     нормализация Band, извлечение номера антенны
  logger.py                          Логирование в файл и GUI

templates/                           Excel-шаблоны по регионам и типам BBU
  <Регион>/
    3900/
      <имя_шаблона>.xlsx
    5900/
      <имя_шаблона>.xlsx

logs/                                Файлы логов (app.log)
temp/                                Рабочие копии шаблонов
```

---

## Зависимости / Dependencies

| Пакет | Версия | Назначение |
|-------|--------|------------|
| PySide6 | `>=6.7,<7.0` | Графический интерфейс |
| openpyxl | `>=3.1,<4.0` | Чтение и запись Excel |
| pyinstaller | `>=6.10,<7.0` | Сборка exe (только для разработки) |

См. `requirements.txt`.

---

## Логи / Logs

- Выводятся в окно приложения (LogViewer) и дублируются в `logs/app.log`.
- Формат: `2026-06-02 10:30:15 [INFO] Сообщение`.
- Уровни: **INFO** (ход выполнения), **WARNING** (некритичные проблемы), **ERROR** (ошибки).

---

## Примечание о посторонних файлах / Note on unrelated files

В корне репозитория присутствуют файлы, **не относящиеся к приложению Lazy Integration**. Они остались от стартового шаблона и AI-тулкита; приложение работает без них и их можно удалить:

- **React/Vite/TS scaffold** из `yellowbe-opencode-starter`: `src/`, `index.html`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `eslint.config.js`, `public/`, `node_modules/`, `.npmrc`, `npmrc.example`, `beecat.png`, `smiling.png`.
- **OpenCode pipeline tooling**: `.opencode/`, `.opencode-pipeline/`, `AGENTS.md`, `opencode.json`, `docs/specs/`, `ca-bundle.pem`, `Vimpelcom-InternalCA-G2-G3.pem`.

Файлы самого приложения: `main.py`, `gui/`, `core/`, `services/`, `models/`, `config/`, `utils/`, `templates/`, `logs/`, `temp/`, `app.ico`, `requirements.txt`, `run_windows.bat`, `run_macos.command`, `build_windows_exe.bat`, `Lazy Integration.spec`, `scripts/`.

> **EN** — The repo root also contains files unrelated to Lazy Integration (leftover React/Vite/TS scaffold from `yellowbe-opencode-starter` and OpenCode pipeline tooling). They are not used by the app and can be safely removed.
