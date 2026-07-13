"""High-level Roomspot operations built on top of RoomspotApi."""
import aiohttp

from notbehomeless.models.room import Room
from notbehomeless.roomspot.api import RoomspotApi
from notbehomeless.roomspot.exception import (
    ActionUnavailableError,
    RoomNotFoundError,
    RoomNotReactableError,
)
from notbehomeless.roomspot.room_reaction_action import RoomReactionAction


class RoomspotService:
    """Orchestrates Roomspot use cases, keeping the HTTP layer thin."""

    def __init__(self, api: RoomspotApi):
        self.api = api

    async def react(
        self,
        session: aiohttp.ClientSession,
        room_id: int,
        action: RoomReactionAction,
    ) -> Room:
        """
            React to a room with the requested action.

            Raises RoomNotFoundError / RoomNotReactableError / ActionUnavailableError
            for client-side rejections, and ReactionFailedError on upstream failure.
        """
        rooms = await self.api.get_rooms(session)
        room = next((r for r in rooms if r.room_id == room_id), None)
        if room is None:
            raise RoomNotFoundError(room_id)
        if not room.can_react:
            raise RoomNotReactableError(room_id)
        if action.value != room.action:
            raise ActionUnavailableError(room_id, action.value, room.action)

        if action is RoomReactionAction.ADD:
            await self.api.sign_room(session, room)
        else:
            await self.api.unsign_room(session, room)

        return room
