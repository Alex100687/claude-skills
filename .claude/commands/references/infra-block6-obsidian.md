# Блок 6 — Obsidian Vault на сервере

## Шаг 1: Создание vault
```bash
mkdir -p /opt/workspace/vault/{00-Inbox,Projects,Daily-Notes}
cd /opt/workspace/vault
git init
echo "# My Knowledge Base" > README.md
git add . && git commit -m "init vault"
```

## Шаг 2: GitHub репозиторий
```bash
cd /opt/workspace/vault
gh repo create my-vault --private --source=. --push
```

Если gh не установлен:
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh -y
gh auth login
```

## Шаг 3: Клонирование на компьютер

macOS:
```bash
cd ~ && git clone https://github.com/USERNAME/my-vault.git
```

Windows (PowerShell):
```powershell
cd ~\Documents
git clone https://github.com/USERNAME/my-vault.git
```

## Шаг 4: Obsidian
1. Скачать Obsidian
2. Open folder as vault → выбрать my-vault
3. Settings → Community plugins → Browse → "Obsidian Git" → Install → Enable

## Шаг 5: Настройки Obsidian Git
| Настройка | Значение |
|---|---|
| Auto backup every X minutes | 5 |
| Auto pull on startup | ON |
| Auto pull interval | 5 |
| Commit message | vault auto-sync |
| Push on backup | ON |

## macOS: SSH ошибка с Obsidian Git
Переключить remote на HTTPS:
```bash
cd ~/my-vault
git remote set-url origin https://github.com/USERNAME/my-vault.git
git config --global credential.helper osxkeychain
```

## Синхронизация с сервером
```bash
# На сервере — получить свежее
cd /opt/workspace/vault && git pull

# Отправить изменения сервера
git add . && git commit -m "server update" && git push
```

Итог: Obsidian пушит каждые 5 минут → сервер делает git pull → Claude видит заметки.
