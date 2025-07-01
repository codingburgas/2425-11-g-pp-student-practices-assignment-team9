from flask import render_template, flash, redirect, url_for, request, session, abort
from flask_login import login_required, current_user
from . import student_bp
from .forms import SurveyForm, SettingsForm
from .. import db
from ..auth.models import User
from .models import Survey, Post, Like
from .forms import VideoSubmissionForm
from .models import VideoSubmission
from .ai_recommender import initialize_recommender, recommender


@student_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
        Allows students to update their profile settings including username, email, and password.

        Returns:
            Renders the settings form or redirects with success/error messages.
        """
    if not current_user.is_authenticated or current_user.role != 'student':
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
    """
        Allows students to submit a learning preference and study habits survey.

        Returns:
            Renders the survey form or redirects to the recommendation page.
        """
    if current_user.role != 'student':
        return "Access denied", 403

    form = SurveyForm()

    if form.validate_on_submit():
        try:
            # Handle checkbox fields more robustly
            video_platforms = []
            if form.video_platforms.data:
                video_platforms = form.video_platforms.data
            video_platforms_str = ','.join(video_platforms) if video_platforms else ''
            
            lesson_quality = []
            if form.lesson_quality.data:
                lesson_quality = form.lesson_quality.data
            lesson_quality_str = ','.join(lesson_quality) if lesson_quality else ''

            response = Survey(
                user_id=current_user.id,
                class_section=form.class_section.data,
                study_time=form.study_time.data,
                interest_level=form.interest_level.data,
                confidence=form.confidence.data,
                memory_method=form.memory_method.data,
                online_learning=form.online_learning.data,
                hardest_subject=form.hardest_subject.data,
                favorite_subject=form.favorite_subject.data,
                social_time=form.social_time.data,
                video_platforms=video_platforms_str,
                video_helpful=form.video_helpful.data,
                lesson_quality=lesson_quality_str,
                ideal_length=form.ideal_length.data,
                videos_for_tests=form.videos_for_tests.data,
                review_before_class=form.review_before_class.data
            )
            db.session.add(response)
            db.session.commit()
            flash('Thank you for completing the survey.', 'success')
            
            # Redirect to recommendations page instead of back to survey
            return redirect(url_for('student.recommendations', survey_id=response.id))
            
        except Exception as e:
            print(f"Error saving survey: {e}")
            db.session.rollback()
            flash('There was an error saving your survey. Please try again.', 'danger')
            return redirect(url_for('student.survey'))
    else:
        # Show validation errors if any
        if form.errors:
            flash('Please fill in all required fields correctly.', 'warning')

    return render_template('survey.html', form=form, current_user=current_user)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return "Access denied", 403

    try:
        # Motivational videos (existing logic)
        videos = MotivationalVideo.query.all()
        video_data = []
        for video in videos:
            ratings = [r.rating for r in video.ratings]
            avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None
            my_rating = next((r.rating for r in video.ratings if r.student_id == current_user.id), None)
            video_data.append({
                'video': video,
                'average_rating': avg_rating,
                'my_rating': my_rating
            })

        # --- NEW: Get recommendations for the current student ---
        # Get the latest survey for the current user
        survey = Survey.query.filter_by(user_id=current_user.id).order_by(Survey.id.desc()).first()
        recommended_videos = []
        if survey:
            # Get all available videos (submitted + motivational)
            submitted_videos = VideoSubmission.query.all()
            motivational_videos = MotivationalVideo.query.all()
            all_videos = list(submitted_videos) + list(motivational_videos)
            
            # Initialize recommender if needed
            try:
                initialize_recommender()
                recommended_videos = recommender.get_recommendations(survey, all_videos, top_k=5)
            except Exception as e:
                print(f"Error getting recommendations for dashboard: {e}")
                recommended_videos = []

        return render_template(
            'student_dashboard.html',
            videos=video_data,
            recommended_videos=recommended_videos
        )
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        flash('There was an error loading the dashboard. Please try again.', 'warning')
        return render_template('student_dashboard.html', videos=[], recommended_videos=[])

@student_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    """
        Allows students to submit educational video links.

        Returns:
            Renders the submission form or refreshes the page with submission list.
        """
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
    """
        Displays academic tips for students.

        Returns:
            Tips HTML page.
        """
    return render_template('tips.html')

@student_bp.route('/classes')
@login_required
def classes():
    """
      Displays available classes to students.

      Returns:
          Classes HTML page.
      """
    return render_template('classes.html')

@student_bp.route('/find_friends')
def find_friends():
    """
        Displays all student profiles for social interaction.

        Returns:
            Find friends page with a list of students.
        """
    all_students = User.query.all()
    return render_template('find_friends.html', students=all_students)

@student_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    """
        Displays a specific user's profile including their posts and like status.

        Args:
            user_id (int): The ID of the user to view.

        Returns:
            Profile page for the selected user.
        """
    user = User.query.get_or_404(user_id)

    # Map: post.id -> whether the current user liked it
    likes_map = {post.id: any(like.user_id == current_user.id for like in post.likes) for post in user.posts}

    return render_template('profile.html', user=user, likes_map=likes_map)


@student_bp.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    """
        Allows students to view and add their own posts.

        Returns:
            The user's posts page or refresh after adding a new post.
        """
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
    """
        Allows students to edit their existing post.

        Args:
            post_id (int): The ID of the post to edit.

        Returns:
            Post editing page or redirect after update.
        """
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
    """
       Deletes a student's post.

       Args:
           post_id (int): The ID of the post to delete.

       Returns:
           Redirect to the posts page after deletion.
       """
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
    """
       Toggles like status on a post for the current user.

       Args:
           post_id (int): The ID of the post to like/unlike.

       Returns:
           Redirects to the referring page or student profile.
       """
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
    """
        Recommends videos to students based on their survey data using logistic regression AI.

        Args:
            survey_id (int): The ID of the submitted survey.

        Returns:
            Renders a recommendation page with up to 5 recommended videos.
    """
    if current_user.role != 'student':
        return "Access denied", 403

    try:
        # Get the survey data
        survey = Survey.query.get_or_404(survey_id)
        
        # Verify the survey belongs to the current user
        if survey.user_id != current_user.id:
            abort(403)

        # Get all available videos (both submitted and motivational)
        submitted_videos = VideoSubmission.query.all()
        motivational_videos = MotivationalVideo.query.all()
        
        # Combine all videos
        all_videos = list(submitted_videos) + list(motivational_videos)

        if not all_videos:
            # If no videos are available, return empty recommendations
            return render_template('recommendations.html', recommendations=[], survey=survey)

        # Initialize the recommender (load existing model or train new one)
        try:
            initialize_recommender()
        except Exception as e:
            print(f"Error initializing recommender: {e}")
            # Continue with fallback method
        
        # Get AI-powered recommendations with timeout
        recommendations = []
        try:
            # Use a simpler approach without signal.SIGALRM (which doesn't work on Windows)
            recommendations = recommender.get_recommendations(survey, all_videos, top_k=5)
                
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            # No fallback recommendations - just return empty list
            recommendations = []
        
        # Add model information for transparency
        model_info = {
            'model_type': 'Logistic Regression',
            'features_used': len(recommender.feature_names),
            'is_trained': recommender.model is not None
        }

        return render_template('recommendations.html', 
                             recommendations=recommendations, 
                             survey=survey,
                             model_info=model_info)
    except Exception as e:
        print(f"Error in recommendations route: {e}")
        flash('There was an error generating recommendations. Please try again.', 'warning')
        return redirect(url_for('student.survey'))

from ..teacher.models import MotivationalVideo, VideoRating

@student_bp.route('/rate_video', methods=['POST'])
@login_required
def rate_video():
    if current_user.role != 'student':
        return "Access denied", 403

    video_id = request.form.get('video_id')
    rating_str = request.form.get('rating')

    # Validate video_id and rating presence
    if not video_id or not rating_str:
        flash('Video ID and rating are required.', 'danger')
        return redirect(url_for('student.dashboard'))

    try:
        video_id = int(video_id)
        rating = int(rating_str)
    except ValueError:
        flash('Invalid video ID or rating.', 'danger')
        return redirect(url_for('student.dashboard'))

    # Check if the video exists to avoid FK violation
    video = MotivationalVideo.query.get(video_id)
    if not video:
        flash('Video not found.', 'danger')
        return redirect(url_for('student.dashboard'))

    # Check for existing rating and update or create new
    existing = VideoRating.query.filter_by(student_id=current_user.id, video_id=video_id).first()
    if existing:
        existing.rating = rating
    else:
        new_rating = VideoRating(student_id=current_user.id, video_id=video_id, rating=rating)
        db.session.add(new_rating)

    db.session.commit()
    flash('Your rating was saved!', 'success')
    return redirect(url_for('student.dashboard'))

