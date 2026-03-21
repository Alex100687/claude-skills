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
└── Scripts/         ← скрипты автоматизации
```

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
