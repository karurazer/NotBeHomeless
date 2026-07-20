"""Room listing and reaction endpoints."""
from fastapi import APIRouter

from notbehomeless.api.dependencies import (
    RoomFilterDep,
    RoomspotServiceDep,
    SessionDep,
)
from notbehomeless.api.schemas.reaction import ReactionRequest
from notbehomeless.api.schemas.room import ReactionResult, RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("")
async def list_rooms(
    service: RoomspotServiceDep,
    session: SessionDep,
    room_filter: RoomFilterDep,
) -> list[RoomOut]:
    """List current rooms, optionally filtered via query parameters."""
    rooms = await service.get_rooms(session, room_filter)
    return [RoomOut.from_room(r) for r in rooms]


@router.post(
    "/{room_id}/react",
    responses={
        404: {"description": "Room not found"},
        409: {"description": "Room not reactable / action unavailable"},
        502: {"description": "Roomspot request failed"},
    },
)
async def react_to_room(
    room_id: int,
    body: ReactionRequest,
    service: RoomspotServiceDep,
    session: SessionDep,
) -> ReactionResult:
    """React to a room with the requested action (add/remove)."""
    room = await service.react(session, room_id, body.action)
    return ReactionResult(status=body.action.value, room=RoomOut.from_room(room))
