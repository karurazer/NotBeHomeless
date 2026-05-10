"""
Roomspot API client for authorization, room retrieval,
and room reaction management.
"""
import time

import aiohttp
from yarl import URL
from notbehomeless.models.WebSite import WebSite
from notbehomeless.models.Room import Room
from notbehomeless.Utils.Config import login_data
from notbehomeless.Utils.Utils import load_cookies
from notbehomeless.Utils.Utils import save_cookies
from notbehomeless.Utils.Utils import is_token_expired
from notbehomeless.roomspot.room_reactor import RoomReactor
from notbehomeless.roomspot.room_reaction_action import RoomReactionAction

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
    LOGIN_URL = URL("https://www.roomspot.nl/portal/proxy/frontend/api/v1/oauth/token")
    REFRESH_TOKEN_URL = URL("https://www.roomspot.nl/portal/account/frontend/loginbyservice/format/json")
    ROOM_INFO_URL = URL("https://www.roomspot.nl/portal/object/frontend/getobject/format/json")

    login_payload_template = {
        "grant_type": "password",
        "client_id": "wzp",
        "username": "",
        "password": ""
    }

    def __init__(self):
        self.reactor = RoomReactor()
        self.params = {
            "limit": 50,
            "locale": "nl_NL",
            "page": 0,
            "sort": "!reactionData.zoekprofielMatchOrder,"
                    "-reactionData.zoekprofielMatchOrder,"
                    "+reactionData.aangepasteTotaleHuurprijs"
        }

    async def sign_for_room(self, session: aiohttp.ClientSession, room: Room):
        """
            Add a reaction to the specified room.
        """
        room_info = await self.get_room_info(session, room.room_id)
        reaction_data = room_info.get("result", {}).get("reactionData", {})
        try:
            await self.reactor.react_to_room(
                session,
                reaction_data,
                room,
                RoomReactionAction.ADD
            )
        except ValueError as e:
            print(f"Failed to sign for room {room.room_id}: {e}")

    async def remove_reaction_for_room(self, session: aiohttp.ClientSession, room: Room):
        """
            Remove an existing reaction from the specified room.
        """
        room_info = await self.get_room_info(session, room.room_id)
        reaction_data = room_info.get("result", {}).get("reactionData", {})

        try:
            await self.reactor.react_to_room(
                session,
                reaction_data,
                room,
                RoomReactionAction.REMOVE
            )
        except ValueError as e:
            print(f"Failed to remove reaction for room {room.room_id}: {e}")

    async def _fetch_rooms(self, session: aiohttp.ClientSession) -> dict:
        """
            Fetch a single page of rooms from the Roomspot API.
        """
        params = self.params.copy()

        async with session.get(self.ROOMS_URL, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_room_info(self, session: aiohttp.ClientSession, room_id: int) -> dict:
        """
            Fetch a single page of rooms from the Roomspot API.
        """
        params = {"id": str(room_id)}

        async with session.get(self.ROOM_INFO_URL, params=params) as response:
            response.raise_for_status()
            if response.status != 200:
                print(f"Failed to get room info for room id {room_id}: {response.status}")
            return await response.json()

    async def get_all_rooms(self, session: aiohttp.ClientSession) -> list[Room]:
        """
            Fetch and parse all available rooms from Roomspot.
        """
        rooms = []
        seen_links = set()

        data = await self._fetch_rooms(session)

        page_count = data.get("_metadata", {}).get("page_count", 0)

        for page in range(page_count):
            self.params["page"] = page

            if page != 0:
                data = await self._fetch_rooms(session)

            for item in data.get("data", []):

                room_id = item.get("id", "")
                street = item.get("street", "")
                house = item.get("houseNumber", "")
                addition = item.get("houseNumberAddition", "")

                price = item.get("totalRent")
                location = item.get("city", {}).get("name")
                size = item.get("areaDwelling")

                title = f"{street} {house} {addition}".strip()

                url_key = item.get("urlKey")
                if not url_key:
                    continue

                link = f"https://www.roomspot.nl/aanbod/te-huur/details/{url_key}"

                if link in seen_links:
                    continue

                seen_links.add(link)

                room = Room(
                    WebSite.ROOMSPOT,
                    room_id,
                    title,
                    price,
                    location,
                    link,
                    size
                )

                rooms.append(room)

        return rooms

    async def authorize(self, session: aiohttp.ClientSession, username: str, password: str):
        """
            Authorize the user and store Roomspot session cookies.
        """
        load_cookies(session, WebSite.ROOMSPOT.name)
        if await self.is_valid_session(session):
            print("Already logged in to Roomspot")
            return

        login_payload = self.login_payload_template.copy()
        login_payload["username"] = username
        login_payload["password"] = password

        async with session.post(self.LOGIN_URL, data=login_payload) as response:
            if response.status != 200:
                text = await response.text()

                print(text)
                raise ValueError(f"Failed to login to Roomspot: {response.status}")

            cookies = session.cookie_jar.filter_cookies(self.MAIN_URL)
            save_cookies(cookies, WebSite.ROOMSPOT.name)
            print("Successfully updated Roomspot cookies")

    async def is_valid_session(self, session: aiohttp.ClientSession) -> bool:
        """
            Check whether the current Roomspot session is still valid.
        """
        try:
            cookies = session.cookie_jar.filter_cookies(self.MAIN_URL)
        except KeyError:
            return False

        token = cookies.get("backendToken")
        if token is None:
            return False

        if is_token_expired(token.value):
            return False

        async with session.post(self.REFRESH_TOKEN_URL) as r:
            return r.status == 200

async def test_room_retrieval():
    """
       Test room retrieval from Roomspot.
       """
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        rooms = await api.get_all_rooms(session)
        for room in rooms:
            print(room)
        print("Total find rooms: ", len(rooms))

async def test_sign():
    """
        Test authorization and room reaction submission.
    """
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(WebSite.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        rooms = await api.get_all_rooms(session)

        if rooms:
            await api.sign_for_room(session, rooms[0])
            print("Waiting for 2 seconds before removing reaction...")
            time.sleep(2)
            await api.remove_reaction_for_room(session, rooms[0])

if __name__ == "__main__":
    import asyncio

    asyncio.run(test_sign())
