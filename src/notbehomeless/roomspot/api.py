"""
Roomspot API client for authorization, room retrieval,
and room reaction management.
"""

import aiohttp
from yarl import URL

from notbehomeless.models.base_api import BaseApi
from notbehomeless.models.room import Room
from notbehomeless.roomspot.authorizer import Authorizer
from notbehomeless.roomspot.room_parser import RoomspotRoomParser
from notbehomeless.roomspot.room_reactor import RoomReactor
from notbehomeless.roomspot.room_reaction_action import RoomReactionAction
from notbehomeless.roomspot.exception import ReactionFailedError
from notbehomeless.utils.files import load_json_file



class RoomspotApi(BaseApi):
    """
        Provides interaction with the Roomspot API.

        Supports:
        - authorization
        - session validation
        - room retrieval
        - room information fetching
        - adding and removing room reactions
        """
    MAIN_URL = URL("https://www.roomspot.nl/")
    ROOMS_URL = URL("https://studentenenschede-aanbodapi.zig365.nl/api/v1/actueel-aanbod")
    ROOM_INFO_URL = URL("https://www.roomspot.nl/portal/object/frontend/getobject/format/json")

    def __init__(self):
        super().__init__()
        self.reactor = RoomReactor()
        self.authorizer = Authorizer()

    async def _authorize(self, session: aiohttp.ClientSession, username: str, password: str):
        """
            Authorize the user.
        """
        await self.authorizer.authorize(session, username, password)

    async def _room_action(self, session: aiohttp.ClientSession, room: Room, action: RoomReactionAction):
        """
            Do an action (add/remove reaction) for the specified room.
        """
        try:
            await self.reactor.react_to_room(
                session,
                room,
                action
            )
        except (ValueError, aiohttp.ClientError) as e:
            self.logger.error("Failed to perform room action for room %s: %s", room.room_id, e)
            raise ReactionFailedError(room.room_id) from e

    async def sign_room(self, session: aiohttp.ClientSession, room: Room):
        """
            Add a reaction to the specified room.
        """
        await self._room_action(session, room, RoomReactionAction.ADD)

    async def unsign_room(self, session: aiohttp.ClientSession, room: Room):
        """
            Remove an existing reaction from the specified room.
        """
        await self._room_action(session, room, RoomReactionAction.REMOVE)

    async def perform_available_room_action(self, session: aiohttp.ClientSession, room: Room):
        """
            Perform the available action (add/remove reaction) for the specified room.
        """
        if room.can_react:
            if room.action == RoomReactionAction.ADD.value:
                await self.sign_room(session, room)
            elif room.action == RoomReactionAction.REMOVE.value:
                await self.unsign_room(session, room)
            else:
                self.logger.warning("Unknown action '%s' for room %s", room.action, room.room_id)
        else:
            self.logger.debug("No available action for room %s", room.room_id)

    async def _fetch_rooms(self, session: aiohttp.ClientSession, params: dict) -> dict:
        """
            Fetch a single page of rooms from the Roomspot API.
        """
        payload = await load_json_file('roomspot/data/hidden_filters.json')

        async with session.post(self.ROOMS_URL, params=params, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    async def get_room_info(self, session: aiohttp.ClientSession, room_id: int) -> dict:
        """
            Fetch detailed information for a specific Roomspot room.
        """
        params = {"id": str(room_id)}

        async with session.get(self.ROOM_INFO_URL, params=params) as response:
            response.raise_for_status()
            if response.status != 200:
                self.logger.warning("Failed to get room info for room id %s: %s", room_id, response.status)
            return await response.json()

    async def get_all_rooms(self, session: aiohttp.ClientSession) -> list[Room]:
        """
            Fetch and parse all available rooms from Roomspot.
        """
        params = {
            "limit": 50,
            "locale": "nl_NL",
            "page": 0,
            "sort": "!reactionData.zoekprofielMatchOrder,-reactionData.zoekprofielMatchOrder,+reactionData.aangepasteTotaleHuurprijs"
        }

        rooms = []
        seen_links = set()

        data = await self._fetch_rooms(session, params)

        page_count = data.get("_metadata", {}).get("page_count", 0)

        for page in range(page_count):
            params["page"] = page

            if page != 0:
                data = await self._fetch_rooms(session, params)

            for item in data.get("data", []):

                room = RoomspotRoomParser.parse(item)
                if room is None:
                    continue

                if room.link in seen_links:
                    continue

                seen_links.add(room.link)
                rooms.append(room)

        await self.reactor.add_room_reaction_data(session, rooms)
        self.logger.info("Fetched %s rooms from Roomspot", len(rooms))
        return rooms

