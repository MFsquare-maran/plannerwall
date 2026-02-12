# services/graph.py
import requests


def graph_get(path: str, token: str, base: str):
    r = requests.get(
        f"{base}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if not r.ok:
        try:
            body = r.json()
        except Exception:
            body = r.text
        return {"_http_status": r.status_code, "_text": body, "_path": path, "_base": base}
    return r.json()


def graph_post(path: str, token: str, body: dict, base: str):
    r = requests.post(
        f"{base}{path}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    if not r.ok:
        try:
            err = r.json()
        except Exception:
            err = r.text
        return {"_http_status": r.status_code, "_text": err, "_path": path, "_base": base}
    return r.json()


def resolve_usernames_batch(user_ids: list[str], token: str, base: str) -> dict:
    user_ids = [u for u in user_ids if u]
    user_ids = list(dict.fromkeys(user_ids))
    mapping = {}
    if not user_ids:
        return mapping

    for i in range(0, len(user_ids), 20):
        chunk = user_ids[i : i + 20]
        batch_body = {
            "requests": [
                {"id": uid, "method": "GET", "url": f"/users/{uid}?$select=id,displayName,mail,userPrincipalName"}
                for uid in chunk
            ]
        }
        resp = graph_post("/$batch", token, batch_body, base=base)
        if "_http_status" in resp:
            for uid in chunk:
                mapping[uid] = uid
            continue

        for item in resp.get("responses", []) or []:
            uid = item.get("id")
            if item.get("status") == 200:
                b = item.get("body", {}) or {}
                mapping[uid] = b.get("displayName") or b.get("mail") or b.get("userPrincipalName") or uid
            else:
                mapping[uid] = uid

    return mapping
