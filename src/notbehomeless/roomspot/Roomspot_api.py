import aiohttp
from yarl import URL
from notbehomeless.models.WebSite import WebSite
from notbehomeless.models.Room import Room
from notbehomeless.Utils.Config import login_data
from notbehomeless.Utils.Utils import load_cookies
from notbehomeless.Utils.Utils import save_cookies
from notbehomeless.Utils.Utils import is_token_expired
from urllib.parse import parse_qs
from notbehomeless.roomspot.Room_reaction_action import RoomReactionAction


class RoomspotApi:
    MAIN_URL = URL("https://www.roomspot.nl/")
    ROOMS_URL = URL("https://studentenenschede-aanbodapi.zig365.nl/api/v1/actueel-aanbod")
    LOGIN_URL = URL("https://www.roomspot.nl/portal/proxy/frontend/api/v1/oauth/token")
    REFRESH_TOKEN_URL = URL("https://www.roomspot.nl/portal/account/frontend/loginbyservice/format/json")
    REACT_ROOM_URL = URL("https://www.roomspot.nl/portal/object/frontend/react/format/json")
    ROOM_INFO_URL = URL("https://www.roomspot.nl/portal/object/frontend/getobject/format/json")
    ROOM_GET_FORM_SUBMIT_ONLY_CONFIG = URL("https://www.roomspot.nl/portal/core/frontend/getformsubmitonlyconfiguration/format/json")

    login_payload_template = {
        "grant_type": "password",
        "client_id": "wzp",
        "username": "",
        "password": ""
    }

    def __init__(self):
        self.params = {
            "limit": 60,
            "locale": "nl_NL",
            "page": 0,
            "sort": "!reactionData.zoekprofielMatchOrder,"
                    "-reactionData.zoekprofielMatchOrder,"
                    "+reactionData.aangepasteTotaleHuurprijs"
        }

    async def _fetch_rooms(self, session: aiohttp.ClientSession) -> dict:
        params = self.params.copy()

        async with session.get(self.ROOMS_URL, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_all_rooms(self, session: aiohttp.ClientSession) -> list[Room]:
        rooms = []
        seen_links = set()

        data = await self._fetch_rooms(session)

        page_count = data.get("_metadata", {}).get("page_count", 0)

        for page in range(page_count):
            self.params["page"] = page

            if page != 0:
                data = await self._fetch_rooms(session)

            for item in data.get("data", []):

                id = item.get("id", "")
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
                    id,
                    title,
                    price,
                    location,
                    link,
                    size
                )

                rooms.append(room)

        return rooms

    async def sign_for_room(self, session: aiohttp.ClientSession, room: Room):
        room_info = await self.get_room_info(session, room.id)
        reaction_data = room_info.get("result", {}).get("reactionData", {})
        if reaction_data is None:
            raise ValueError("No reaction data for room")

        action = reaction_data.get("action", "")
        match action:
            case RoomReactionAction.ADD.value:
                await self._handle_add_action(session, room, reaction_data)

            case RoomReactionAction.REMOVE.value:
                print(f"Room already registered:\n {room}\n===================")
                return

            case _:
                raise NotImplementedError(
                    f"Unknown action for signing up for room: {action}"
                )

    async def _handle_add_action(self, session: aiohttp.ClientSession, room: Room, reaction_data: dict):
        url = reaction_data.get("url", "")
        if not url:
            raise ValueError("No URL for signing up for room")
        params = parse_qs(url[1:])
        add_id = int(params["add"][0])
        dwelling_id = int(params["dwellingID"][0])

        form_submit_only = await self.get_form_submit_only_config(session)
        form = form_submit_only.get("form", {})
        hash__ = form.get("elements", {}).get("__hash__", {}).get("initialData", "")
        id__ = form.get("id", "")

        payload = {
            "add": add_id,
            "dwellingID": dwelling_id,
            "__hash__": str(hash__),
            "__id__": str(id__)
        }

        async with session.post(self.REACT_ROOM_URL, data=payload) as response:
            response.raise_for_status()
            if response.status == 200:
                print(f"|Successfully signed up for room:\n {room}\n===================")
            return await response.json()

    async def get_form_submit_only_config(self, session: aiohttp.ClientSession) -> dict:
        async with session.get(self.ROOM_GET_FORM_SUBMIT_ONLY_CONFIG) as response:
            response.raise_for_status()
            return await response.json()

    async def get_room_info(self, session: aiohttp.ClientSession, room_id: int) -> dict:
        payload = {"id": str(room_id)}
        print(f"Getting room info for room id {room_id}")
        async with session.get(self.ROOM_INFO_URL, params=payload) as response:
            response.raise_for_status()
            if response.status != 200:
                print(f"Failed to get room info for room id {room_id}: {response.status}")
            return await response.json()

    async def authorize(self, session: aiohttp.ClientSession, username: str, password: str):
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

async def test():
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        rooms = await api.get_all_rooms(session)
        for room in rooms:
            print(room)
        print("Total find rooms: ", len(rooms))

async def test_sign():
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(WebSite.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        rooms = await api.get_all_rooms(session)

        if rooms:
            await api.sign_for_room(session, rooms[0])

if __name__ == "__main__":
    import asyncio

    asyncio.run(test_sign())
