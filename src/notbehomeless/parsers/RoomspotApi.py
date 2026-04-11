import aiohttp
from yarl import URL

from notbehomeless.models.WebSite import WebSite
from notbehomeless.models.Room import Room
from notbehomeless.Utils.Utils import save_cookies, load_cookies
from notbehomeless.Utils.Utils import is_token_expired
from notbehomeless.Utils.Config import login_data

class RoomspotApi:
    MAIN_URL = URL("https://www.roomspot.nl/")
    ROOMS_URL = URL("https://studentenenschede-aanbodapi.zig365.nl/api/v1/actueel-aanbod")
    LOGIN_URL = URL("https://www.roomspot.nl/portal/proxy/frontend/api/v1/oauth/token")

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
            "sort": "!reactionData.zoekprofielMatchOrder,-reactionData.zoekprofielMatchOrder,+reactionData.aangepasteTotaleHuurprijs"
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
                    title,
                    price,
                    location,
                    link,
                    size
                )

                rooms.append(room)

        return rooms

    async def authorize(self, session: aiohttp.ClientSession, username: str, password: str):
        load_cookies(session, WebSite.ROOMSPOT.name)
        if self._is_valid_session(session):
            print("Session is still valid, no need to login again")
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
            print("Successfully logged in to Roomspot")

    def _is_valid_session(self, session: aiohttp.ClientSession) -> bool:
        try:
            cookies = session.cookie_jar.filter_cookies(self.MAIN_URL)
        except KeyError:
            return False

        token = cookies.get("backendToken")
        if token is None:
            return False

        return not is_token_expired(token.value)

async def test_login():
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()
        user_data =  login_data(WebSite.ROOMSPOT)
        username = user_data.login
        password = user_data.password

        await api.authorize(session, username=username, password=password)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_login())
