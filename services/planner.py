# services/planner.py
from __future__ import annotations

from services.graph import graph_get, resolve_usernames_batch
from utils.text import label_ends_with_ku, split_title_and_customer

INTERN_PREFIXES = ("Interne Aufträge",)


def is_done(task: dict) -> bool:
    percent = task.get("percentComplete", 0) or 0
    return percent >= 100 or bool(task.get("completedDateTime"))


def build_label_map_from_plan_details(plan_details: dict) -> dict:
    cd = (plan_details or {}).get("categoryDescriptions") or {}
    out = {}
    for k, v in cd.items():
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()
    return out


def task_labels(task: dict, label_map: dict) -> list[str]:
    ac = task.get("appliedCategories") or {}
    keys = [k for k, v in ac.items() if v is True]

    def sort_key(x: str) -> int:
        try:
            return int(x.replace("category", ""))
        except Exception:
            return 999

    keys.sort(key=sort_key)
    return [(label_map.get(k) or k) for k in keys]


def classify_task(bucket_name: str, labels: list[str]) -> str:
    """
    Regeln:
    - Wenn irgendein Label am Ende 'KU' hat => extern
    - Sonst: Bucket beginnt mit 'Interne Aufträge' => intern
    - Sonst => extern
    """
    if any(label_ends_with_ku(lab) for lab in (labels or [])):
        return "extern"

    name = (bucket_name or "").strip().lower()
    intern = tuple((p or "").strip().lower() for p in INTERN_PREFIXES)
    if any(name.startswith(p) for p in intern):
        return "intern"

    return "extern"


def get_board_groups(
    token: str,
    plan_id: str,
    graph_base: str,
    debug_print: bool = True,
    debug_collect: bool = False,
):
    debug_notes: list[str] = []

    def dbg(msg: str):
        if debug_print:
            print(msg)
        if debug_collect:
            debug_notes.append(str(msg))

    # Labels (Bezeichnung) aus Plan-Details
    plan_details = graph_get(f"/planner/plans/{plan_id}/details?$select=categoryDescriptions", token, base=graph_base)
    if "_http_status" in plan_details:
        dbg(f"DEBUG plan_details error: {plan_details}")
        label_map = {}
    else:
        label_map = build_label_map_from_plan_details(plan_details)

    # Buckets
    buckets_resp = graph_get(f"/planner/plans/{plan_id}/buckets", token, base=graph_base)
    if "_http_status" in buckets_resp:
        raise RuntimeError(f"Buckets error: {buckets_resp}")
    buckets = buckets_resp.get("value", []) or []
    bucket_id_to_name = {b["id"]: (b.get("name") or "") for b in buckets}

    # Tasks
    tasks_resp = graph_get(
        f"/planner/plans/{plan_id}/tasks?$select=id,title,assignments,appliedCategories,bucketId,percentComplete,completedDateTime",
        token,
        base=graph_base,
    )
    if "_http_status" in tasks_resp:
        raise RuntimeError(f"Tasks error: {tasks_resp}")

    tasks_all = tasks_resp.get("value", []) or []
    tasks_open = [t for t in tasks_all if not is_done(t)]
    dbg(f"DEBUG tasks_all={len(tasks_all)} tasks_open={len(tasks_open)}")

    # Assignees
    user_ids = []
    for t in tasks_open:
        assignments = t.get("assignments") or {}
        user_ids.extend(list(assignments.keys()))
    id_to_name = resolve_usernames_batch(user_ids, token, base=graph_base) if user_ids else {}

    def to_row(t: dict) -> dict:
        title, customer = split_title_and_customer(t.get("title") or "")
        assignments = t.get("assignments") or {}
        assignees = [id_to_name.get(uid, uid) for uid in assignments.keys()]
        labels = task_labels(t, label_map)
        bucket_name = bucket_id_to_name.get(t.get("bucketId"), "") or ""
        return {"bucket": bucket_name, "labels": labels, "title": title, "customer": customer, "assignees": assignees}

    groups = {"extern": [], "intern": []}
    side_counts = {"extern": 0, "intern": 0}

    for t in tasks_open:
        row = to_row(t)
        side = classify_task(bucket_name=row["bucket"], labels=row["labels"])
        groups[side].append(row)
        side_counts[side] = side_counts.get(side, 0) + 1

    dbg("DEBUG counts: " + ", ".join([f"{k}={side_counts.get(k, 0)}" for k in ("extern", "intern")]))

    def sort_key_row(r: dict):
        return ((r.get("customer") or "").lower(), (r.get("title") or "").lower())

    for k in groups:
        groups[k].sort(key=sort_key_row)

    return groups, debug_notes
