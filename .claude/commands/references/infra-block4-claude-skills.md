# Блок 4 — CLAUDE.md + Skills

## Часть 1: CLAUDE.md

Два уровня:
| Уровень | Путь | Описание |
|---|---|---|
| Глобальный | ~/.claude/CLAUDE.md | Действует во всех проектах |
| Проектный | ./CLAUDE.md | Действует только в текущем проекте |

Проектный имеет приоритет и дополняет глобальный.

### Установка из репо курса
```bash
git clone https://github.com/alexfrmn/infralearn.git /opt/workspace/infralearn
mkdir -p ~/.claude
cp /opt/workspace/infralearn/configs/CLAUDE.md ~/.claude/CLAUDE.md
```

### Что писать в CLAUDE.md
- Кто вы — роль, стек, уровень
- Правила — язык, стиль кода, что можно/нельзя
- Контекст проекта — архитектура, ключевые файлы
- Память — что важно помнить между сессиями

## Часть 2: Skills (Скиллы)

Скилл — переиспользуемый промпт-шаблон. Структура: `~/.claude/skills/[имя]/SKILL.md`

### Установка готовых скиллов
```bash
mkdir -p ~/.claude/skills
cp -r /opt/workspace/infralearn/skills/* ~/.claude/skills/
ls ~/.claude/skills/
```

### 4 скилла из курса
| Скилл | Вызов | Что делает |
|---|---|---|
| code-review | /code-review | Ревью кода: баги, безопасность. Оценка 1-10 |
| decision-helper | /decision-helper | Pros/cons, рекомендация |
| compress | /compress | Сжатие контекста |
| exa-web-research | /exa-web-research | Исследование через Exa MCP |

### Создание своего скилла (пример)
```bash
mkdir -p ~/.claude/skills/server-status
cat > ~/.claude/skills/server-status/SKILL.md << 'EOF'
---
name: server-status
description: Показать статус сервера — CPU, RAM, диск, uptime
---

# Server Status

Покажи текущий статус сервера:
1. Дата и время
2. Uptime
3. CPU нагрузка (load average)
4. Оперативная память (free -h)
5. Свободное место на диске (df -h /)

Формат: компактный, в одном сообщении, с emoji.
EOF
```
