from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone, time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint, func, Time
from app.extensions import db

if TYPE_CHECKING:
    from app.models import User

class Cafe(db.Model):
    __tablename__ = "cafes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(250),
        unique=True,
        nullable=False
    )
    map_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    img_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    location: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )
    open_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )
    close_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )
    seats: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )
    has_toilet: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    has_wifi: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    has_sockets: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    can_take_calls: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )
    coffee_price: Mapped[Optional[str]] = mapped_column(
        String(250),
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    is_featured: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True
    )
    date_submitted: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(), # remember, prevents database wipe if data is missing
        nullable=False
    )
    date_updated: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )
    author: Mapped[Optional["User"]] = relationship(
        back_populates="authored_cafes"
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="cafe",
        cascade="all, delete-orphan"
    )
    closed_reports: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
        default=0
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    def to_dict(self):
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        data["average_rating"] = self.average_rating
        return data

    def print_columns(self):
        return self.__table__.columns

    @hybrid_property
    def average_rating(self):
        if not self.ratings:
            return 0.0

        total_score = sum(review.score for review in self.ratings)
        return round(total_score / len(self.ratings), 1) # type: ignore


class Rating(db.Model):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    user: Mapped["User"] = relationship(
        back_populates="ratings"
    )

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey("cafes.id", ondelete="CASCADE"),
        nullable=False
    )
    cafe: Mapped["Cafe"] = relationship(
        back_populates="ratings"
    )

    score: Mapped[int] = mapped_column(
        CheckConstraint('score >= 1 AND score <= 5'),
        nullable=False
    )