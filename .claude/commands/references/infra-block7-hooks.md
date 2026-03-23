# Блок 7 — Hooks + Statusline

## Что такое хуки
Скрипты, которые Claude Code запускает при событиях:
- **PreToolUse** — перед выполнением инструмента (можно блокировать)
- **PostToolUse** — после выполнения инструмента
- **SessionStart** — при запуске сессии
- **SessionEnd** — при завершении сессии
- **Notification** — когда Claude хочет привлечь внимание

## Шаг 1: Копирование хуков
```bash
mkdir -p ~/.claude/hooks
cp /opt/workspace/infralearn/hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
```

## Шаг 2: settings.local.json

ВАЖНО: только АБСОЛЮТНЫЕ пути! `/root/.claude/hooks/`, НЕ `~/.claude/hooks/`

```bash
cp /opt/workspace/infralearn/configs/settings.local.json ~/.claude/settings.local.json
```

Структура settings.local.json:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /root/.claude/hooks/session-start.sh"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /root/.claude/hooks/session-end.sh"
          }
        ]
      }
    ]
  }
}
```

Структура: событие → matcher (пустая строка = все) → hooks массив с командами.

## Пример: хук уведомления
```bash
cat > ~/.claude/hooks/notify.sh << 'HOOKEOF'
#!/bin/bash
LOGFILE="/tmp/claude-notifications.log"
INPUT=$(cat)
TITLE=$(echo "$INPUT" | jq -r '.title // "no title"')
MSG=$(echo "$INPUT" | jq -r '.message // "no message"')
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $TITLE: $MSG" >> "$LOGFILE"
HOOKEOF
chmod +x ~/.claude/hooks/notify.sh
```

## Statusline

Показывает: модель, контекст %, время сессии, стоимость, изменения кода.

```
sonnet 4.6 | ▓▓░░░░░░░░ 18% | 1h05m | $2.30 +234,-12 lines
```

### Установка
```bash
cp /opt/workspace/infralearn/configs/statusline.js ~/.claude/statusline.js
cp /opt/workspace/infralearn/configs/settings.json ~/.claude/settings.json
```

Перезапустить Claude Code — statusline появится внизу.
