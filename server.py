from flask import Flask
from api import api_bp
from web import web_bp
from auth import auth_bp
from extensions import db, login_manager, bootstrap, ckeditor
import models

app = Flask(__name__)
app.secret_key = 'sEncos-vuvfe3-xazdiv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes_test.db'
app.config['CKEDITOR_PKG_TYPE'] = 'standard-all'

db.init_app(app)
bootstrap.init_app(app)
ckeditor.init_app(app)

login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(models.User, int(user_id))

app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(web_bp)
app.register_blueprint(auth_bp)

# CREATE DATABASE
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)