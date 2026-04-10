# Решение проблем — Справочник

Когда пользователь сообщает о проблеме, найди подходящий раздел и предложи решение по порядку (от простого к сложному).

## SSH не подключается (Connection refused / timeout)
1. Проверь IP-адрес — опечатка?
2. Порт должен быть 22 (стандартный SSH)
3. VPS только что создан? Подождать 2-3 минуты
4. Проверить, что VPS запущен в панели хостинга
5. Попробовать пинг; если хостинг даёт веб-консоль — проверить через неё

## Claude Code OAuth — не открывается URL
1. URL нужно открыть **на ноутбуке** в браузере, НЕ на сервере
2. Скопировать URL полностью (с `https://`)
3. Убедиться что залогинен на console.anthropic.com
4. Проверить что подписка (Pro или Max) активна

## MCP timeout / не запускается
npx скачивает пакет при каждом запуске — это медленно. Решение — глобальная установка:
```bash
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
```
Затем в `claude mcp add` использовать прямой путь к бинарнику вместо npx.

Также: после `claude mcp add` ВСЕГДА нужна новая сессия (`/exit` → `claude`).

## Permission denied (нет прав)
1. Для скриптов: `chmod +x filename.sh`
2. Для директорий: `chmod 755 /path/to/dir`
3. Внутри Claude Code: `/permissions` для управления разрешениями
4. Проверить пользователя: `whoami` (должен быть root на учебном сервере)

## Claude Code не отвечает / зависает
1. `/status` — проверить статус подключения
2. Проверить подписку на console.anthropic.com
3. `/clear` и начать новый диалог
4. Выйти (Ctrl+C) и запустить заново: `claude`
5. Проверить интернет на сервере: `curl -s https://api.anthropic.com`

## Codex CLI не авторизуется
1. Попробовать OAuth через браузер (как с Claude Code)
2. Если OAuth не работает — использовать API Key:
```bash
export OPENAI_API_KEY="sk-your-key-here"
codex
```
Ключ: platform.openai.com/api-keys

## Node.js не найден после установки
1. Повторить установку:
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs
node -v
```
2. Проверить PATH: `echo $PATH`
3. Node.js должен быть в `/usr/bin/node`: `which node`

## npm WARN / npm ERR при установке пакетов
- **WARN** — обычно можно игнорировать (предупреждения)
- **ERR** — ошибка. Частые причины:
  1. Нет интернета: `ping google.com`
  2. Старая версия npm: `npm install -g npm@latest`
  3. Нет места на диске: `df -h`

## Потерял соединение — работа пропала
Использовать tmux! Золотое правило: подключился → сразу `tmux` (или `tmux attach`).
```bash
# Подключились обратно
tmux attach
# Все процессы внутри tmux продолжают работать
```

## Хуки не работают
1. Проверить что пути АБСОЛЮТНЫЕ: `/root/.claude/hooks/`, НЕ `~/.claude/hooks/`
2. Проверить что скрипты исполняемые: `chmod +x ~/.claude/hooks/*.sh`
3. Проверить структуру `settings.local.json`: событие → matcher → hooks массив
4. Перезапустить Claude Code

## IPv6 выдаёт геолокацию (Google/Gemini блокирует)
Google/Gemini может блокировать через IPv6 даже если VPN настроен.
Решение: отключить IPv6 в свойствах сетевого адаптера на ноутбуке.
