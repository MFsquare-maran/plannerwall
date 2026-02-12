# app.py
from flask import Flask

from config import Config
from extensions import init_extensions
from web import register_blueprints


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="web/templates",
        static_folder="web/static",
    )
    app.config.from_object(Config)

    init_extensions(app)
    register_blueprints(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", port=5000, debug=True, use_reloader=False)
