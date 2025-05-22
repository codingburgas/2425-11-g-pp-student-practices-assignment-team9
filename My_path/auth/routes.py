from flask import Blueprint, render_template, flash
from flask_login import login_user
from models import User
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return "Login successful!"
        else:
            flash("Wrong username or password")
    return render_template("login.html", form=form)
