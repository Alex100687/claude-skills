#!/usr/bin/env python3
"""
Ежедневный анализ Todoist → отправка 5 советов в Telegram.
Использование: python todoist_daily_report.py
"""
import json
import urllib.request
import sys
import os
from datetime import datetime, timezone

# === НАСТРОЙКИ ===
# Токены берутся из переменных окружения (не хранятся в коде)
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "")
TODOIST_BASE = "https://api.todoist.com/api/v1"
TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")


def todoist_get(endpoint):
    req = urllib.request.Request(
        f"{TODOIST_BASE}/{endpoint}",
        headers={"Authorization": f"Bearer {TODOIST_TOKEN}"}
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode("utf-8"))
        if isinstance(data, dict):
            return data.get("results", data.get("items", data))
        return data


def send_telegram(text):
    payload = json.dumps({"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read())
        return result.get("ok", False)


def analyze_tasks(tasks, projects):
    now = datetime.now(timezone.utc)
    proj_map = {p["id"]: p["name"] for p in projects}
    tips = []

    # Обогащаем задачи
    enriched = []
    for t in tasks:
        due = t.get("due")
        due_date = due.get("date") if due else None
        added_at = t.get("added_at", "")
        days_overdue = None
        days_old = None
        days_upd = None

        if due_date:
            try:
                d = datetime.fromisoformat(due_date[:10]).replace(tzinfo=timezone.utc)
                days_overdue = (now - d).days
            except Exception:
                pass

        if added_at:
            try:
                d = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
                days_old = (now - d).days
            except Exception:
                pass

        updated_at = t.get("updated_at", "")
        if updated_at:
            try:
                d = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                days_upd = (now - d).days
            except Exception:
                pass

        enriched.append({
            "id": t["id"],
            "content": t.get("content", ""),
            "priority": t.get("priority", 1),
            "project": proj_map.get(t.get("project_id"), "Входящие"),
            "due_date": due_date,
            "days_overdue": days_overdue,
            "days_old": days_old,
            "days_upd": days_upd,
            "parent_id": t.get("parent_id"),
        })

    # 1. Самая долгая просроченная задача
    overdue = [t for t in enriched if t["days_overdue"] and t["days_overdue"] > 0]
    overdue.sort(key=lambda x: x["days_overdue"], reverse=True)
    if overdue:
        t = overdue[0]
        tips.append(
            f"⏰ <b>Просрочено {t['days_overdue']} дней:</b> «{t['content'][:60]}» [{t['project']}]\n"
            f"→ Сделай сегодня или перенеси с реальной датой"
        )

    # 2. Самая старая задача без даты и без движения
    frozen = [t for t in enriched
              if not t["due_date"]
              and t["days_old"] and t["days_old"] > 180
              and t["days_upd"] and t["days_upd"] > 90]
    frozen.sort(key=lambda x: x["days_upd"], reverse=True)
    if frozen:
        t = frozen[0]
        tips.append(
            f"🧊 <b>Заморожена {t['days_upd']} дней:</b> «{t['content'][:60]}» [{t['project']}]\n"
            f"→ Удали, делегируй или поставь дедлайн — иначе она будет висеть вечно"
        )

    # 3. Задачи без приоритета (API priority=1 = P4/нет приоритета) в большом количестве
    no_prio = [t for t in enriched if t["priority"] == 1 and not t["due_date"]]
    if len(no_prio) > 5:
        tips.append(
            f"🎯 <b>Без приоритета и дедлайна: {len(no_prio)} задач</b>\n"
            f"→ Выбери 3 самые важные и поставь им P1 или дату — без этого они никогда не будут сделаны"
        )

    # 4. Расфокус: слишком много задач в одном проекте
    from collections import Counter
    proj_counts = Counter(t["project"] for t in enriched if not t["parent_id"])
    busiest_proj, count = proj_counts.most_common(1)[0]
    if count > 10:
        tips.append(
            f"📦 <b>Перегружен проект «{busiest_proj}»: {count} задач</b>\n"
            f"→ Разбей на подзадачи или создай подпроект — большой список парализует"
        )

    # 5. Задачи-placeholders (короткие, без смысла)
    vague = [t for t in enriched
             if len(t["content"].strip()) < 15
             and not t["due_date"]
             and t["days_old"] and t["days_old"] > 30]
    if vague:
        names = ", ".join(f'«{t["content"][:20]}»' for t in vague[:3])
        tips.append(
            f"✏️ <b>Размытые задачи без смысла:</b> {names}{'...' if len(vague) > 3 else ''}\n"
            f"→ Переформулируй: добавь глагол + результат, иначе мозг их игнорирует"
        )

    # Fallback если не хватает советов
    if len(tips) < 5:
        today_tasks = [t for t in enriched if t["days_overdue"] and t["days_overdue"] <= 0 and t["days_overdue"] > -3]
        if today_tasks:
            names = "\n".join(f"  • {t['content'][:50]}" for t in today_tasks[:3])
            tips.append(f"📅 <b>Ближайшие задачи:</b>\n{names}")

    return tips[:5]


def main():
    try:
        tasks_raw = todoist_get("tasks")
        projects = todoist_get("projects")
        tasks = tasks_raw if isinstance(tasks_raw, list) else []

        tips = analyze_tasks(tasks, projects)

        today = datetime.now().strftime("%d.%m.%Y")
        lines = [f"🧠 <b>Todoist Advisor | {today}</b>\n"]
        for i, tip in enumerate(tips, 1):
            lines.append(f"{i}. {tip}")

        lines.append(f"\n<i>Задач всего: {len(tasks)} | Проектов: {len(projects)}</i>")

        message = "\n\n".join(lines)
        ok = send_telegram(message)
        print("OK" if ok else "FAILED")

    except Exception as e:
        error_msg = f"⚠️ Todoist Advisor: ошибка при анализе\n{str(e)[:200]}"
        try:
            send_telegram(error_msg)
        except Exception:
            pass
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
