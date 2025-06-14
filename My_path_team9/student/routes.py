from flask import render_template, flash, redirect, url_for, request, session, abort
from flask_login import login_required, current_user
from . import student_bp
from .forms import SurveyForm, SettingsForm
from .. import db
from ..auth.models import User
from .models import Survey, Post, Like
from .forms import VideoSubmissionForm
from .models import VideoSubmission
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

@student_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'student':
        return "Access denied", 403

    form = SettingsForm(obj=current_user)

    if form.validate_on_submit():
        # Check for username/email conflicts
        if User.query.filter(User.username == form.username.data, User.id != current_user.id).first():
            flash('Username already taken.', 'warning')
            return redirect(url_for('student.settings'))

        if User.query.filter(User.email == form.email.data, User.id != current_user.id).first():
            flash('Email already in use.', 'warning')
            return redirect(url_for('student.settings'))

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
                    return redirect(url_for('student.settings'))

        db.session.commit()
        flash('Profile updated successfully.', 'success')
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
        # Redirect to recommendations page instead of back to survey
        return redirect(url_for('student.recommendations', survey_id=response.id))

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

@student_bp.route('/find_friends')
def find_friends():
    all_students = User.query.all()
    return render_template('find_friends.html', students=all_students)

@student_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)

    # Map: post.id -> whether the current user liked it
    likes_map = {post.id: any(like.user_id == current_user.id for like in post.likes) for post in user.posts}

    return render_template('profile.html', user=user, likes_map=likes_map)


@student_bp.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    if request.method == 'POST':
        content = request.form.get('content')
        if not content.strip():
            flash("Post content can't be empty.", "warning")
        else:
            new_post = Post(content=content, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash("Post added successfully!", "success")
            return redirect(url_for('student.my_posts'))

    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('my_posts.html', posts=posts)

@student_bp.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        content = request.form.get('content')
        post.content = content
        db.session.commit()
        flash("Post updated!", "success")
        return redirect(url_for('student.my_posts'))

    return render_template('edit_post.html', post=post)


@student_bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for('student.my_posts'))


@student_bp.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if existing_like:
        # Already liked — remove like
        db.session.delete(existing_like)
    else:
        # Not liked yet — add like
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)

    db.session.commit()
    return redirect(request.referrer or url_for('student.profile'))


@student_bp.route('/recommendations/<int:survey_id>')
@login_required
def recommendations(survey_id):
    if current_user.role != 'student':
        return "Access denied", 403

    # Get the survey data
    survey = Survey.query.get_or_404(survey_id)

    # Get all video submissions
    all_videos = VideoSubmission.query.filter_by(confirmed=True).all()

    if not all_videos:
        # If no videos are available, return empty recommendations
        return render_template('recommendations.html', recommendations=[])

    # Prepare survey data for logistic regression
    # We'll use key features from the survey that might influence video preferences
    features = []

    # Convert categorical variables to numerical using one-hot encoding
    # For simplicity, we'll use a few key features

    # Memory method (direct indicator of preference for videos)
    memory_method_map = {'notes': 0, 'videos': 1, 'repetition': 0.5}
    memory_method_value = memory_method_map.get(survey.memory_method, 0)

    # Online learning frequency
    online_learning_map = {'daily': 1, 'few_times': 0.75, 'rarely': 0.25, 'never': 0}
    online_learning_value = online_learning_map.get(survey.online_learning, 0)

    # Video helpfulness
    video_helpful_map = {'very': 1, 'somewhat': 0.7, 'not_much': 0.3, 'not_at_all': 0}
    video_helpful_value = video_helpful_map.get(survey.video_helpful, 0)

    # Videos for tests
    videos_for_tests_map = {'always': 1, 'sometimes': 0.7, 'only_if_needed': 0.4, 'never': 0}
    videos_for_tests_value = videos_for_tests_map.get(survey.videos_for_tests, 0)

    # Combine features
    X = np.array([
        memory_method_value,
        online_learning_value,
        video_helpful_value,
        videos_for_tests_value
    ])

    # Simple logistic regression model
    # In a real application, this would be trained on historical data
    # For now, we'll use a simple heuristic approach

    # Calculate a score for each video based on the features
    recommendations = []

    for video in all_videos:
        # Calculate a score based on the features
        # This is a simplified approach - in a real application, you would use a trained model
        score = (memory_method_value * 0.3 + 
                online_learning_value * 0.2 + 
                video_helpful_value * 0.3 + 
                videos_for_tests_value * 0.2)

        # Normalize score to be between 0 and 1
        score = min(max(score, 0), 1)

        # Generate a reason for the recommendation
        reason = "This video matches your learning preferences"

        if memory_method_value > 0.7:
            reason += " and your preference for video-based learning"

        if video_helpful_value > 0.7:
            reason += " and aligns with how helpful you find videos"

        if survey.hardest_subject in video.video_link.lower():
            reason += f" and may help with your challenging subject ({survey.hardest_subject})"
            score += 0.1  # Boost score for videos matching difficult subjects

        # Add to recommendations
        recommendations.append({
            'video': video,
            'score': min(score, 1.0),  # Cap at 1.0
            'reason': reason
        })

    # Sort recommendations by score (highest first)
    recommendations.sort(key=lambda x: x['score'], reverse=True)

    # Limit to top 5 recommendations
    recommendations = recommendations[:5]

    return render_template('recommendations.html', recommendations=recommendations)
