#!/usr/bin/env python3
"""
Todoist Fetch Script — выгружает все задачи и проекты в JSON для анализа.
Использование: python todoist_fetch.py
"""
import json
import urllib.request
import sys
from datetime import datetime, timezone

TOKEN = "18b7ba53e343ec809d939eeb93fc806e560f01a1"
BASE_URL = "https://api.todoist.com/api/v1"


def api_get(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, dict):
                return data.get("results", data.get("items", data))
            return data
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return []


def main():
    tasks = api_get("tasks")
    projects = api_get("projects")
    sections = api_get("sections")

    # Build project map
    proj_map = {p["id"]: p["name"] for p in projects}
    sect_map = {s["id"]: s["name"] for s in sections} if sections else {}

    # Enrich tasks
    now = datetime.now(timezone.utc)
    enriched = []
    for t in tasks:
        due = t.get("due")
        due_date = due.get("date") if due else None
        added_at = t.get("added_at", "")
        updated_at = t.get("updated_at", "")

        # Calculate days overdue
        days_overdue = None
        if due_date:
            try:
                due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                if due_dt.tzinfo is None:
                    due_dt = datetime.strptime(due_date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                days_overdue = (now - due_dt).days
            except Exception:
                pass

        # Days since created
        days_since_created = None
        if added_at:
            try:
                created_dt = datetime.fromisoformat(added_at.replace("Z", "+00:00"))
                days_since_created = (now - created_dt).days
            except Exception:
                pass

        # Days since last update
        days_since_updated = None
        if updated_at:
            try:
                upd_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                days_since_updated = (now - upd_dt).days
            except Exception:
                pass

        enriched.append({
            "id": t.get("id"),
            "content": t.get("content", ""),
            "description": t.get("description", ""),
            "priority": t.get("priority", 4),
            "project_id": t.get("project_id"),
            "project_name": proj_map.get(t.get("project_id"), "Входящие"),
            "section_id": t.get("section_id"),
            "section_name": sect_map.get(t.get("section_id"), ""),
            "parent_id": t.get("parent_id"),
            "labels": t.get("labels", []),
            "due_date": due_date,
            "days_overdue": days_overdue,
            "added_at": added_at,
            "updated_at": updated_at,
            "days_since_created": days_since_created,
            "days_since_updated": days_since_updated,
            "note_count": t.get("note_count", 0),
        })

    result = {
        "fetched_at": now.isoformat(),
        "total_tasks": len(enriched),
        "total_projects": len(projects),
        "projects": [{"id": p["id"], "name": p["name"]} for p in projects],
        "tasks": enriched,
    }

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
