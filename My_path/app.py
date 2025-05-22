from flask import Flask
from auth.models import db, User
from flask_login import LoginManager
from auth.routes import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_user():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', password='admin')
        db.session.add(user)
        db.session.commit()


app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)
