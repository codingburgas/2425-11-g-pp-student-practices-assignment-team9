from flask import render_template

def register_error_handlers(app):
    """@app.errorhandler(404)
    def not_found_error(e):
        return render_template('page_errors/404.html'), 404"""

    """@app.errorhandler(500)
    def internal_error(error):
        try:
            return render_template('page_errors/500.html'), 500
        except Exception as e:
            return "An unexpected error occurred.", 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        try:
            return render_template('page_errors/general_error.html', error=error), 500
        except Exception:
            return "A general error occurred.", 500"""
