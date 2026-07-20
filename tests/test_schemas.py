"""API DTO mapping: RoomOut.from_room."""
from notbehomeless.api.schemas.room import RoomOut
from notbehomeless.models.allocation_type import AllocationType


def test_status_reacted_when_remove_available(make_room):
    out = RoomOut.from_room(make_room(action="remove"))
    assert out.status == "reacted"


def test_status_not_reacted_when_add_available(make_room):
    out = RoomOut.from_room(make_room(action="add"))
    assert out.status == "not_reacted"


def test_allocation_type_serialized_as_value(make_room):
    out = RoomOut.from_room(make_room(allocation_type=AllocationType.COOPTATION))
    assert out.allocation_type == "cooptation"


def test_allocation_type_none_stays_none(make_room):
    out = RoomOut.from_room(make_room(allocation_type=None))
    assert out.allocation_type is None


def test_fields_copied_verbatim(make_room):
    room = make_room(room_id=42, price=650.5, private_kitchen=True)
    out = RoomOut.from_room(room)
    assert (out.room_id, out.price, out.private_kitchen) == (42, 650.5, True)
    assert out.link == room.link
