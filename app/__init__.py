from flask import Flask
from config import Config
from app.extensions import db, bootstrap, ckeditor, login_manager, csrf, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    ckeditor.init_app(app)

    from app.routes import api_bp, web_bp, auth_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    csrf.exempt(api_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)

    from app.utils import smart_url_filter, format_time, format_date
    app.add_template_filter(smart_url_filter, name='smart_url')
    app.add_template_filter(format_time, name='format_time')
    app.add_template_filter(format_date, name='format_date')

    return app