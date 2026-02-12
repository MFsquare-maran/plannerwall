# web/routes.py
from datetime import datetime

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from services.auth_msal import (
    build_msal_app,
    get_token_silent,
    load_cache,
    redirect_uri,
    save_cache,
)
from services.graph import graph_get
from services.planner import get_board_groups
from services.weather import get_weather_bern
from services.aare import get_aare_temp
from services.transit import get_transit_departures



bp = Blueprint("web", __name__)

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


@bp.route("/")
def index():
    return render_template("index.html", redirect_uri=redirect_uri())


@bp.route("/login")
def login():
    cache = load_cache()
    cca = build_msal_app(cache=cache)
    auth_url = cca.get_authorization_request_url(
        scopes=current_app.config["SCOPES"],
        redirect_uri=redirect_uri(),
        prompt="select_account",
    )
    save_cache(cache)
    return redirect(auth_url)


@bp.route("/auth/callback")
def auth_callback():
    if request.args.get("error"):
        return (
            render_template(
                "index.html",
                redirect_uri=redirect_uri(),
                auth_error=request.args.get("error"),
                auth_error_description=request.args.get("error_description"),
            ),
            400,
        )

    code = request.args.get("code")
    if not code:
        return render_template("index.html", redirect_uri=redirect_uri(), auth_error="Missing code"), 400

    cache = load_cache()
    cca = build_msal_app(cache=cache)
    result = cca.acquire_token_by_authorization_code(
        code,
        scopes=current_app.config["SCOPES"],
        redirect_uri=redirect_uri(),
    )
    save_cache(cache)

    if "access_token" not in result:
        return (
            render_template(
                "index.html",
                redirect_uri=redirect_uri(),
                auth_error="Token error",
                token_result=result,
            ),
            400,
        )

    return redirect(url_for("web.planner_board"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.index"))


@bp.route("/me")
def me():
    token_result = get_token_silent()
    if not token_result or "access_token" not in token_result:
        return redirect(url_for("web.login"))

    me_obj = graph_get(
        "/me?$select=id,displayName,mail,userPrincipalName",
        token_result["access_token"],
        base=current_app.config["GRAPH_V1"],
    )
    return render_template("me.html", me=me_obj)


@bp.route("/planner/board")
def planner_board():
    # KW, Datum & Zeit
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    iso_week = f"{now.isocalendar().week:02d}"

    weekday = WEEKDAYS_DE[now.weekday()]      # Mo..So
    current_date = now.strftime("%d.%m.%Y")   # 02.02.2026

    # Wetter & Aare
    weather = get_weather_bern(location_label=current_app.config["WEATHER_LOCATION_LABEL"])
    aare = get_aare_temp(
        label=current_app.config["AARE_LABEL"],
        city=current_app.config["AARE_CITY"],
        timeout_s=current_app.config["AARE_TIMEOUT_S"],
        url_template=current_app.config["AARE_URL"],
        app_id=current_app.config["AARE_APP"],
        version=current_app.config["AARE_VERSION"],
    )

    # Abfahrten abrufen
    departures = get_transit_departures(max_minutes=current_app.config.get("TRANSIT_MAX_MINUTES", 15), limit=10)

    # Auth
    token_result = get_token_silent()
    if not token_result or "access_token" not in token_result:
        return redirect(url_for("web.login"))

    # Planner Board Daten
    groups, debug_notes = get_board_groups(
        token=token_result["access_token"],
        plan_id=current_app.config["PLAN_ID"],
        graph_base=current_app.config["GRAPH_V1"],
        debug_print=current_app.config["DEBUG_PRINT_TO_TERMINAL"],
        debug_collect=current_app.config["DEBUG_SHOW_ON_PAGE"],
    )

    return render_template(
        "board.html",
        groups=groups,
        debug_show=current_app.config["DEBUG_SHOW_ON_PAGE"],
        debug_notes=debug_notes,
        weather=weather,
        aare=aare,
        departures=departures,  # Übergabe der Abfahrtsdaten an das Template
        current_time=current_time,
        iso_week=iso_week,
        weekday=weekday,
        current_date=current_date,
    )
