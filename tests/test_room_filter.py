"""RoomFilter.matches: every criterion and the -1 'no limit' sentinel."""
from notbehomeless.models.room_filter import RoomFilter


def test_default_filter_matches_everything(make_room):
    assert RoomFilter().matches(make_room(price=99999, size=1))


def test_max_price_rejects_more_expensive(make_room):
    f = RoomFilter(max_price=800)
    assert f.matches(make_room(price=800))
    assert not f.matches(make_room(price=800.01))


def test_min_size_rejects_smaller(make_room):
    f = RoomFilter(min_size=15)
    assert f.matches(make_room(size=15))
    assert not f.matches(make_room(size=14.9))


def test_disabled_limits_do_not_reject(make_room):
    f = RoomFilter(max_price=-1, min_size=-1)
    assert f.matches(make_room(price=5000, size=0.5))


def test_kitchen_required(make_room):
    f = RoomFilter(kitchen=True)
    assert f.matches(make_room(private_kitchen=True))
    assert not f.matches(make_room(private_kitchen=False))


def test_bathroom_required(make_room):
    f = RoomFilter(bathroom=True)
    assert f.matches(make_room(private_bathroom=True))
    assert not f.matches(make_room(private_bathroom=False))


def test_furnished_required(make_room):
    f = RoomFilter(furnished=True)
    assert f.matches(make_room(furnished=True))
    assert not f.matches(make_room(furnished=False))


def test_combined_criteria(make_room):
    f = RoomFilter(max_price=700, kitchen=True)
    assert f.matches(make_room(price=600, private_kitchen=True))
    assert not f.matches(make_room(price=600, private_kitchen=False))
    assert not f.matches(make_room(price=750, private_kitchen=True))
