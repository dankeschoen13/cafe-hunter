# ☕ Café Hunter 🥯 🥖 🍝

Cafe Hunter is a full-stack web application designed to help remote workers, students, and digital nomads discover the best cafes in their area. 

Built with **Python** and **Flask**, this project demonstrates a production-ready web architecture. 

It features a publicly consumable RESTful API allowing developers to access and integrate café data, role-based access control (Super Admin vs. Guest Admin viewing), and secure credential management and full CRUD operation through the web interface. The platform also includes a secure user authentication system, enabling visitors to create accounts, submit star ratings, and in the future, write detailed reviews for their favorite local spots.

The database schema handles complex relationships and boolean casting across different SQL dialects, seamlessly transitioning from a local SQLite development environment to a live PostgreSQL production database.

### Tech Stack & Highlights
* **Backend:** Flask, Python
* **Database:** SQLAlchemy, PostgreSQL (Production), SQLite (Local)
* **Migrations:** Flask-Migrate (Alembic)
* **Frontend UI:** Jinja2, Bootstrap, CKEditor (Rich Text Integration)
* **Deployment:** Render, Gunicorn
* **Architecture:** Application Factory Pattern, secure `.env` credential injection