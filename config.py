import os

db_url = os.environ.get('DATABASE_URL')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-only-not-safe')
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///cafes.db"
    DEMO_MODE = os.environ.get('DEMO_MODE') == 'True'
    ADMIN_ID = os.environ.get('OFFICIAL_ADMIN_ID')
    CKEDITOR_PKG_TYPE = 'standard-all'
    SR_PER_PAGE = 3 # Search results per page
    
