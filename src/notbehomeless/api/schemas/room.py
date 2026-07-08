from datetime import datetime

from pydantic import BaseModel

from notbehomeless.models.room import Room


class RoomOut(BaseModel):
    """Room as returned by the API."""

    room_id: int
    title: str
    link: str
    price: float
    city: str
    size: float
    publication_date: datetime
    closing_date: datetime
    allocation_type: str | None = None
    private_kitchen: bool
    private_bathroom: bool
    furnished: bool
    wifi: bool
    can_react: bool

    @classmethod
    def from_room(cls, room: Room) -> "RoomOut":
        """Map an internal ``Room`` domain object to the API DTO."""
        return cls(
            room_id=room.room_id,
            title=room.title,
            link=room.link,
            price=room.price,
            city=room.city,
            size=room.size,
            publication_date=room.publication_date,
            closing_date=room.closing_date,
            allocation_type=room.allocation_type.value if room.allocation_type else None,
            private_kitchen=room.private_kitchen,
            private_bathroom=room.private_bathroom,
            furnished=room.furnished,
            wifi=room.wifi,
            can_react=room.can_react,
        )

class ReactionResult(BaseModel):
    room: RoomOut
    status: str
