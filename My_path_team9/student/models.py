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
