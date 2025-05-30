from flask_login import current_user, login_required
from flask import render_template
from student import student_bp
@student_bp.route('/student_dashboard')
@login_required
def dashboard():
    return render_template('student_dashboard.html', user=current_user)







