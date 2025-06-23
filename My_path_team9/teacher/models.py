from .. import db
class MotivationalVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    video_link = db.Column(db.String(500), nullable=True)
    ratings = db.relationship('VideoRating', backref='video', lazy=True)

    @property
    def average_rating(self):
        if not self.ratings:
            return None
        return sum(r.rating for r in self.ratings) / len(self.ratings)

class VideoRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('motivational_video.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale