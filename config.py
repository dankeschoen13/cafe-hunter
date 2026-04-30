import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-only-not-safe')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cafes.db')
    CKEDITOR_PKG_TYPE = 'standard-all'
    SR_PER_PAGE = 3 # Search results per page
    DEMO_MODE = os.environ.get('DEMO_MODE') == 'True'