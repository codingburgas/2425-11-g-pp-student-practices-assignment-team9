from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import auth_bp
from .forms import LoginForm, RegisterForm
from .models import User
from .. import login_manager, db

# Set the login view for the login manager
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the database by ID for Flask-Login.
    Args:
        user_id (str): The ID of the user to load.
    Returns:
        User: The user object if found, otherwise None.
    """
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login requests. Renders the login form and processes form submissions.

    Returns:
        Response: A redirect to the appropriate dashboard if login is successful,
                  or a re-rendered login page with an error message on failure.
    """
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.verify_password(form.password.data):
            login_user(user)

            if user.role == 'student':
                return redirect(url_for('student.survey'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main_bp.index'))

        flash('Invalid username or password', 'danger')

    return render_template("login.html", form=form, current_user=current_user)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration requests. Renders the registration form and processes user data.

    Returns:
        Response: Redirects to login on success or re-renders the form with messages on failure.
    """
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
                role=form.role.data
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template("register.html", form=form, current_user=current_user)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logs the current user out and redirects to the home page.

    Returns:
        Response: A redirect to the main home page after logging out.
    """
    logout_user()
    print('Logged out successfully.')
    return redirect(url_for("main.home"))
