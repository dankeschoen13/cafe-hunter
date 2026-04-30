from flask import Blueprint, request, render_template, url_for, redirect, flash, current_app, abort
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from app.constants import Alerts, Errors
from app.forms import RegisterForm, LoginForm
from app.models import User
from app.extensions import db
from app.utils import is_safe_url

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # POST
    if form.validate_on_submit():
        if db.session.execute(db.select(User).where(User.email == form.email.data)).scalar():
            flash("That email is already registered. Login instead!")
            return redirect(url_for('auth.login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("That email is already registered. Login instead!")
            return redirect(url_for('auth.login'))
        login_user(new_user)
        return redirect(url_for('web.cafe_index'))
    # GET
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # POST
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not is_safe_url(next_page):
                next_page =  url_for('web.cafe_index')
            return redirect(next_page)

        flash('Invalid email address or password', 'Error')
    # GET
    return render_template('auth/login.html', form=form)


@auth_bp.route('/demo-login')
def demo_login():

    if not current_app.config["DEMO_MODE"]:
        return abort(403)

    demo_user = db.session.execute(
        db.select(User).where(User.email == "demo@cafehunter.com")
    ).scalar_one_or_none()

    if demo_user:
        login_user(demo_user)
        flash(Alerts.DEMO_WELCOME, "success")
        return redirect(url_for('web.cafe_index'))

    flash(Errors.DEMO_ACCOUNT_NOT_FOUND, "danger")
    return redirect(url_for('web.cafe_index'))


@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out', 'info')
    return redirect(url_for('web.cafe_index'))