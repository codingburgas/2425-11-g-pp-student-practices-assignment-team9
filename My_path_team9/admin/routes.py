from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import admin_bp
from .. import db
from ..auth.models import User
from ..teacher.models import MotivationalVideo, VideoRating
from ..student.models import VideoSubmission, Survey, Post


def admin_required(f):
    """Decorator to check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard showing all users and videos"""
    users = User.query.all()
    motivational_videos = MotivationalVideo.query.all()
    video_submissions = VideoSubmission.query.all()

    return render_template('dashboard.html',
                           users=users,
                           motivational_videos=motivational_videos,
                           video_submissions=video_submissions)


@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    """List all users with admin controls"""
    users = User.query.all()
    return render_template('users.html', users=users)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    user = User.query.get_or_404(user_id)

    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users_list'))

    # Prevent admin from deleting other admins
    if user.role == 'admin':
        flash('You cannot delete other admin accounts.', 'danger')
        return redirect(url_for('admin.users_list'))

    # Delete related records to avoid foreign key constraint issues
    Survey.query.filter_by(user_id=user.id).delete()
    VideoSubmission.query.filter_by(student_id=user.id).delete()
    Post.query.filter_by(user_id=user.id).delete()
    VideoRating.query.filter_by(student_id=user.id).delete()

    # Now delete the user
    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.username} has been deleted successfully.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user information (admin only)"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')

        # Check for conflicts
        existing_user = User.query.filter(User.username == username, User.id != user.id).first()
        if existing_user:
            flash('Username already taken.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        existing_email = User.query.filter(User.email == email, User.id != user.id).first()
        if existing_email:
            flash('Email already in use.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))

        # Update user
        user.username = username
        user.email = email
        user.role = role

        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users_list'))

    return render_template('edit_user.html', user=user)


@admin_bp.route('/videos/motivational')
@login_required
@admin_required
def motivational_videos():
    """List all motivational videos with admin controls"""
    videos = MotivationalVideo.query.all()
    return render_template('motivational_videos.html', videos=videos)


@admin_bp.route('/videos/motivational/delete/<int:video_id>', methods=['POST'])
@login_required
@admin_required
def delete_motivational_video(video_id):
    """Delete a motivational video (admin only)"""

    video = MotivationalVideo.query.get_or_404(video_id)
    title = video.title

    # Delete related video ratings to avoid foreign key constraint errors
    VideoRating.query.filter_by(video_id=video.id).delete()

    # Now delete the video
    db.session.delete(video)
    db.session.commit()

    flash(f'Motivational video "{title}" has been deleted successfully.', 'success')
    return redirect(url_for('admin.motivational_videos'))


@admin_bp.route('/videos/submissions')
@login_required
@admin_required
def video_submissions():
    """List all video submissions with admin controls"""
    submissions = VideoSubmission.query.all()
    return render_template('video_submissions.html', submissions=submissions)


@admin_bp.route('/videos/submissions/delete/<int:submission_id>', methods=['POST'])
@login_required
@admin_required
def delete_video_submission(submission_id):
    """Delete a video submission (admin only)"""
    submission = VideoSubmission.query.get_or_404(submission_id)
    video_link = submission.video_link
    db.session.delete(submission)
    db.session.commit()

    flash(f'Video submission "{video_link}" has been deleted successfully.', 'success')
    return redirect(url_for('admin.video_submissions'))
