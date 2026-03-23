# Блок 5 — Memory + MCP

## Часть 1: Память

### Уровень 1: MEMORY.md (встроенная)
Claude Code автоматически пишет в `~/.claude/MEMORY.md` (до 200 строк). Работает из коробки.

```bash
cat ~/.claude/MEMORY.md
```

Попросить запомнить: "Запомни: мой основной язык — Python, я работаю над проектом X"

### Уровень 2: claude-mem (MCP-сервер)
Граф знаний без лимита: сущности, факты, связи.

```bash
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
```

Инструменты после установки:
| Инструмент | Что делает |
|---|---|
| create_entities | Создать сущности |
| add_observations | Добавить факты |
| search_nodes | Поиск по памяти |
| create_relations | Связать сущности |

### Тест памяти
1. `claude` → "Запомни: мой любимый язык — Python"
2. `/exit`
3. `claude` → "Какой мой любимый язык?"
4. Claude должен ответить правильно!

## Часть 2: MCP-серверы

### Filesystem
```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /opt/workspace
```

### GitHub
```bash
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_YOUR_TOKEN \
  -- npx -y @modelcontextprotocol/server-github
```
Токен: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic). Права: repo, read:org.

### Context7 (документация)
```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

### Exa (веб-поиск)
```bash
claude mcp add exa -e EXA_API_KEY=YOUR_EXA_API_KEY \
  -- npx -y exa-mcp-server
```
Регистрация: exa.ai, есть бесплатный план.

### Проверка
```bash
claude mcp list
```
Должно быть 5 серверов: memory, filesystem, github, context7, exa.

### Если MCP timeout
Установить глобально вместо npx:
```bash
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
```

## ВАЖНО
После `claude mcp add` нужна НОВАЯ сессия: `/exit` → `claude`
