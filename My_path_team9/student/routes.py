from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import student_bp
from .forms import SurveyForm
from .. import db
from .models import Survey

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
        return redirect(url_for('student.survey'))  # Redirect to avoid form resubmission

    return render_template('survey.html', form=form, current_user=current_user)
