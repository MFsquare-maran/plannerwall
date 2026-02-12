# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET", "dev-secret-change-me")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(os.getcwd(), ".flask_session")
    SESSION_PERMANENT = False

    # Azure / MSAL
    AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
    AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
    AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
    AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"

    # Graph / Planner
    GRAPH_V1 = "https://graph.microsoft.com/v1.0"
    SCOPES = ["User.Read", "Tasks.Read", "Group.Read.All", "User.ReadBasic.All"]
    PLAN_ID = os.environ.get("PLAN_ID", "VgAqa7JDk0G1dc3BOtlIIZcAHdOG")

    # UI / Branding
    BRAND_NAME = os.environ.get("BRAND_NAME", "Planner Board")
    BRAND_LOGO_URL = (os.environ.get("BRAND_LOGO_URL", "") or "").strip()
    BRAND_PAGE_BG_URL = (os.environ.get("BRAND_PAGE_BG_URL", "") or "").strip()

    # Debug
    DEBUG_SHOW_ON_PAGE = os.environ.get("DEBUG_SHOW_ON_PAGE", "0").lower() in ("1", "true", "yes")
    DEBUG_PRINT_TO_TERMINAL = os.environ.get("DEBUG_PRINT_TO_TERMINAL", "1").lower() in ("1", "true", "yes")

    # Weather
    WEATHER_LOCATION_LABEL = os.environ.get("WEATHER_LOCATION_LABEL", "Bern")

    # Aare
    AARE_LABEL = os.environ.get("AARE_LABEL", "Aare")
    AARE_CITY = os.environ.get("AARE_CITY", "bern").lower()
    AARE_TIMEOUT_S = float(os.environ.get("AARE_TIMEOUT_S", "3"))
    AARE_URL = (os.environ.get("AARE_URL", "") or "").strip()
    AARE_APP = os.environ.get("AARE_APP", "planner.wall")
    AARE_VERSION = os.environ.get("AARE_VERSION", "1.0.0")
