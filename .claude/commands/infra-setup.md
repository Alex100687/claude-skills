---
name: infra-setup
description: "Настройка AI-инфраструктуры на VPS: Ubuntu, Node.js, Claude Code, Codex CLI, MCP-серверы, скиллы, хуки, память, Obsidian vault, безопасность, tmux, cron. Использовать когда пользователь хочет настроить сервер, установить Claude Code на VPS, подключить MCP, настроить хуки, поднять VPN, настроить Obsidian sync, или выполнить любой шаг из курса InfraLearn. Также использовать при словах: 'настрой сервер', 'поставь Claude Code', 'подключи MCP', 'настрой инфраструктуру', 'infra', 'VPS setup'."
---

# AI Infrastructure Setup (InfraLearn)

Ты — эксперт по настройке AI-инфраструктуры на VPS-серверах. Твоя задача — провести пользователя через полную настройку или выполнить конкретный блок по запросу.

## Режимы работы

### 1. Полная настройка (по умолчанию)
Если пользователь говорит "настрой всё" / "полная установка" — выполняй блоки последовательно, проверяя каждый шаг.

### 2. Диагностика
Если пользователь говорит "проверь что настроено" / "диагностика" / "аудит" — запусти проверку всех компонентов и покажи чеклист.

### 3. Конкретный блок
Если пользователь называет конкретную задачу — выполни только её.

---

## Блоки настройки

Инфраструктура состоит из 9 блоков. При полной настройке выполняй их по порядку.

### Блок 0 — Диагностика окружения
Перед любой настройкой определи текущее состояние. Выполни:

```bash
echo "=== OS ===" && cat /etc/os-release | head -3
echo "=== Node ===" && (node -v 2>/dev/null || echo "NOT INSTALLED")
echo "=== npm ===" && (npm -v 2>/dev/null || echo "NOT INSTALLED")
echo "=== Python ===" && (python3 --version 2>/dev/null || echo "NOT INSTALLED")
echo "=== Git ===" && (git --version 2>/dev/null || echo "NOT INSTALLED")
echo "=== Claude Code ===" && (claude --version 2>/dev/null || echo "NOT INSTALLED")
echo "=== Codex ===" && (codex --version 2>/dev/null || echo "NOT INSTALLED")
echo "=== tmux ===" && (tmux -V 2>/dev/null || echo "NOT INSTALLED")
echo "=== MCP ===" && (claude mcp list 2>/dev/null || echo "NOT CONFIGURED")
echo "=== Hooks ===" && (cat ~/.claude/settings.local.json 2>/dev/null || echo "NOT CONFIGURED")
echo "=== CLAUDE.md ===" && (ls -la ~/.claude/CLAUDE.md 2>/dev/null || echo "NOT FOUND")
echo "=== Skills ===" && (ls ~/.claude/skills/ 2>/dev/null || echo "NO SKILLS")
echo "=== Workspace ===" && (ls /opt/workspace/ 2>/dev/null || echo "NOT CREATED")
echo "=== Firewall ===" && (ufw status 2>/dev/null || echo "NOT CONFIGURED")
echo "=== fail2ban ===" && (fail2ban-client status sshd 2>/dev/null || echo "NOT INSTALLED")
```

Покажи результат в виде чеклиста с галочками/крестиками. Предложи настроить недостающее.

### Блок 1 — Базовая настройка сервера
Прочитай `references/infra-block1-server.md` для подробных команд.

Краткий план:
1. `apt update && apt upgrade -y`
2. Установить утилиты: git, curl, wget, htop, tmux, jq, unzip
3. Установить Node.js 22 LTS через NodeSource
4. Проверить версии: node, npm, python3, git
5. Настроить git (спросить имя и email у пользователя)
6. Создать `/opt/workspace`

### Блок 2 — tmux
Прочитай `references/infra-block2-tmux.md` для подробностей.

Объясни пользователю зачем tmux и покажи основные команды. tmux уже установлен в блоке 1.

### Блок 3 — Claude Code
Прочитай `references/infra-block3-claude-code.md` для подробных команд.

1. `npm install -g @anthropic-ai/claude-code`
2. Первый запуск: `cd /opt/workspace && claude`
3. OAuth авторизация (объясни: URL открыть в браузере на ноутбуке, код вставить в терминал)
4. Настроить язык: `claude config set language ru`
5. Тестовый диалог

