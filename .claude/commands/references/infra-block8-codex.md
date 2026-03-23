# Блок 8 — Codex CLI

## Установка
```bash
npm install -g @openai/codex
```

## Первый запуск
```bash
codex
```
Авторизация: OAuth через браузер (ChatGPT Plus) или API Key (OpenAI).

## AGENTS.md
Аналог CLAUDE.md, но для Codex. Лежит в корне проекта.
```bash
cp /opt/workspace/infralearn/configs/AGENTS.md /opt/workspace/AGENTS.md
```

## Сравнение Claude Code vs Codex CLI
| Параметр | Claude Code | Codex CLI |
|---|---|---|
| Компания | Anthropic | OpenAI |
| Модели | Claude Sonnet/Opus | GPT-4.1/o3 |
| Файл инструкций | CLAUDE.md | AGENTS.md |
| Плагины | MCP-серверы | Нет |
| Скиллы | Да (Markdown) | Нет |
| Хуки | Да | Нет |
| Память | Через MCP | Нет |
| Песочница | Нет (прямой доступ) | Да (sandbox) |
| Подписка | Claude Pro/Max | ChatGPT Plus/Pro |

## Когда что использовать
- **Claude Code** — основной инструмент (MCP, скиллы, хуки)
- **Codex CLI** — второе мнение, альтернативный подход

## Настройка codex-start
Промпт для Codex (вставить внутри Codex CLI):
```
Настрой для меня удобный старт Codex и статусную строку.
1. Исследуй окружение
2. Создай команду codex-start в ~/.local/bin/
3. Настрой /statusline
4. Покажи документацию
```

## Проверка
```bash
which codex-start
codex-start
# Внутри Codex: /statusline
```
