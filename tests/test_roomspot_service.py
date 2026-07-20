"""RoomspotService: react branches and get_rooms filtering (no HTTP)."""
import pytest

from notbehomeless.models.room_filter import RoomFilter
from notbehomeless.websites.roomspot.exception import (
    ActionUnavailableError,
    ReactionFailedError,
    RoomNotFoundError,
    RoomNotReactableError,
)
from notbehomeless.websites.roomspot.room_reaction_action import RoomReactionAction
from notbehomeless.websites.roomspot.service import RoomspotService


async def test_react_unknown_room_raises_not_found(sim_api, make_room):
    service = RoomspotService(sim_api(rooms=[make_room(room_id=1)]))
    with pytest.raises(RoomNotFoundError):
        await service.react(None, 999, RoomReactionAction.ADD)


async def test_react_not_reactable_raises(sim_api, make_room):
    service = RoomspotService(sim_api(rooms=[make_room(can_react=False)]))
    with pytest.raises(RoomNotReactableError):
        await service.react(None, 1, RoomReactionAction.ADD)


async def test_react_action_mismatch_raises(sim_api, make_room):
    service = RoomspotService(sim_api(rooms=[make_room(action="remove")]))
    with pytest.raises(ActionUnavailableError):
        await service.react(None, 1, RoomReactionAction.ADD)


async def test_react_add_signs_room(sim_api, make_room):
    api = sim_api(rooms=[make_room(room_id=7, action="add")])
    room = await RoomspotService(api).react(None, 7, RoomReactionAction.ADD)
    assert room.room_id == 7
    assert api.signed == [7]
    assert api.unsigned == []


async def test_react_remove_unsigns_room(sim_api, make_room):
    api = sim_api(rooms=[make_room(room_id=7, action="remove")])
    await RoomspotService(api).react(None, 7, RoomReactionAction.REMOVE)
    assert api.unsigned == [7]
    assert api.signed == []


async def test_react_upstream_failure_propagates(sim_api, make_room):
    api = sim_api(rooms=[make_room(room_id=7)], fail_sign=True)
    with pytest.raises(ReactionFailedError):
        await RoomspotService(api).react(None, 7, RoomReactionAction.ADD)


async def test_get_rooms_applies_filter(sim_api, make_room):
    api = sim_api(rooms=[
        make_room(room_id=1, price=400),
        make_room(room_id=2, price=900),
        make_room(room_id=3, price=650),
    ])
    rooms = await RoomspotService(api).get_rooms(None, RoomFilter(max_price=700))
    assert [r.room_id for r in rooms] == [1, 3]


async def test_get_rooms_default_filter_returns_all(sim_api, make_room):
    api = sim_api(rooms=[make_room(room_id=i) for i in range(3)])
    rooms = await RoomspotService(api).get_rooms(None, RoomFilter())
    assert len(rooms) == 3
