import requests
from datetime import datetime
from zoneinfo import ZoneInfo

SEARCHCH_STATIONBOARD_URL = "https://fahrplan.search.ch/api/stationboard.json"

def get_transit_departures(
    *,
    max_minutes: int = 20,
    limit: int = 10,
    stop: str = "Bern, Gewerbeschule",
    direction_contains: str = "Länggasse",
    timeout: float = 6.0,
) -> list[dict]:
    """
    Holt Abfahrten ab 'stop' und filtert auf 'direction_contains' (z.B. Länggasse)
    sowie auf die nächsten 'max_minutes'. Gibt max. 'limit' Einträge zurück.

    Rückgabeformat:
      [{"line": "...", "direction": "...", "mins": 5}, ...]
    """
    departures: list[dict] = []

    # Lokale Zeit für Bern/CH
    tz = ZoneInfo("Europe/Zurich")
    now = datetime.now(tz)

    params = {
        "stop": stop,
        # Optional: du könntest hier auch "limit" an die API geben,
        # aber wir begrenzen zuverlässig im Code.
        # "limit": 50,
    }

    try:
        r = requests.get(
            SEARCHCH_STATIONBOARD_URL,
            params=params,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        # Wenn du lieber Exceptions nach oben werfen willst: `raise`
        return departures

    for conn in data.get("connections", []) or []:
        if len(departures) >= limit:
            break

        try:
            direction = (conn.get("terminal") or {}).get("name") or ""
            if direction_contains and direction_contains.lower() not in direction.lower():
                continue

            line = conn.get("line") or conn.get("number") or conn.get("name") or ""

            # search.ch liefert typischerweise: "YYYY-MM-DD HH:MM:SS"
            time_str = conn.get("time")
            if not time_str:
                continue

            dep_naive = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            dep = dep_naive.replace(tzinfo=tz)

            mins = int((dep - now).total_seconds() // 60)

            # Nur zukünftige Abfahrten im Fenster
            if mins < 0:
                continue

            if mins is not None and mins <= max_minutes:
                departures.append({
                    "line": line,
                    "direction": direction,
                    "mins": mins
                })
        except Exception:
            continue

    return departures
