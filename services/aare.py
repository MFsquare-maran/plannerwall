# services/aare.py
import requests

from utils.env import pick


def get_aare_temp(
    label: str,
    city: str,
    timeout_s: float = 3.0,
    url_template: str = "",
    app_id: str = "planner.wall",
    version: str = "1.0.0",
) -> dict:
    try:
        if url_template:
            url = url_template.replace("{AARE_CITY}", city)
            resp = requests.get(url, timeout=timeout_s)
            resp.raise_for_status()
            data = resp.json() or {}
        else:
            url = "https://aareguru.existenz.ch/v2018/current"
            params = {"city": city, "app": app_id, "version": version}
            resp = requests.get(url, params=params, timeout=timeout_s)
            resp.raise_for_status()
            data = resp.json() or {}

        temperature = (
            pick(data, "aare.temperature")
            or pick(data, "bueber.temperature")
            or (data.get("temperature") if isinstance(data, dict) else None)
        )

        if temperature is not None:
            t = float(temperature)
            return {"label": label, "temp": f"{t:.1f}°C"}

        temperature_text = (
            pick(data, "aare.temperature_text")
            or pick(data, "bueber.temperature_text")
            or (data.get("temperature_text") if isinstance(data, dict) else None)
        )
        if temperature_text:
            return {"label": label, "temp": str(temperature_text)}

        return {"label": label, "temp": "--"}
    except Exception:
        return {"label": label, "temp": "--"}
