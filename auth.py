from flask import Blueprint, request, render_template, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from forms import RegisterForm, LoginForm
from models import User
from extensions import db

import utlis


auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # POST
    if form.validate_on_submit():
        if db.session.execute(db.select(User).where(User.email == form.email.data)).scalar():
            flash("That email is already registered. Login instead!")
            return redirect(url_for('auth_bp.login'))

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
            return redirect(url_for('auth_bp.login'))
        login_user(new_user)
        return redirect(url_for('web_bp.index'))
    # GET
    return render_template('register.html', form=form)


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
            if not next_page or not utlis.is_safe_url(next_page):
                next_page =  url_for('web_bp.index')
            return redirect(next_page)

        flash('Invalid email address or password', 'Error')
    # GET
    return render_template('login.html', form=form)