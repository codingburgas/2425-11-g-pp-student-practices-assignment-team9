import pytest
from My_path_team9 import create_app, db  # смени My_path_team9 с името на твоя app package
from My_path_team9.auth.models import User  # импорт на User модела (ако го ползваш)
from flask_login import login_user

class TestConfig:
    TESTING = True,
    DEBUG = True,
    PROPAGATE_EXCEPTIONS = True,
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://CloudSAd5c2a932:Viktoriq21@mypath.database.windows.net/mypath?driver=ODBC+Driver+17+for+SQL+Server"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "SECRET_KEY"

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def logged_in_student(client, app):
    with app.app_context():

        user = User(username="teststudent", email="student@test.com", role="student")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()


    response = client.post("/login", data={
        "username": "teststudent",
        "password": "password"
    }, follow_redirects=True)
    assert response.status_code == 200
    return client