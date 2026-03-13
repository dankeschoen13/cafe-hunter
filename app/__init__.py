import os
from flask import Flask
from app.extensions import db, bootstrap, ckeditor, login_manager, csrf, migrate

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-only-not-safe')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cafes.db')
    app.config['CKEDITOR_PKG_TYPE'] = 'standard-all'

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    ckeditor.init_app(app)

    from app.routes import api_bp, web_bp, auth_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)

    return app