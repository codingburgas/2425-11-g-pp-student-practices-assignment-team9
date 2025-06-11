from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from .. import db
from ..auth.models import User
from ..student.forms import SettingsForm
from ..student.models import VideoSubmission
from . import teacher_bp

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        return "Access denied", 403

    submissions = VideoSubmission.query.all()
    return render_template('teacher_dashboard.html', submissions=submissions)


@teacher_bp.route('/approve/<int:submission_id>')
@login_required
def approve_video(submission_id):
    if current_user.role != 'teacher':
        return "Access denied", 403

    submission = VideoSubmission.query.get_or_404(submission_id)
    submission.confirmed = True
    db.session.commit()
    flash('Video approved successfully.', 'success')
    return redirect(url_for('teacher.dashboard'))


@teacher_bp.route('/reject/<int:submission_id>')
@login_required
def reject_video(submission_id):
    if current_user.role != 'teacher':
        return "Access denied", 403

    submission = VideoSubmission.query.get_or_404(submission_id)
    db.session.delete(submission)
    db.session.commit()
    flash('Video rejected and deleted.', 'warning')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/settings_teacher', methods=['GET', 'POST'])
@login_required
def settings_teacher():
    if current_user.role != 'teacher':
        return "Access denied", 403

    form = SettingsForm(obj=current_user)

    if form.validate_on_submit():
        # Check for username/email conflicts
        if User.query.filter(User.username == form.username.data, User.id != current_user.id).first():
            flash('Username already taken.', 'warning')
            return redirect(url_for('teacher.settings_teacher'))

        if User.query.filter(User.email == form.email.data, User.id != current_user.id).first():
            flash('Email already in use.', 'warning')
            return redirect(url_for('teacher.settings_teacher'))

        current_user.username = form.username.data
        current_user.email = form.email.data

        # Change password only if fields are filled
        if form.new_password.data:
            if not form.current_password.data:
                flash('Current password is required to change your password.', 'warning')
            elif not current_user.verify_password(form.current_password.data):
                flash('Current password is incorrect.', 'danger')
            else:
                try:
                    current_user.password = form.new_password.data
                    flash('Password changed successfully.', 'success')
                except ValueError as ve:
                    flash(str(ve), 'danger')
                    return redirect(url_for('teacher.settings_teacher'))

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('teacher.settings_teacher'))

    return render_template('settings_teacher.html', form=form, current_user=current_user)