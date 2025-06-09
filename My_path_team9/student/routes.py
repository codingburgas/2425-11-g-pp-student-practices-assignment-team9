from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from . import student_bp
from .forms import SurveyForm, SettingsForm
from .. import db
from ..auth.models import User
from .models import Survey
from .forms import VideoSubmissionForm
from .models import VideoSubmission

@student_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'student':
        return "Access denied", 403

    form = SettingsForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('This username is already taken.', 'warning')
        else:
            current_user.username = form.username.data
            db.session.commit()
            flash('Username updated successfully.', 'success')
            return redirect(url_for('student.settings'))

    return render_template('settings.html', form=form, current_user=current_user)

@student_bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    if current_user.role != 'student':
        return "Access denied", 403

    form = SurveyForm()

    if form.validate_on_submit():
        video_platforms = ','.join(form.video_platforms.data) if form.video_platforms.data else ''
        lesson_quality = ','.join(form.lesson_quality.data) if form.lesson_quality.data else ''

        response = Survey(
            class_section=form.class_section.data,
            study_time=form.study_time.data,
            interest_level=form.interest_level.data,
            confidence=form.confidence.data,
            memory_method=form.memory_method.data,
            online_learning=form.online_learning.data,
            hardest_subject=form.hardest_subject.data,
            favorite_subject=form.favorite_subject.data,
            social_time=form.social_time.data,
            video_platforms=video_platforms,
            video_helpful=form.video_helpful.data,
            lesson_quality=lesson_quality,
            ideal_length=form.ideal_length.data,
            videos_for_tests=form.videos_for_tests.data,
            review_before_class=form.review_before_class.data
        )
        db.session.add(response)
        db.session.commit()
        flash('Thank you for completing the survey.', 'success')
        return redirect(url_for('student.survey'))

    return render_template('survey.html', form=form, current_user=current_user)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('student_dashboard.html')


@student_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if current_user.role != 'student':
        return "Access denied", 403

    form = VideoSubmissionForm()

    if form.validate_on_submit():
        submission = VideoSubmission(
            student_id=current_user.id,
            video_link=form.video_link.data
        )
        db.session.add(submission)
        db.session.commit()
        flash("Video submitted successfully.", "success")
        return redirect(url_for('student.submit'))

    submissions = VideoSubmission.query.filter_by(student_id=current_user.id).all()
    return render_template('submit.html', form=form, submissions=submissions)

@student_bp.route('/tips')
@login_required
def tips():
    return render_template('tips.html')

@student_bp.route('/classes')
@login_required
def classes():
    return render_template('classes.html')