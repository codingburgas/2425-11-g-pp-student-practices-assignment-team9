from datetime import datetime

from .. import db

class Survey(db.Model):
    __tablename__ = 'survey'
    id = db.Column(db.Integer, primary_key=True)

    class_section = db.Column(db.String(10), nullable=False)
    study_time = db.Column(db.String(20), nullable=False)
    interest_level = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.String(20), nullable=False)
    memory_method = db.Column(db.String(20), nullable=False)
    online_learning = db.Column(db.String(20), nullable=False)
    hardest_subject = db.Column(db.String(30), nullable=False)
    favorite_subject = db.Column(db.String(30), nullable=False)
    social_time = db.Column(db.String(20), nullable=False)

    # For multiple checkboxes, store as comma-separated string
    video_platforms = db.Column(db.String(100), nullable=True)
    video_helpful = db.Column(db.String(20), nullable=False)
    lesson_quality = db.Column(db.String(100), nullable=True)
    ideal_length = db.Column(db.String(20), nullable=False)
    videos_for_tests = db.Column(db.String(20), nullable=False)
    review_before_class = db.Column(db.String(20), nullable=False)


class VideoSubmission(db.Model):
    __tablename__ = 'video_submissions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_link = db.Column(db.String(500), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)

    student = db.relationship('User', backref='video_submissions')


from datetime import datetime

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))  # Optional
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='posts')
    likes = db.relationship('Like', backref='post', cascade='all, delete-orphan')

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


    # Optional: Unique constraint to prevent duplicate likes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_like'),
    )


