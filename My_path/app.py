from flask import Flask
from .config import Config
from . import create_app, db

app = create_app(Config)
"""with app.app_context():
    db.create_all()"""


if __name__ == '__main__':
    app.run()