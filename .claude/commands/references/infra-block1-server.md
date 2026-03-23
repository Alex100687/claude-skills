# Блок 1 — Базовая настройка сервера

## Шаг 1. Обновление системы
```bash
apt update && apt upgrade -y
```

## Шаг 2. Базовые утилиты
```bash
apt install -y git curl wget htop tmux jq unzip
```
- git — контроль версий
- curl, wget — скачивание файлов
- htop — мониторинг ресурсов
- tmux — мультиплексор терминала
- jq — работа с JSON
- unzip — распаковка архивов

## Шаг 3. Node.js 22 LTS
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs
```

## Шаг 4. Проверка версий
```bash
node -v && npm -v && python3 --version && git --version
```
Ожидается: Node v22.x.x, npm 10.x.x, Python 3.12.x, git 2.x.x

Если node не найден — повторить шаг 3.
Если python3 не найден: `apt install -y python3`

## Шаг 5. Настройка Git
```bash
git config --global user.name "СПРОСИТЬ_У_ПОЛЬЗОВАТЕЛЯ"
git config --global user.email "СПРОСИТЬ_У_ПОЛЬЗОВАТЕЛЯ"
```

## Шаг 6. Рабочая директория
```bash
mkdir -p /opt/workspace && cd /opt/workspace
```

## Мониторинг (справка)
```bash
htop                    # CPU, память, процессы
df -h                   # место на диске
free -h                 # оперативная память
uptime                  # время работы
```
