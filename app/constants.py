from enum import StrEnum

class Errors(StrEnum):
    NO_DATA_FOUND = "Sorry, there are no cafes in the database."
    FEATURED_NOT_FOUND = "Sorry, there are no featured cafes in the database."
    ID_NOT_FOUND = "Sorry, a cafe with that id was not found in the database."
    LOC_NOT_FOUND = "Sorry, we don't have a cafe at that location."
    RESULTS_NOT_FOUND = "Sorry, there are no matching entries in the database"
    DEMO_ACCOUNT_NOT_FOUND = "Demo account not found. Please contact the administrator."

    WRONG_API_KEY = "Sorry, that's not allowed. Make sure you have the correct api_key."
    CAFE_ALREADY_EXISTS = "Sorry, the cafe's name already exists in the database."
    DB_ERROR_AT_CREATION = "Database IntegrityError during cafe creation"

    INVALID_BOOL_VALUE ="has invalid value. Expected 'true' or 'false'."
    INVALID_RATING = "Invalid rating submitted. Please choose between 1 and 5"

    CLOSED_REPORT_FAILED = "Failed to increment closed report"
    SOFT_DELETE_FAILED = "Failed to delete the cafe"
    RATING_FAILED = "Failed to add rating to the database"

    UNABLE_TO_REPORT = "Could not process report. Please try again later."
    UNABLE_TO_DELETE = "Could not delete cafe. Please try again later."
    UNABLE_TO_RATE  = "Could not rate cafe. Please try again later."


class Alerts(StrEnum):
    CAFE_ADDED = "Successfully added the new cafe."
    CAFE_DELETED = "Cafe has been deleted from the database."
    CAFE_UPDATED = "Cafe details have been successfully updated."
    CAFE_RATED = "Successfully rated the cafe."
    PRICE_UPDATED = "Successfully updated the price."
    CAFE_REPORTED = "Cafe reported. Total reports"
    RANDOM_API_CALLED = "Featured cafes not found. Random API called instead."
    DEMO_WELCOME = "Welcome to the Demo! Feel free to add cafes or delete the ones you create."

class Actions(StrEnum):
    ADD_NEW_CAFE = "Adding a new cafe to the database."
    EDITING_CAFE = "Editing existing cafe entry."