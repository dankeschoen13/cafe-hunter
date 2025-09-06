from flask import Flask
from flask_bootstrap import Bootstrap5 #flask_boostrap is bootstrap_flask
from flask_ckeditor import CKEditor
from api import api_bp
from web import web_bp
from models import db

app = Flask(__name__)
app.secret_key = 'sEncos-vuvfe3-xazdiv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes_test.db'
app.config['CKEDITOR_PKG_TYPE'] = 'standard-all'
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(web_bp)

ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)

# CREATE DATABASE
db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)