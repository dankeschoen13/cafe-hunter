from flask import abort, request, flash, redirect, url_for
from flask_login import current_user
from functools import wraps

def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.id == 1:
            return abort(403)
        return func(*args, **kwargs)
    return wrapper

def login_required_to_post(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'POST' and not current_user.is_authenticated:
            flash("Please log in to leave a comment.", "Error")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper