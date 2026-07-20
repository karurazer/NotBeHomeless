"""Roomspot client exceptions."""
from notbehomeless.models.base_exception import AppException
from notbehomeless.models.website import Website


class RoomspotError(AppException):
    """Base for Roomspot upstream failures."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code=status_code, website=Website.ROOMSPOT)


class ReactionFailedError(RoomspotError):
    """A reaction request to Roomspot failed."""

    def __init__(self, room_id: int):
        super().__init__(f"Reaction request failed for room {room_id}")
        self.room_id = room_id


class RoomNotFoundError(RoomspotError):
    """The requested room is not in the current listing."""

    def __init__(self, room_id: int):
        super().__init__(f"Room {room_id} not found", status_code=404)
        self.room_id = room_id


class RoomNotReactableError(RoomspotError):
    """The room currently offers no reaction action."""

    def __init__(self, room_id: int):
        super().__init__(f"Room {room_id} is not reactable", status_code=409)
        self.room_id = room_id


class ActionUnavailableError(RoomspotError):
    """The requested action is not the one currently available for the room."""

    def __init__(self, room_id: int, requested: str, available: str):
        super().__init__(
            f"Action '{requested}' not available for room {room_id} "
            f"(available: '{available}')",
            status_code=409,
        )
        self.room_id = room_id
