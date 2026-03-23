# Блок 10 — Бонусы

## OpenClaw — Claude в Telegram

### Установка
```bash
npm install -g openclaw
```

### Создание бота
1. Telegram → @BotFather → /newbot
2. Придумать имя и username
3. Скопировать токен

### Настройка
```bash
openclaw init    # мастер настройки
openclaw start   # запуск
```
Требует активную подписку Claude и работающий Claude Code на сервере.

## Upload2Server — файлы через Telegram

### Создание бота
1. @BotFather → /newbot → скопировать токен
2. Узнать свой ID: @userinfobot → /start

### Установка
```bash
cd /opt/workspace
cp -r infralearn/upload-bot .
cd upload-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Настройка
```bash
cat > .env << EOF
BOT_TOKEN=ВАШ_ТОКЕН_БОТА
ADMIN_ID=ВАШ_TELEGRAM_ID
EOF
```

### Запуск
```bash
source .env && python3 bot.py
```

### Автозапуск (systemd)
```bash
sudo cp upload-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now upload-bot
sudo systemctl status upload-bot
```

### Отправка файлов С сервера в Telegram
```bash
curl -F document=@/path/to/file \
  "https://api.telegram.org/bot${BOT_TOKEN}/sendDocument" \
  -F chat_id=ВАШ_TELEGRAM_ID
```

## OpenVPN за 10 минут

```bash
curl -O https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
chmod +x openvpn-install.sh
sudo ./openvpn-install.sh
```

Ответы на вопросы установщика:
- IP: по умолчанию
- IPv6: n
- Port: 1194
- Protocol: UDP
- DNS: 3 (Cloudflare)
- Compression: n
- Client name: phone (или laptop)

Файл конфигурации: `~/phone.ovpn`

Подключение: OpenVPN Connect (App Store / Google Play) → импортировать .ovpn

```bash
sudo ./openvpn-install.sh              # добавить клиента
sudo systemctl status openvpn-server@server  # проверить статус
```

## Cron — планировщик задач

### Формат
```
┌───── минута (0-59)
│ ┌──── час (0-23)
│ │ ┌─── день месяца (1-31)
│ │ │ ┌── месяц (1-12)
│ │ │ │ ┌─ день недели (0-7, вс=0 или 7)
* * * * *  команда
```

### Примеры
```bash
# Каждый день в 3:00 — обновления
0 3 * * * apt update && apt upgrade -y >> /var/log/auto-upgrade.log 2>&1

# Каждый день в 4:00 — бэкап
0 4 * * * tar czf /root/backup-$(date +\%Y\%m\%d).tar.gz /opt/myproject/

# Каждые 6 часов — диск
0 */6 * * * df -h / >> /var/log/disk-usage.log

# Каждое воскресенье — очистка бэкапов
0 5 * * 0 ls -t /root/backup-*.tar.gz | tail -n +6 | xargs -r rm

# Git-бэкап vault каждый вечер
0 22 * * * cd /opt/workspace/vault && git add -A && git commit -m "auto-backup $(date +\%F)" && git push 2>&1 | tail -1 >> /var/log/vault-backup.log
```

### Управление
```bash
crontab -e                          # редактировать
crontab -l                          # посмотреть
grep CRON /var/log/syslog | tail -10  # логи

```

### Частые ошибки
- Забыли `2>&1` — ошибки не попадут в лог
- `%` в crontab — спецсимвол, писать `\%`
- PATH: cron не знает ваш PATH, использовать полные пути (`/usr/bin/python3`)

## Ребут сервера — что происходит
| Что | После ребута |
|---|---|
| tmux-сессии | Умирают → запустить `tmux new -s work` |
| systemd-сервисы | Запускаются сами (если enable) |
| cron-задачи | Работают |
| UFW | Работает |
| fail2ban | Запускается, баны обнуляются |

### Чеклист после ребута
```bash
systemctl --failed       # проверить сервисы
tmux ls                  # скорее всего пусто
tmux new -s work         # новая сессия
```
