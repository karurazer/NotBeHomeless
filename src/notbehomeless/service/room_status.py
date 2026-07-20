from datetime import datetime, timezone

from notbehomeless.models.room import Room


def is_active_room(room: Room) -> bool:
    now = datetime.now(timezone.utc)

    is_between = room.publication_date <= now <= room.closing_date
    return is_between