# services/weather.py
import requests


def weather_icon_from_code(code: int) -> str:
    if code in (0,):
        return "☀️"
    if code in (1, 2):
        return "⛅"
    if code in (3,):
        return "⛅"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55, 56, 57):
        return "🌦️"
    if code in (61, 63, 65, 66, 67):
        return "🌧️"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️"
    if code in (80, 81, 82):
        return "🌧️"
    if code in (95, 96, 99):
        return "⛈️"
    return "🌡️"

def get_weather_bern(location_label: str = "Bern") -> dict:
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=46.9481&longitude=7.4474"
            "&current=temperature_2m,weather_code,wind_speed_10m"
            "&timezone=Europe%2FZurich"
        )
        resp = requests.get(url, timeout=(2, 3))
        resp.raise_for_status()

        cur = (resp.json() or {}).get("current") or {}

        temp = cur.get("temperature_2m")
        code = cur.get("weather_code")
        wind = cur.get("wind_speed_10m")

        code_int = int(code) if code is not None else None
        icon = weather_icon_from_code(code_int) if code_int is not None else "🌡️"

        temp_c = float(temp) if temp is not None else None
        temp_str = "--" if temp_c is None else f"{temp_c}°C"

        return {
            "location": location_label,
            "icon": icon,
            "temp": temp_str,
        }
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {
            "location": location_label,
            "icon": "🌡️",
            "temp": "--",
        }
