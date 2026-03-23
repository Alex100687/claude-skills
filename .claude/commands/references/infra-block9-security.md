# Блок 9 — Безопасность сервера

## Факт
Как только VPS появляется в интернете, боты начинают стучаться в SSH. Это автоматические сканеры. Без защиты рано или поздно подберут пароль.

## Проверка атак
```bash
lastb | head -20
```

## Шаг 1. Автообновления (2 мин)
```bash
apt update && apt upgrade -y
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
# → ответить Yes
```

## Шаг 2. fail2ban — автобан ботов (3 мин)
5 неправильных паролей → IP банится на 10 минут.
```bash
apt install fail2ban -y
systemctl enable --now fail2ban
fail2ban-client status sshd
```

## Шаг 3. UFW — файрвол (3 мин)

### КРИТИЧЕСКИ ВАЖНО: порядок команд!
ВСЕГДА сначала `ufw allow 22`, ПОТОМ `ufw enable`. Иначе потеря доступа!

```bash
# 1. Разрешить SSH (ПЕРВАЯ КОМАНДА!)
ufw allow 22/tcp

# 2. HTTPS (если нужен веб-сервер)
ufw allow 443/tcp

# 3. OpenVPN (если настраивали)
ufw allow 1194/udp

# 4. Включить файрвол
ufw enable
# → ответить y

# 5. Проверить
ufw status
```

Управление портами:
```bash
ufw allow 8080/tcp          # добавить порт
ufw status numbered         # список с номерами
ufw delete 3                # удалить правило №3
```

## Копипаста: безопасность за 5 минут
```bash
apt update && apt upgrade -y
apt install unattended-upgrades fail2ban ufw -y
dpkg-reconfigure -plow unattended-upgrades
ufw allow 22/tcp
ufw allow 443/tcp
ufw enable
echo "=== fail2ban ==="
fail2ban-client status sshd
echo "=== firewall ==="
ufw status
echo "=== auto-updates ==="
systemctl is-active unattended-upgrades
```

## Что НЕ надо делать (пока)
- Менять SSH порт — забудете и потеряете доступ
- Отключать вход по паролю — потеряете ключ = заблокируете себя
- Отключать root-логин — пока один пользователь, это = заблокировать себя
- CrowdSec, knock-knock, 2FA на SSH — оверинжиниринг для учебного сервера

## Принцип
Каждый открытый порт должен иметь владельца и причину. Не знаешь зачем открыт — закрой.
