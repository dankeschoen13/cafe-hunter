import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    admin_name = "MarcoBernacer"

    if not admin_email or not admin_password:
        print("❌ ERROR: Missing ADMIN_EMAIL or ADMIN_PASSWORD in environment.")
        exit(1)

    # CREATE ADMIN
    admin = db.session.execute(db.select(User).filter_by(email=admin_email)).scalar_one_or_none()

    if not admin:
        admin = User(
            email=admin_email,
            password=generate_password_hash(admin_password),
            name=admin_name,
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created with ID: {admin.id}")
    else:
        print(f"⚡ Admin already exists with ID: {admin.id}")

    # CREATE DEMO ACCOUNT
    demo_email = os.environ.get("DEMO_EMAIL")
    demo_password = os.environ.get("DEMO_PASSWORD")

    if not demo_email or not demo_password:
        print("❌ ERROR: Missing DEMO_EMAIL or DEMO_PASSWORD in environment.")
        exit(1)

    demo = db.session.execute(db.select(User).filter_by(email=demo_email)).scalar_one_or_none()

    if not demo:
        demo = User(
            email=demo_email,
            password=generate_password_hash(demo_password),
            name='demo_user',
            is_admin=False
        )
        db.session.add(demo)
        db.session.commit()
        print(f"✅ Demo created with ID: {demo.id}")