### Блок 4 — CLAUDE.md + Skills
Прочитай `references/infra-block4-claude-skills.md` для подробностей.

1. Клонировать репо курса: `git clone https://github.com/alexfrmn/infralearn.git /opt/workspace/infralearn`
2. Установить глобальный CLAUDE.md: `cp /opt/workspace/infralearn/configs/CLAUDE.md ~/.claude/CLAUDE.md`
3. Скопировать скиллы: `cp -r /opt/workspace/infralearn/skills/* ~/.claude/skills/`
4. Показать как создать свой скилл

### Блок 5 — Memory + MCP
Прочитай `references/infra-block5-memory-mcp.md` для подробных команд.

MCP-серверы для установки:
1. **memory** — `claude mcp add memory -- npx -y @modelcontextprotocol/server-memory`
2. **filesystem** — `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /opt/workspace`
3. **github** — нужен Personal Access Token (спросить у пользователя)
4. **context7** — `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest`
5. **exa** — нужен API ключ Exa (спросить у пользователя, опционально)

После добавления MCP — напомнить: нужна НОВАЯ сессия Claude Code (`/exit` → `claude`).

### Блок 6 — Obsidian Vault
Прочитай `references/infra-block6-obsidian.md` для подробностей.

1. Создать vault: `mkdir -p /opt/workspace/vault/{00-Inbox,Projects,Daily-Notes}`
2. Инициализировать git в vault
3. Создать GitHub репо (через `gh repo create`)
4. Объяснить синхронизацию с Obsidian на компьютере через плагин Obsidian Git

### Блок 7 — Hooks + Statusline
Прочитай `references/infra-block7-hooks.md` для подробностей.

1. Скопировать хуки из репо курса
2. Настроить `settings.local.json` (использовать АБСОЛЮТНЫЕ пути `/root/.claude/hooks/`)
3. Настроить statusline через `settings.json` + `statusline.js`

### Блок 8 — Codex CLI
Прочитай `references/infra-block8-codex.md` для подробностей.

1. `npm install -g @openai/codex`
2. Авторизация (OAuth или API key)
3. Скопировать AGENTS.md
4. Сравнение с Claude Code

### Блок 9 — Безопасность
Прочитай `references/infra-block9-security.md` для подробных команд.

Обязательный минимум (5 минут):
1. Автообновления: `apt install unattended-upgrades -y`
2. fail2ban: `apt install fail2ban -y && systemctl enable --now fail2ban`
3. UFW файрвол: **СНАЧАЛА** `ufw allow 22/tcp`, **ПОТОМ** `ufw enable`

### Блок 10 — Бонусы (опционально)
Прочитай `references/infra-block10-bonus.md` для подробностей.

- OpenClaw (Claude в Telegram)
- Upload2Server бот
- OpenVPN
- Cron-задачи

---

## Правила выполнения

1. **Всегда начинай с диагностики** (Блок 0) чтобы не переустанавливать то что уже есть
2. **Спрашивай перед действием** если нужны ключи/токены/данные пользователя
3. **Проверяй каждый шаг** — после установки проверь что работает
4. **Используй абсолютные пути** в хуках и конфигах (`/root/.claude/hooks/`, не `~/.claude/hooks/`)
5. **Напоминай про tmux** — любая работа на сервере начинается с `tmux` или `tmux attach`
6. **После MCP — новая сессия** — всегда напоминай что нужен `/exit` → `claude`
7. **UFW — порядок важен** — сначала `allow 22`, потом `enable`. Иначе потеря доступа!
8. **Не коммить секреты** — никогда не добавлять .env, токены, ключи в git

## Финальный чеклист

После настройки покажи итоговый чеклист:
- [ ] VPS работает, подключение через SSH
- [ ] Node.js 22, Git, утилиты установлены
- [ ] Claude Code установлен и авторизован
- [ ] CLAUDE.md на месте (глобальный)
- [ ] Минимум 3 скилла установлены
- [ ] Memory MCP настроен
- [ ] 3+ MCP-сервера подключены
- [ ] Хуки настроены (settings.local.json)
- [ ] Безопасность: fail2ban + UFW + auto-updates
- [ ] tmux используется
- [ ] Codex CLI установлен (опционально)
