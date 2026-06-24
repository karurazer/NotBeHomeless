"""
Roomspot API client for authorization, room retrieval,
and room reaction management.
"""
import logging

import aiohttp
from yarl import URL

from notbehomeless.models.website import Website
from notbehomeless.models.room import Room
from notbehomeless.utils.config import login_data
from notbehomeless.roomspot.authorizer import Authorizer
from notbehomeless.roomspot.room_parser import RoomspotRoomParser
from notbehomeless.roomspot.room_reactor import RoomReactor
from notbehomeless.roomspot.room_reaction_action import RoomReactionAction
from notbehomeless.utils.files import load_json_file

logger = logging.getLogger(__name__)


class RoomspotApi:
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
        self.reactor = RoomReactor()
        self.authorizer = Authorizer()

    async def authorize(self, session: aiohttp.ClientSession, username: str, password: str):
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
        except ValueError as e:
            logger.error("Failed to perform room action for room %s: %s", room.room_id, e)

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
                logger.warning("Unknown action '%s' for room %s", room.action, room.room_id)
        else:
            logger.debug("No available action for room %s", room.room_id)

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
                logger.warning("Failed to get room info for room id %s: %s", room_id, response.status)
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
        logger.info("Fetched %s rooms from Roomspot", len(rooms))
        return rooms


async def test_room_retrieval():
    """
       Test room retrieval from Roomspot.
    """
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(Website.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        rooms = await api.get_all_rooms(session)

        rooms_text = "\n".join(str(room) for room in rooms)
        rooms_text += "\n\n" + f"Total rooms: {len(rooms)}"
        logger.debug(rooms_text)


async def test_sign():
    """
        Test authorization and room reaction submission.
    """
    import asyncio

    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(Website.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        rooms = await api.get_all_rooms(session)
        if rooms:
            await api.sign_room(session, rooms[0])
            logger.info("Waiting for 5 seconds before removing reaction...")

            await asyncio.sleep(5)
            await api.unsign_room(session, rooms[0])


if __name__ == "__main__":
    import asyncio

    from notbehomeless.utils.logging_config import setup_logging

    setup_logging()
    asyncio.run(test_room_retrieval())
