#!/usr/bin/env python3
"""
Telegram-бот для запуска AI-дайджеста по команде.
Запускай один раз — висит в фоне и слушает команды.

Команды:
  /digest  — запустить генерацию дайджеста
  /status  — проверить статус (занят или свободен)
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error

# === Настройки ===
TG_TOKEN      = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID    = os.environ.get("TG_CHAT_ID", "")   # только этот чат принимает команды
TG_THREAD_DIGEST = os.environ.get("TG_THREAD_DIGEST", "")

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
WORK_DIR    = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
CLAUDE_EXE  = r"C:\Users\aleks\AppData\Roaming\Claude\claude-code\2.1.72\claude.exe"

_running = False
_lock    = threading.Lock()


# ── Telegram helpers ──────────────────────────────────────────────────────────

def _tg(method, params=None, timeout=35):
    url  = f"https://api.telegram.org/bot{TG_TOKEN}/{method}"
    data = json.dumps(params or {}).encode()
    req  = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def send(text, thread_id=None):
    params = {"chat_id": TG_CHAT_ID, "text": text}
    if thread_id:
        params["message_thread_id"] = int(thread_id)
    try:
        _tg("sendMessage", params)
    except Exception as e:
        print(f"[send error] {e}", file=sys.stderr)


def get_updates(offset):
    try:
        resp = _tg("getUpdates", {"timeout": 30, "allowed_updates": ["message"], "offset": offset})
        return resp.get("result", [])
    except Exception as e:
        print(f"[poll error] {e}", file=sys.stderr)
        time.sleep(5)
        return []


# ── Digest runner (в отдельном потоке, чтоб бот не завис) ────────────────────

def _do_run_digest(reply_thread):
    global _running
    try:
        # Убираем CLAUDECODE чтобы CC не блокировал вложенный запуск
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)

        result = subprocess.run(
            [CLAUDE_EXE, "-p", "сделай дайджест этой недели. Выполни ВСЕ шаги включая Шаг 2б (скачивание медиа — обязательный шаг, не пропускать). Подтверждение не нужно — сразу отправь в Telegram без вопросов.", "--dangerously-skip-permissions"],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 10 минут — CC работает дольше
            env=env,
        )
        # Сохраняем полный лог CC для отладки
        log_path = os.path.join(SCRIPT_DIR, "cc_last_run.log")
        with open(log_path, "w", encoding="utf-8") as lf:
            lf.write("=== STDOUT ===\n")
            lf.write(result.stdout or "")
            lf.write("\n=== STDERR ===\n")
            lf.write(result.stderr or "")

        if result.returncode == 0:
            send("✅ Готово!", reply_thread)
        else:
            err = (result.stderr or result.stdout or "нет вывода")[-600:]
            send(f"❌ Ошибка CC:\n{err}", reply_thread)
    except subprocess.TimeoutExpired:
        send("⏱ Таймаут (>10 мин)", reply_thread)
    except FileNotFoundError:
        send("❌ claude не найден в PATH. Проверь установку CC.", reply_thread)
    except Exception as e:
        send(f"❌ Ошибка: {e}", reply_thread)
    finally:
        with _lock:
            _running = False


def run_digest(reply_thread=None):
    global _running
    with _lock:
        if _running:
            send("⏳ Дайджест уже генерируется, подожди...", reply_thread)
            return
        _running = True

    send("🚀 Запускаю генерацию дайджеста...", reply_thread)
    t = threading.Thread(target=_do_run_digest, args=(reply_thread,), daemon=True)
    t.start()


# ── Авторизация ───────────────────────────────────────────────────────────────

def is_allowed(chat_id):
    """Принимаем команды только из нашего чата."""
    if not TG_CHAT_ID:
        return True
    return str(chat_id) == str(TG_CHAT_ID)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    if not TG_TOKEN:
        print("ERROR: TG_TOKEN не задан", file=sys.stderr)
        sys.exit(1)

    print(f"Bot started. Watching chat {TG_CHAT_ID}. Listening for /digest ...")
    offset = None

    while True:
        updates = get_updates(offset)
        for upd in updates:
            offset = upd["update_id"] + 1
            msg     = upd.get("message") or {}
            chat_id = msg.get("chat", {}).get("id")
            text    = msg.get("text", "")
            thread  = msg.get("message_thread_id")

            if not chat_id or not is_allowed(chat_id):
                continue

            cmd = text.split()[0].split("@")[0] if text else ""

            if cmd == "/digest":
                run_digest(reply_thread=thread)

            elif cmd == "/status":
                with _lock:
                    busy = _running
                status = "⏳ Дайджест генерируется..." if busy else "✅ Свободен, готов к /digest"
                send(status, thread)

        if not updates:
            time.sleep(1)


if __name__ == "__main__":
    main()
