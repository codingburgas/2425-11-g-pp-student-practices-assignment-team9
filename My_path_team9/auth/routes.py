from urllib import request

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User
from .. import login_manager, db

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.verify_password(form.password.data):
            login_user(user)

            if user.role == 'student':
                return redirect(url_for('student.survey'))

            elif user.role == 'teacher':
                return redirect(url_for('teacher_bp.teacher_dashboard'))
            else:
                return redirect(url_for('main_bp.index'))

        flash('Invalid username or password', 'danger')
    return render_template("login.html", form=form, current_user=current_user)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()

        if existing_user:
            flash('Username already taken. Choose another.', 'warning')
            return redirect(url_for('auth.register'))
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_email:
            flash('Email already registered. Please use another.', 'warning')
            return redirect(url_for('auth.register'))

        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                role=form.role.data)

            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError as ve:
            flash(str(ve), 'danger')  # Password validation errors
            return redirect(url_for('auth.register'))

    return render_template("register.html", form=form, current_user=current_user)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    print('Logged out successfully.')
    return redirect(url_for("main.home"))