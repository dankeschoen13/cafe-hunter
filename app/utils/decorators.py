from flask import abort, request, flash, redirect, url_for, g
from flask_login import current_user
from functools import wraps
from app.services import CafeService
from typing import Any


def access_required(func):
    """
    Authorization middleware that enforces role-based access control (RBAC) for café routes.

    This decorator secures routes by verifying the user's authentication status and
    evaluating their permissions against the requested resource. It gracefully handles
    both resource-specific routes (Edit/Delete) and general routes (Add).

    Access Rules:
        1. User must be authenticated (returns 403 if not).
        2. If a `café_id` is provided in the route parameters:
            - Fetches the café from the database.
            - If the café exists, the user must be a Super Admin OR the original author
              of the café to proceed (returns 403 if unauthorized).
            - If the café does not exist, allows the route to proceed so the underlying
              view function can handle the missing resource (e.g., via flash & redirect).
        3. If no `café_id` is provided (e.g., adding a new café), the user is granted access.

    Side Effects:
        - If a valid café is found and authorized, it is attached to the Flask global
          object as `g.current_café` to prevent redundant database queries in the route.
        - If the requested `café_id` does not exist in the database, `g.current_café`
          is set to `None`.

    Args:
        func (Callable): The Flask view function being decorated.

    Returns:
        Callable: The wrapped view function, or triggers `flask.abort(403)` if
        authorization fails.
    """
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