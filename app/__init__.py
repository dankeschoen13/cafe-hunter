import os
from flask import Flask
from app.extensions import db, bootstrap, ckeditor, login_manager

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes_test.db'
    app.config['CKEDITOR_PKG_TYPE'] = 'standard-all'

    db.init_app(app)
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)

    from app.routes import api_bp, web_bp, auth_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)

    # CREATE DATABASE
    with app.app_context():
        from app.models import Cafe, User
        db.create_all()

    return app