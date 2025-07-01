from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, SelectMultipleField, widgets, SubmitField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
from wtforms.validators import URL

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SurveyForm(FlaskForm):
    class_section = RadioField('Which class and section are you in?', validators=[DataRequired()], choices=[
        ('9A', '9A'), ('9B', '9B'), ('9V', '9V'), ('9G', '9G')
    ])

    study_time = RadioField('How many hours a day do you study outside school?', validators=[DataRequired()], choices=[
        ('under_1', 'Less than 1 hour'),
        ('1_2', '1–2 hours'),
        ('2_3', '2–3 hours'),
        ('over_3', 'More than 3 hours')
    ])

    interest_level = RadioField('How interested are you in the school material?', validators=[DataRequired()], choices=[
        ('very_high', 'Very high'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('none', 'Not interested')
    ])

    confidence = RadioField('How confident do you feel before tests/exams?', validators=[DataRequired()], choices=[
        ('very', 'Very confident'),
        ('moderate', 'Moderately confident'),
        ('low', 'Not very confident'),
        ('stressed', 'Stressed')
    ])

    memory_method = RadioField("What's your easiest way to remember information?", validators=[DataRequired()], choices=[
        ('notes', 'Taking notes'),
        ('videos', 'Watching videos'),
        ('repetition', 'Repeating information')
    ])

    online_learning = RadioField('How often do you use online learning resources?', validators=[DataRequired()], choices=[
        ('daily', 'Daily'),
        ('few_times', 'Several times a week'),
        ('rarely', 'Rarely'),
        ('never', 'Never')
    ])

    hardest_subject = SelectField('Which subject do you find most difficult?', validators=[DataRequired()], choices=[
        ('Natural sciences', 'Natural sciences'),
        ('mathematics', 'Mathematics'),
        ('languages', 'Languages'),
        ('social sciences', 'Social sciences'),
        ('Computer sciences', 'Computer sciences'),
        ('other', 'Other')
    ])

    favorite_subject = SelectField('What is your favorite school subject?', validators=[DataRequired()], choices=[
        ('Natural sciences', 'Natural sciences'),
        ('mathematics', 'Mathematics'),
        ('languages', 'Languages'),
        ('social sciences', 'Social sciences'),
        ('Computer sciences', 'Computer sciences'),
        ('other', 'Other')
    ])

    social_time = RadioField('How much time do you spend on social media/games daily?', validators=[DataRequired()], choices=[
        ('under_1', 'Less than 1 hour'),
        ('1_3', '1–3 hours'),
        ('over_3', 'More than 3 hours')
    ])

    video_platforms = MultiCheckboxField('Which platforms do you use most for video lessons?', validators=[Optional()], choices=[
        ('youtube', 'YouTube'),
        ('ucha_se', 'Ucha.se'),
        ('khan', 'Khan Academy'),
        ('online_school', 'Online School')
    ])

    video_helpful = RadioField('Do video lessons help you understand the material better?', validators=[DataRequired()], choices=[
        ('very', 'Very much'),
        ('somewhat', 'Somewhat'),
        ('not_much', 'Not really'),
        ('not_at_all', 'Not at all')
    ])

    lesson_quality = MultiCheckboxField('What are the most important qualities of a good video lesson?', validators=[Optional()], choices=[
        ('short_clear', 'Short and clear'),
        ('examples', 'With examples and exercises'),
        ('visuals', 'With visuals and animations'),
        ('slow_clear', 'Explained slowly and clearly')
    ])

    ideal_length = RadioField('What is the ideal length of a video lesson?', validators=[DataRequired()], choices=[
        ('under_5', 'Less than 5 minutes'),
        ('5_10', '5–10 minutes'),
        ('10_20', '10–20 minutes'),
        ('doesnt_matter', 'Does not matter as long as it is useful')
    ])

    videos_for_tests = RadioField('Do you watch video lessons when preparing for tests?', validators=[DataRequired()], choices=[
        ('always', 'Always'),
        ('sometimes', 'Sometimes'),
        ('only_if_needed', 'Only if I do not understand'),
        ('never', 'Never')
    ])

    review_before_class = RadioField('How often do you review lessons before class?', validators=[DataRequired()], choices=[
        ('always', 'Always'),
        ('sometimes', 'Sometimes'),
        ('never', 'Never')
    ])

    submit = SubmitField('Submit')


class SettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Save Changes')
class VideoSubmissionForm(FlaskForm):
    video_link = StringField('Video Link', validators=[
        DataRequired(), URL(), Length(max=500)
    ])
    submit = SubmitField('Submit')