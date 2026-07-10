# Design System First

Все UI-компоненты по умолчанию берутся из библиотеки `@beeline/design-system-react`.

## Главный принцип

`Design System First` в этом пайплайне означает не «любой ценой следовать DS», а **строить сильный визуальный результат с опорой на DS**:

- сначала добиться живой, убедительной и хорошо дышащей композиции;
- затем опираться на DS-компоненты, layout primitives и documented props;
- затем, если MCP доступен и полезен, использовать DS colors / tokens / guidelines;
- если MCP недоступен, неполон или противоречив, не деградировать в бедный интерфейс: допускается controlled fallback с явным описанием решения.

## Правила

1. **Импорт**: по умолчанию из `@beeline/design-system-react`
   ```tsx
   import { Button, TextField, Select } from '@beeline/design-system-react';
   ```

2. **Пропсы**: использовать документированные пропсы (из MCP `get-component-props`). Имена пропсов не угадывать.

3. **Варианты и composition**:
   - сначала искать решение через DS-компоненты, `Box`, `Stack`, `Grid`, `GridItem`, documented props и layout primitives;
   - для layout приоритет у композиции и читаемости экрана, а не у формальной token-purity.

4. **Вложенные компоненты**: если `get-component` показывает nested components — использовать их (например, `Select.Option`, `List.Item`).

5. **ThemeProvider**: ОБЯЗАТЕЛЕН в корне приложения:
   ```tsx
   import { ThemeProvider } from '@beeline/design-system-react';
   
   function App() {
     return (
       <ThemeProvider>
         {/* ... */}
       </ThemeProvider>
     );
   }
   ```

6. **Цвет, тема и токены** (при подключённом `ThemeProvider`):
   - Для цветов, палитр, типографики и elevation **предпочтительно** опираться на DS props и подтверждённые токены из `get-global-design-tokens`.
   - Если MCP доступен, сначала пробовать подтвердить DS token name и использовать его как основной ориентир.
   - Если MCP недоступен, возвращает неполные данные или не покрывает нужный случай, допускается tasteful fallback без выдумывания псевдо-DS custom properties.
   - Нежелательно перекрашивать интерфейс случайными палитрами, если задача не требует осознанного controlled fallback.
   - Если пришлось отойти от DS token source, это должно быть отражено в `ds_gaps`, `Implementation Report` или review notes с кратким объяснением, почему решение выбрано ради качества результата.

7. **Spacing и layout**:
   - `spacing`, контейнеры, `max-width`, section rhythm и desktop composition не должны сводиться к agent-у «только глобальные токены или ничего».
   - Для layout сначала использовать DS layout primitives и handoff от дизайнера.
   - Если для сильной композиции нужен custom spacing/layout beyond DS props, это допустимо при условии, что решение остаётся аккуратным, согласованным с DS и не ломает визуальную систему экрана.

8. **Отсутствующий компонент**: если в DS нет нужного компонента:
   - зафиксировать в `ds_gaps`;
   - создать минимальную обёртку или fallback с опорой на существующие DS-компоненты;
   - не создавать самописный клон существующего DS-компонента без необходимости.

## Категории DS (86 компонентов)

| Категория | Назначение | Примеры |
|-----------|-----------|---------|
| form | Ввод данных | TextField, Select, Checkbox, DatePicker, PhoneInput, Rating, Switch, Radio, TextArea, Autocomplete, MaskField, Slider, FileUploader, Search, InlineEdit, TimePicker |
| display | Отображение | Avatar, Badge, Card, Chip, Counter, Icon, Label, Skeleton, Typography, Timeline, Tree |
| feedback | Уведомления | Banner, Informer, Progress, ProgressBar, Snackbar, InlineAlert, Notifications |
| layout | Разметка | Box, Divider, NavigationDrawer, NavigationRail, Toolbar |
| navigation | Навигация | Breadcrumbs, Pagination, Stepper, Tabs, TabsPrimitive, FloatingNavigation |
| interactive | Действия | Button, ButtonGroup, ButtonSet, FAB, Link, LinkRouter, IconButton |
| overlay | Всплывающие | BottomSheet, Dialog, Drawer, Dropdown, Popover, Tooltip, Sidesheet, Menu, NewDropdownMenu |
| other | Прочее | Collapse, ExpansionPanel, Header, Footer, ThemeProvider, BottomActionBar, TextfieldWithChips |
