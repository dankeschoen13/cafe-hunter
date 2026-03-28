from enum import StrEnum

class Errors(StrEnum):
    NO_DATA_FOUND = "Sorry, there are no cafes in the database."
    FEATURED_NOT_FOUND = "Sorry, there are no featured cafes in the database."
    ID_NOT_FOUND = "Sorry, a cafe with that id was not found in the database."
    LOC_NOT_FOUND = "Sorry, we don't have a cafe at that location."
    RESULTS_NOT_FOUND = "Sorry, there are no matching entries in the database"

    WRONG_API_KEY = "Sorry, that's not allowed. Make sure you have the correct api_key."
    CAFE_ALREADY_EXISTS = "Sorry, the cafe's name already exists in the database."
    INVALID_BOOL_VALUE ="has invalid value. Expected 'true' or 'false'."

    DB_ERROR_AT_CREATION = "Database IntegrityError during cafe creation"
    CLOSED_REPORT_FAILED = "Failed to increment closed report"

class Alerts(StrEnum):
    CAFE_ADDED = "Successfully added the new cafe."
    CAFE_DELETED = "Cafe has been deleted from the database."
    CAFE_UPDATED = "Cafe details have been successfully updated."
    PRICE_UPDATED = "Successfully updated the price."
    CAFE_REPORTED = "Cafe reported. Total reports"
    RANDOM_API_CALLED = "Featured cafes not found. Random API called instead."

class Actions(StrEnum):
    ADD_NEW_CAFE = "Adding a new cafe to the database."
    EDITING_CAFE = "Editing existing cafe entry."