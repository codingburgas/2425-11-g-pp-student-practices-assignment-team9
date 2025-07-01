from flask import url_for
from My_path_team9.auth.models import User
from My_path_team9 import db

def login_as_student(client, app):
    with app.app_context():
        from My_path_team9.auth.models import User  # Увери се, че е правилният импорт
        from My_path_team9 import db

        # Изтрий стария потребител, ако вече съществува
        existing = User.query.filter_by(email="s@example.com").first()
        if existing:
            db.session.delete(existing)
            db.session.commit()

        # Създай нов потребител
        student = User(username="teststudent", email="s@example.com", role="student")
        student.password = "Test1234"  # Паролата трябва да е валидна
        db.session.add(student)
        db.session.commit()

    # Използвай context manager, за да задържиш сесията
    with client:
        response = client.post('/auth/login', data={
            'username': 'teststudent',
            'password': 'Test1234'
        }, follow_redirects=True)
        assert b"Dashboard" in response.data or response.status_code == 200


def test_dashboard_access(client, app):
    login_as_student(client, app)
    with client:
        response = client.get('/student/dashboard')
        print(response.data.decode())
        assert response.status_code == 200

def test_settings_requires_login(client):
    response = client.get('/student/settings', follow_redirects=False)
    assert response.status_code == 302  # Redirect to login

def test_submit_video(client, app):
    login_as_student(client, app)
    response = client.post('/student/submit', data={'video_link': 'https://youtube.com/example'}, follow_redirects=True)
    assert b"Video submitted successfully" in response.data

def test_survey_submission(client, app):
    login_as_student(client, app)
    response = client.post('/survey', data={
        'class_section': 'A',
        'study_time': '2',
        'interest_level': 'high',
        'confidence': 'medium',
        'memory_method': 'videos',
        'online_learning': 'daily',
        'hardest_subject': 'Math',
        'favorite_subject': 'Physics',
        'social_time': 'medium',
        'video_platforms': ['YouTube'],
        'video_helpful': 'very',
        'lesson_quality': ['clear'],
        'ideal_length': '10',
        'videos_for_tests': 'always',
        'review_before_class': True
    }, follow_redirects=True)
    assert b"Thank you for completing the survey" in response.data