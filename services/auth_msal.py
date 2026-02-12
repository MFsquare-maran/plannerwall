# services/auth_msal.py
import msal
from flask import current_app, request, session


def redirect_uri() -> str:
    base = request.host_url.rstrip("/")
    return f"{base}/auth/callback"


def load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def save_cache(cache: msal.SerializableTokenCache) -> None:
    session["token_cache"] = cache.serialize()


def build_msal_app(cache=None) -> msal.ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        current_app.config["AZURE_CLIENT_ID"],
        authority=current_app.config["AUTHORITY"],
        client_credential=current_app.config["AZURE_CLIENT_SECRET"],
        token_cache=cache,
    )


def get_token_silent():
    cache = load_cache()
    cca = build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if not accounts:
        return None
    result = cca.acquire_token_silent(current_app.config["SCOPES"], account=accounts[0])
    save_cache(cache)
    return result
