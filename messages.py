from enum import Enum

class Errors(str, Enum):
    LOCATION_NO_MATCH = "Sorry, we don't have a cafe at that location."
    ID_NO_MATCH = "Sorry a cafe with that id was not found in the database."
    WRONG_API_KEY = "Sorry, that's not allowed. Make sure you have the correct api_key."

class Messages(str, Enum):
    ADD_SUCCESS = "Successfully added the new cafe."
    UPDATE_PRICE_SUCCESS = "Successfully updated the price."
    DELETE_SUCCESS = "Cafe has been deleted from the database."