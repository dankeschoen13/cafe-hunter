from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in first.'
login_manager.login_message_category = "warning"

bootstrap = Bootstrap5()
ckeditor = CKEditor()
csrf = CSRFProtect()