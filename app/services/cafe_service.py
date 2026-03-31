import time
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
from flask import current_app
from flask_login import current_user
from sqlalchemy import desc, or_, and_
from app.extensions import db
from app.models import Cafe, Rating, User
from app.constants import Errors

class CafeService:

    BARRED_KEYS = [
        'id',
        'average_rating',
        'date_submitted',
        'date_updated',
        'ratings',
        'deleted_at'
    ]
    BOOL_KEYS = [
        'has_sockets',
        'has_toilet',
        'has_wifi',
        'can_take_calls',
        'is_featured'
    ]

    @classmethod
    def _populate_attributes(cls, cafe_obj: Cafe, cafe_data: dict) -> None:
        """
        Internal helper: Safely maps a dictionary of data onto a Cafe object.
        Modifies the object in-place.
        """
        for key, value in cafe_data.items():
            if key in cls.BARRED_KEYS or not hasattr(cafe_obj, key):
                continue

            if key in cls.BOOL_KEYS:
                if isinstance(value, str):
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    else:
                        raise ValueError(
                            f"{key}:{Errors.INVALID_BOOL_VALUE}")
                else:
                    value = bool(value)
                setattr(cafe_obj, key, value)
            else:
                setattr(cafe_obj, key, value)


    @classmethod
    def _active_cafes_query(cls):
        """
        Internal helper: Returns a Select object pre-filtered for active cafés.
        """
        return db.select(Cafe).where(Cafe.deleted_at.is_(None))


    @classmethod
    def fetch_by_id(cls, cafe_id) -> Cafe | None:
        """
        Fetches a café with matching id.
        """
        stmt = cls._active_cafes_query().where(Cafe.id == cafe_id)

        return db.session.execute(stmt).scalar_one_or_none()


    @classmethod
    def fetch_all(cls) -> list[Cafe]:
        """
        Fetches all cafés entries from the database.
        """
        stmt = cls._active_cafes_query().order_by(Cafe.name)

        return db.session.execute(stmt).scalars().all()


    @classmethod
    def fetch_random(cls) -> Cafe | None:
        """
        Fetches a random café from the database.
        """
        stmt = cls._active_cafes_query().order_by(func.random()).limit(1)

        return db.session.execute(stmt).scalar_one_or_none()


    @classmethod
    def fetch_featured(cls) -> list[Cafe]:
        """
        Fetches all featured cafés from the database.
        """
        stmt = cls._active_cafes_query().where(Cafe.is_featured == True)

        return db.session.execute(stmt).scalars().all()


    @classmethod
    def fetch_recent(cls, limit: int = 5) -> list[Cafe]:
        """
        Fetches up to 20 most recent cafe entries.
        """
        final_limit = min(limit, 20)

        stmt = cls._active_cafes_query().order_by(
            desc(Cafe.date_submitted)).limit(final_limit)

        return db.session.execute(stmt).scalars().all()


    @classmethod
    def search(cls, keyword: str) -> list[Cafe]:
        """
        Searches database for cafés matching the keyword in their name or location.
        """
        stmt = cls._active_cafes_query().where(or_(
            Cafe.location.ilike(f"%{keyword}%"),
            Cafe.name.ilike(f"%{keyword}%")
        ))

        return db.session.execute(stmt).scalars().all()


    @classmethod
    def rate(cls, cafe_id: int, rating: int, user: User) -> Cafe | None:
        """
        Add a new rating or update an existing one for the current user.
        """
        cafe_to_rate = cls.fetch_by_id(cafe_id)

        if not cafe_to_rate:
            return None

        existing_rating = db.session.execute(
            db.select(Rating).where(and_(
                Rating.cafe_id == cafe_to_rate.id,
                Rating.user_id == user.id
            ))
        ).scalar_one_or_none()

        if existing_rating:
            existing_rating.score = rating

        else:
            new_rating = Rating()
            new_rating.score = rating
            new_rating.cafe = cafe_to_rate
            new_rating.user = user
            db.session.add(new_rating)

        try:
            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"{Errors.RATING_FAILED}: {e}")

            db.session.rollback()
            raise ValueError(Errors.UNABLE_TO_RATE)

        return cafe_to_rate


    @classmethod
    def create(cls, cafe_cata: dict) -> Cafe | None:
        """
        Create a new cafe from a dictionary of attributes.
        """
        new_cafe = Cafe()

        cls._populate_attributes(new_cafe, cafe_cata)

        try:
            db.session.add(new_cafe)
            db.session.commit()

        except IntegrityError as e:
            current_app.logger.error(f"{Errors.DB_ERROR_AT_CREATION}: {e}")

            db.session.rollback()
            raise ValueError(Errors.CAFE_ALREADY_EXISTS)

        return new_cafe


    @classmethod
    def update(cls, updated_data: dict, cafe_id: int) -> Cafe | None:
        """
        Updates an existing cafe.
        """
        existing_cafe = cls.fetch_by_id(cafe_id)

        if not existing_cafe:
            return None

        cls._populate_attributes(existing_cafe, updated_data)

        try:
            db.session.commit()

        except IntegrityError as e:
            current_app.logger.error(f"{Errors.DB_ERROR_AT_CREATION}: {e}")

            db.session.rollback()
            raise ValueError(Errors.CAFE_ALREADY_EXISTS)

        return existing_cafe


    @classmethod
    def report_closed(cls, cafe_id: int) -> Cafe | None:
        """
        Increments the closed_reports counter for a specific cafe.
        """
        cafe_to_report = cls.fetch_by_id(cafe_id)

        if not cafe_to_report:
            return None

        cafe_to_report.closed_reports += 1

        try:
            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"{Errors.CLOSED_REPORT_FAILED}: {e}")

            db.session.rollback()
            raise ValueError(Errors.UNABLE_TO_REPORT)

        return cafe_to_report


    @classmethod
    def soft_delete(cls, cafe_id: int) -> Cafe | None:

        cafe_to_delete = cls.fetch_by_id(cafe_id)
        if not cafe_to_delete:
            return None

        cafe_to_delete.deleted_at = datetime.now(timezone.utc)
        cafe_to_delete.name = f"{cafe_to_delete.name}_[deleted_{int(time.time())}]"

        try:
            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"{Errors.SOFT_DELETE_FAILED}: {e}")

            db.session.rollback()
            raise ValueError(Errors.UNABLE_TO_DELETE)

        return cafe_to_delete


    @classmethod
    def delete(cls, cafe_id: int) -> Cafe | None:
        """
        Deletes an existing cafe from the database.
        """
        cafe_cafe_to_delete = cls.fetch_by_id(cafe_id)
        if not cafe_cafe_to_delete:
            return None

        db.session.delete(cafe_cafe_to_delete)
        db.session.commit()

        return cafe_cafe_to_delete


