from flask import abort, request, flash, redirect, url_for, g
from flask_login import current_user
from functools import wraps
from app.services import CafeService
from typing import Any


def admin_or_author_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs: Any):

        if not current_user.is_authenticated:
            return abort(403)

        cafe_id = kwargs.get('cafe_id')

        if isinstance(cafe_id, int):

            cafe = CafeService.fetch_by_id(cafe_id)

            if not cafe:
                g.current_cafe = None
                return func(*args, **kwargs)

            if current_user.is_admin or cafe.author_id == current_user.id:
                g.current_cafe = cafe
                return func(*args, **kwargs)

            else:
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