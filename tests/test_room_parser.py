"""RoomspotRoomParser.parse: mapping API JSON to Room, and the None-branches."""
import pytest

from notbehomeless.models.allocation_type import AllocationType
from notbehomeless.websites.roomspot.room_parser import RoomspotRoomParser


@pytest.fixture
def item() -> dict:
    """A realistic Roomspot listing item."""
    return {
        "id": "20361",
        "street": "Calslaan",
        "houseNumber": "26",
        "houseNumberAddition": "",
        "totalRent": "402.51",
        "city": {"name": "Enschede"},
        "areaDwelling": "17",
        "publicationDate": "2026-07-01T10:00:00Z",
        "closingDate": "2026-07-08T10:00:00Z",
        "urlKey": "calslaan-26",
        "toewijzingModelCategorie": {"code": "cooptation"},
        "specifiekeVoorzieningen": [
            {"localizedLabel": "Eigen keuken"},
            {"localizedLabel": "Incl. internet"},
        ],
    }


def test_parses_full_item(item):
    room = RoomspotRoomParser.parse(item)

    assert room is not None
    assert room.room_id == 20361
    assert room.title == "Calslaan 26"
    assert room.price == pytest.approx(402.51)
    assert room.city == "Enschede"
    assert room.size == pytest.approx(17)
    assert room.link == "https://www.roomspot.nl/aanbod/te-huur/details/calslaan-26"
    assert room.allocation_type is AllocationType.COOPTATION
    assert room.private_kitchen is True
    assert room.wifi is True
    assert room.private_bathroom is False
    assert room.furnished is False


def test_dates_are_timezone_aware(item):
    room = RoomspotRoomParser.parse(item)
    assert room.publication_date.tzinfo is not None
    assert room.closing_date.tzinfo is not None


def test_unknown_allocation_code_becomes_none(item):
    item["toewijzingModelCategorie"] = {"code": "something-new"}
    room = RoomspotRoomParser.parse(item)
    assert room is not None
    assert room.allocation_type is None


def test_missing_dates_return_none(item):
    item["publicationDate"] = ""
    assert RoomspotRoomParser.parse(item) is None


def test_missing_url_key_returns_none(item):
    del item["urlKey"]
    assert RoomspotRoomParser.parse(item) is None
