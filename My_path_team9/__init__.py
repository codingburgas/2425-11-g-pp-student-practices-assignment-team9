from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .auth import auth_bp
    from .main import main_bp
    from .student import student_bp
    from .teacher import teacher_bp
    from .admin import admin_bp
    from .errors import register_error_handlers

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    register_error_handlers(app)

    return app
