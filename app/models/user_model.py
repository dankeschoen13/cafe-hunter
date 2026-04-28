from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean
from sqlalchemy.sql import false
from app.extensions import db, login_manager

if TYPE_CHECKING:
    from app.models import Rating, Cafe

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(250),
        unique=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
        nullable=False
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    authored_cafes: Mapped[list["Cafe"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )

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