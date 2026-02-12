# web/__init__.py
from .routes import bp as web_bp


def register_blueprints(app):
    app.register_blueprint(web_bp)
