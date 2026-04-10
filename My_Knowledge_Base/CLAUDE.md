# Vault Rules for Claude

## Naming Convention

When creating or renaming files, always follow this format:

```
{project} {type} описание – YYYY-MM-DD.md
```

### Rules
- **EN DASH `–`** — единственное тире (Alt+0150 на Windows)
- **Дата — в конце.** Всегда.
- **Максимум 80 символов** в имени файла
- **Максимум 2 кода** в фигурных скобках перед описанием

---

## Project Codes {project}

```
{startup}       — основной бизнес
{product}       — конкретный продукт
{consulting}    — консалтинг
{channel}       — канал, блог
{course}        — образовательный проект
{self}          — личное развитие
{team}          — командные документы
```

---

## Content Types {type}

```
{rule}          — правила, стандарты
{guide}         — инструкции, how-to
{research}      — исследования, анализ
{plan}          — планы, roadmap
{template}      — шаблоны
{prompt}        — промпты для AI
{tool}          — описание инструмента
{article}       — статья, пост
{summary}       — саммари встречи
{meeting}       — запись встречи
{transcript}    — транскрипт звонка
{daily-focus}   — фокус дня
{weekly-sync}   — еженедельный обзор
{retro}         — ретроспектива
{prd}           — Product Requirements
{case}          — практический кейс
```

---

## Folder Structure

```
My_Knowledge_Base/
├── Inbox/           ← всё новое сюда
├── Skills/          ← навыки и инструменты
├── Дайджесты/       ← дайджесты и выпуски
├── Архив/           ← завершённые проекты
├── Scripts/         ← скрипты автоматизации
└── goals/           ← система целей AI Personal OS
    ├── values.md        # ценности и принципы
    ├── vision.md        # видение 3-5 лет
    ├── yearly.md        # годовые цели
    ├── monthly.md       # цели на месяц
    ├── weekly.md        # план недели + трекер привычек
    ├── daily.md         # задачи на сегодня
    ├── backlog.md       # разовые задачи (синхр. с Todoist)
    ├── journal/         # дневные записи (YYYY-MM-DD.md)
    ├── templates/       # шаблоны (journal.md)
    └── archive/         # архив прошлых периодов
```

### AI Personal OS — команды
- `/coach [morning|evening|priority|stuck|motivation]` — личный коуч
- `/daily-review` — закрыть вчера + спланировать сегодня
- `/goals [status|add|decompose|done|edit|align|backlog]` — управление целями
- `/weekly-review` — недельная ретроспектива
- `/monthly-review` — месячный стратегический обзор

### Правила системы целей
- Макс 3-5 целей на уровень (фокус важнее количества)
- Каждая цель связана с уровнем выше (день → неделя → месяц → год → видение → ценности)
- Лимит на день: **2 часа** (свободное время вечером)
- Формат задачи: `[Xч] Название — Метрика: [что значит "сделано"]`
- Задача > 1ч → разбить на подзадачи
- Todoist = операционный задачник, goals/ = стратегическая система

### Folder Rules
- Новые файлы → `Inbox/` если проект не указан
- Не создавать новые папки верхнего уровня без необходимости
- Flat > nested: один уровень лучше трёх

---

## YAML Frontmatter

Минимальный (всегда добавлять):

```yaml
---
tags:
  - type/research
  - project/startup
date: 2026-03-09
---
```

### Tags
```
type/       — тип (type/research, type/guide)
project/    — проект (project/startup)
topic/      — тема (topic/automation)
status/     — статус (status/active, status/draft)
```

Максимум 5 тегов на файл.

---

## Anti-patterns

- Никогда: `Meeting notes 23.docx` → правильно: `{project} {meeting} тема – 2026-03-09.md`
- Никогда: дата в середине имени
- Никогда: больше 80 символов
- Никогда: 5+ уровней вложенности папок
