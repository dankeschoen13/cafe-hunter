from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()
login_manager.login_view = "web_bp.login"
login_manager.login_message = "Access Denied."

bootstrap = Bootstrap5()
ckeditor = CKEditor()