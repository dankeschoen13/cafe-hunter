from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.extensions import db, login_manager

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True)
    password: Mapped[str] = mapped_column(String(250))
    name: Mapped[str] = mapped_column(String(1000))

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))