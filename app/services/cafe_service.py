import random
from sqlalchemy.exc import IntegrityError
from flask import current_app
from sqlalchemy import desc, or_
from app.extensions import db
from app.models import Cafe
from app.constants import Errors

class CafeService:

    BARRED_KEYS = [
        'id',
        'average_rating',
        'date_submitted',
        'date_updated',
        'ratings'
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


    @staticmethod
    def fetch_by_id(cafe_id) -> Cafe | None:
        """
        Fetches a café with matching id.
        """
        return db.session.get(Cafe, cafe_id)


    @staticmethod
    def fetch_all() -> list[Cafe]:
        """
        Fetches all cafés entries from the database.
        """
        return db.session.execute(
            db.select(Cafe)
        ).scalars().all()


    @staticmethod
    def fetch_random() -> Cafe | None:
        """
        Fetches a random café from the database.
        """
        cafes = db.session.execute(
            db.select(Cafe)
        ).scalars().all()

        if not cafes:
            return None

        return random.choice(cafes)


    @staticmethod
    def fetch_featured() -> list[Cafe]:
        """
        Fetches all featured cafés from the database.
        """
        return db.session.execute(
            db.select(Cafe).where(Cafe.is_featured == True)
        ).scalars().all()


    @staticmethod
    def fetch_recent(limit: int = 5) -> list[Cafe]:
        """
        Fetches up to 20 most recent cafe entries.
        """
        final_limit = min(limit, 20)

        return db.session.execute(
            db.select(Cafe).order_by(
                desc(Cafe.date_submitted)).limit(final_limit)
        ).scalars().all()


    @staticmethod
    def search(keyword: str) -> list[Cafe]:
        """
        Searches database for cafés matching the keyword in their name or location.
        """
        return db.session.execute(
            db.select(Cafe).where(or_(
                Cafe.location.ilike(f"%{keyword}%"),
                Cafe.name.ilike(f"%{keyword}%")
            ))
        ).scalars().all()


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
        """Increments the closed_reports counter for a specific cafe."""
        cafe_to_report = cls.fetch_by_id(cafe_id)

        if not cafe_to_report:
            return None

        cafe_to_report.closed_reports += 1

        try:
            db.session.commit()

        except Exception as e:
            current_app.logger.error(f"{Errors.CLOSED_REPORT_FAILED}: {e}")

            db.session.rollback()
            raise ValueError("Could not process report.")

        return cafe_to_report


    @staticmethod
    def delete(cafe_id: int) -> Cafe | None:
        """
        Deletes an existing cafe from the database.
        """
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if not cafe_to_delete:
            return None

        db.session.delete(cafe_to_delete)
        db.session.commit()
        return cafe_to_delete


