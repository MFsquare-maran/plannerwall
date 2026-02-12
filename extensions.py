# extensions.py
from flask_session import Session

sess = Session()


def init_extensions(app):
    sess.init_app(app)
