import time
from typing import TypedDict, Unpack
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func
from flask import current_app
from sqlalchemy import desc, or_, and_
from app.extensions import db
from app.models import Cafe, Rating, User
from app.constants import Errors

class SearchFilters(TypedDict, total=False):
    wifi: bool
    sockets: bool
    calls: bool
    toilet: bool

class CafeService:
    """
    Handles business logic and database operations for Cafe entities.

    This service class encapsulates SQLAlchemy queries to keep the
    application's routing layer clean and focused purely on HTTP responses.
    """

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

        Args:
            cafe_obj (Cafe): Cafe object to be filled.
            cafe_data (dict): Cafe data to be mapped to the cafe object.

        Returns:
            None
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

        Args:
            cafe_id (int): Cafe id to fetch.

        Returns:
            Cafe | None: A cafe object or None
        """

        stmt = cls._active_cafes_query().where(Cafe.id == cafe_id)
        return db.session.execute(stmt).scalar_one_or_none()


    @classmethod
    def fetch_all(cls) -> list[Cafe]:
        """
        Fetches all cafés entries.

        Returns:
            list[Cafe]: A list of SQLAlchemy Cafe model instances
        """

        stmt = cls._active_cafes_query().order_by(Cafe.name)
        return db.session.execute(stmt).scalars().all()


    @classmethod
    def fetch_random(cls) -> Cafe | None:
        """
        Fetches a random café.

        Returns:
            Cafe | None: A random cafe or None
        """

        stmt = cls._active_cafes_query().order_by(func.random()).limit(1)
        return db.session.execute(stmt).scalar_one_or_none()


    @classmethod
    def fetch_featured(cls) -> list[Cafe]:
        """
        Fetches featured cafés.

        Returns:
            list[Cafe]: A list of SQLAlchemy Cafe model instances
        """

        stmt = cls._active_cafes_query().where(Cafe.is_featured == True)
        return db.session.execute(stmt).scalars().all()


    @classmethod
    def fetch_recent(cls, limit: int = 5) -> list[Cafe]:
        """
        Fetches up to 20 most recent cafe entries.

        Args:
            limit (int, optional): Number of entries to return. Defaults to 5.

        Returns:
            list[Cafe]: A list of SQLAlchemy Cafe model instances
        """

        final_limit = min(limit, 20)

        stmt = cls._active_cafes_query().order_by(
            desc(Cafe.date_submitted)).limit(final_limit)

        return db.session.execute(stmt).scalars().all()


    @classmethod
    def search(
        cls, q: str = None,
        page: int = 1, per_page: int = 10,
        **filters: Unpack[SearchFilters]) -> list[Cafe]:
        """
        Searches active cafés based on text queries & filters.

        Args:
            q (str, optional): Short for "query". The search keyword used to find
                matches within the café's name or location. Defaults to None.
            page (int, optional): The current page number for pagination. Defaults to 1.
            per_page (int, optional): The maximum number of results per page. Defaults to 10.
            **filters (Unpack[SearchFilters]): Dynamic boolean toggles for specific
                amenities (e.g., wifi=True, sockets=True). Keys must match the
                SearchFilters TypedDict.

        Returns:
            list[Cafe]: A paginated list of SQLAlchemy Cafe model instances matching
                all provided criteria.
        """

        stmt = cls._active_cafes_query()

        if q:
            stmt = stmt.where(or_(
                Cafe.location.ilike(f"%{q}%"),
                Cafe.name.ilike(f"%{q}%")
            ))

        feature_map = {
            'wifi': Cafe.has_wifi,
            'sockets': Cafe.has_sockets,
            'calls': Cafe.can_take_calls,
            'toilet': Cafe.has_toilet
        }

        for key, db_column in feature_map.items():
            # noinspection PyTypedDict
            if filters.get(key):
                stmt = stmt.where(db_column == True)

        skip_count = (page - 1) * per_page

        stmt = stmt.offset(skip_count).limit(per_page)
        return db.session.execute(stmt).scalars().all()


    @classmethod
    def rate(cls, cafe_id: int, rating: int, user: User) -> Cafe | None:
        """
        Add a new rating or update an existing one.

        Args:
            cafe_id (int): Cafe object's ID in the database
            rating (int): User's rating value
            user (User): User object that owns the rating

        Returns:
            Cafe | None: The rated Cafe object or None
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

        Args:
            cafe_cata (dict): Dictionary of attributes to create

        Returns:
            Cafe | None: The created Cafe object or None
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
        Updates the details of an existing cafe.

        Args:
            updated_data (dict): Dictionary of attributes to update
            cafe_id (int): Cafe object's ID in the database

        Returns:
            Cafe | None: The updated Cafe object or None
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

        Args:
            cafe_id (int): Cafe object's ID in the database

        Returns:
            Cafe | None: The reported Cafe object or None
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
        """
        Marks a cafe as soft deleted.

        Args:
            cafe_id (int): Cafe object's ID

        Returns:
            Cafe | None: The Cafe object marked as deleted or None
        """

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
        Permanently deletes a cafe from the database.

        Args:
            cafe_id (int): Cafe object's ID

        Returns:
            Cafe | None: The Cafe object permanently deleted or None
        """

        cafe_cafe_to_delete = cls.fetch_by_id(cafe_id)
        if not cafe_cafe_to_delete:
            return None

        db.session.delete(cafe_cafe_to_delete)
        db.session.commit()

        return cafe_cafe_to_delete


