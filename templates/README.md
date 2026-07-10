# Пример структуры папки templates

Каждый шаблон должен лежать в каталоге:

```text
templates/<Филиал>/<Тип_BBU>/
```

Примеры:

```text
templates/Архангельск/3900/arch_3900_template.xlsx
templates/Архангельск/5900/arch_5900_template.xlsx
templates/Санкт-Петербург/3900/spb_3900_template.xlsx
templates/Санкт-Петербург/5900/spb_5900_template.xlsx
```

GUI автоматически перечитывает файлы `.xlsx` и `.xlsm` из нужной папки после выбора филиала и типа BBU.
