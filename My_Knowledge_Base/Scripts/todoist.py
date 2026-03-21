#!/usr/bin/env python3
"""
Todoist CLI Manager
Использование: python todoist.py
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

API_TOKEN = "18b7ba53e343ec809d939eeb93fc806e560f01a1"
BASE_URL = "https://api.todoist.com/api/v1"

PRIORITY_LABELS = {1: "🔴 P1", 2: "🟠 P2", 3: "🔵 P3", 4: "⚪ P4"}


def api(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode()
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        print(f"  ❌ Ошибка {e.code}: {e.read().decode()}")
        return None


def get_projects():
    result = api("GET", "projects")
    if result is None:
        return []
    # New API returns {"results": [...]} with pagination
    if isinstance(result, dict):
        return result.get("results", result.get("projects", []))
    return result


def get_tasks(project_id=None):
    params = {}
    if project_id:
        params["project_id"] = project_id
    endpoint = "tasks"
    if params:
        endpoint += "?" + urllib.parse.urlencode(params)
    result = api("GET", endpoint)
    if result is None:
        return []
    if isinstance(result, dict):
        return result.get("results", result.get("items", []))
    return result


def print_tasks(tasks, show_project=False, projects_map=None):
    if not tasks:
        print("  (нет задач)")
        return
    for t in tasks:
        pri = PRIORITY_LABELS.get(t.get("priority", 4), "⚪")
        due = ""
        if t.get("due"):
            due = f"  📅 {t['due']['date']}"
        proj = ""
        if show_project and projects_map:
            pname = projects_map.get(t.get("project_id"), "?")
            proj = f"  [{pname}]"
        print(f"  {pri}  {t['id'][-6:]}  {t['content']}{due}{proj}")


def cmd_list(projects_map):
    print("\n📋 ВСЕ АКТИВНЫЕ ЗАДАЧИ\n")
    tasks = get_tasks()
    print_tasks(tasks, show_project=True, projects_map=projects_map)


def cmd_today(projects_map):
    today = datetime.now().strftime("%Y-%m-%d")
    all_tasks = get_tasks()
    tasks = [
        t for t in all_tasks
        if t.get("due") and t["due"]["date"] <= today
    ]
    print(f"\n📅 ЗАДАЧИ НА СЕГОДНЯ И ПРОСРОЧЕННЫЕ ({today})\n")
    print_tasks(tasks, show_project=True, projects_map=projects_map)


def cmd_projects(projects):
    print("\n📁 ПРОЕКТЫ\n")
    for p in projects:
        print(f"  {p['id'][-6:]}  {p['name']}")


def cmd_project_tasks(projects):
    print("\nВыберите проект:")
    for i, p in enumerate(projects, 1):
        print(f"  {i}. {p['name']}")
    try:
        idx = int(input("\nНомер: ")) - 1
        project = projects[idx]
    except (ValueError, IndexError):
        print("  ❌ Неверный номер")
        return
    tasks = get_tasks(project["id"])
    print(f"\n📁 {project['name']}\n")
    print_tasks(tasks)


def cmd_add(projects):
    print("\n➕ НОВАЯ ЗАДАЧА\n")
    content = input("  Название: ").strip()
    if not content:
        print("  ❌ Название не может быть пустым")
        return

    print("  Приоритет: 1=🔴 P1  2=🟠 P2  3=🔵 P3  4=⚪ P4 (Enter=P4)")
    pri_input = input("  Приоритет: ").strip()
    priority = int(pri_input) if pri_input in ("1", "2", "3", "4") else 4

    due = input("  Дата (YYYY-MM-DD, Enter=без даты): ").strip()

    print("  Проект (Enter=Входящие):")
    for i, p in enumerate(projects, 1):
        print(f"    {i}. {p['name']}")
    proj_input = input("  Номер проекта: ").strip()
    project_id = None
    if proj_input.isdigit():
        idx = int(proj_input) - 1
        if 0 <= idx < len(projects):
            project_id = projects[idx]["id"]

    payload = {"content": content, "priority": priority}
    if due:
        payload["due_date"] = due
    if project_id:
        payload["project_id"] = project_id

    result = api("POST", "tasks", payload)
    if result:
        print(f"\n  ✅ Задача создана: {result['content']}")


def cmd_complete():
    print("\n✅ ЗАВЕРШИТЬ ЗАДАЧУ\n")
    tasks = get_tasks()
    print_tasks(tasks)
    task_id_short = input("\n  Введите последние 6 символов ID задачи: ").strip()
    matched = [t for t in tasks if t["id"].endswith(task_id_short)]
    if not matched:
        print("  ❌ Задача не найдена")
        return
    task = matched[0]
    confirm = input(f"  Завершить «{task['content']}»? (y/n): ").strip().lower()
    if confirm == "y":
        result = api("POST", f"tasks/{task['id']}/close", {})
        if result is not None:
            print("  ✅ Задача завершена!")


def cmd_delete():
    print("\n🗑️  УДАЛИТЬ ЗАДАЧУ\n")
    tasks = get_tasks()
    print_tasks(tasks)
    task_id_short = input("\n  Введите последние 6 символов ID задачи: ").strip()
    matched = [t for t in tasks if t["id"].endswith(task_id_short)]
    if not matched:
        print("  ❌ Задача не найдена")
        return
    task = matched[0]
    confirm = input(f"  ⚠️  Удалить «{task['content']}»? (y/n): ").strip().lower()
    if confirm == "y":
        api("DELETE", f"tasks/{task['id']}")
        print("  🗑️  Задача удалена.")


def cmd_update():
    print("\n✏️  РЕДАКТИРОВАТЬ ЗАДАЧУ\n")
    tasks = get_tasks()
    print_tasks(tasks)
    task_id_short = input("\n  Введите последние 6 символов ID задачи: ").strip()
    matched = [t for t in tasks if t["id"].endswith(task_id_short)]
    if not matched:
        print("  ❌ Задача не найдена")
        return
    task = matched[0]
    print(f"\n  Редактирую: {task['content']}")

    new_content = input(f"  Новое название (Enter=оставить): ").strip()
    print("  Приоритет: 1=🔴 2=🟠 3=🔵 4=⚪ (Enter=оставить)")
    new_pri = input("  Приоритет: ").strip()
    new_due = input("  Новая дата (YYYY-MM-DD, Enter=оставить): ").strip()

    payload = {}
    if new_content:
        payload["content"] = new_content
    if new_pri in ("1", "2", "3", "4"):
        payload["priority"] = int(new_pri)
    if new_due:
        payload["due_date"] = new_due

    if payload:
        result = api("POST", f"tasks/{task['id']}", payload)
        if result:
            print("  ✅ Задача обновлена!")
    else:
        print("  (ничего не изменено)")


def main():
    print("\n" + "═" * 50)
    print("   TODOIST MANAGER  //  python скрипт")
    print("═" * 50)

    projects = get_projects()
    if projects is None:
        print("\n❌ Не удалось подключиться. Проверьте токен.\n")
        return
    print(f"\n  ✅ Подключено. Проектов: {len(projects)}, задач: {len(get_tasks())}")

    projects_map = {p["id"]: p["name"] for p in projects}

    MENU = {
        "1": ("📋 Все задачи",        lambda: cmd_list(projects_map)),
        "2": ("📅 Задачи на сегодня", lambda: cmd_today(projects_map)),
        "3": ("📁 По проекту",        lambda: cmd_project_tasks(projects)),
        "4": ("📁 Список проектов",   lambda: cmd_projects(projects)),
        "5": ("➕ Добавить задачу",   lambda: cmd_add(projects)),
        "6": ("✅ Завершить задачу",  cmd_complete),
        "7": ("✏️  Редактировать",     cmd_update),
        "8": ("🗑️  Удалить задачу",   cmd_delete),
        "0": ("🚪 Выход",             None),
    }

    while True:
        print("\n─── МЕНЮ " + "─" * 42)
        for key, (label, _) in MENU.items():
            print(f"  {key}.  {label}")
        print()

        choice = input("  Выберите действие: ").strip()

        if choice == "0":
            print("\n  До свидания!\n")
            break
        elif choice in MENU:
            _, action = MENU[choice]
            action()
        else:
            print("  ❌ Неверный выбор")


if __name__ == "__main__":
    main()
