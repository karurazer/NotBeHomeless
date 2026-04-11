import asyncio
import aiohttp
from pathlib import Path
from notbehomeless.Utils.Config import AuthData
from notbehomeless.models.WebSite import WebSite
from notbehomeless.parsers.RoomspotApi import RoomspotApi
from notbehomeless.Utils import Config
from notbehomeless.models.Room import Room
from notbehomeless.parsers.Base_parser import BaseParser



class RoomspotParser(BaseParser):
    source_name = "https://www.roomspot.nl/"
    rooms_url = "/aanbod/te-huur"
    login_data: AuthData = Config.login_data(WebSite.ROOMSPOT)
    STORAGE_PATH = Path(__file__).resolve().parent.parent / "storage" / "roomspot_state.json"
    room_spot_api = RoomspotApi()

    def __init__(self):
        self.session = aiohttp.ClientSession()
        if self.login_data is None:
            raise ValueError("No login data for Roomspot")

    async def _authorize(self):
        await self.room_spot_api.authorize(self.session, self.login_data.login, self.login_data.password)
        print("Authorized RoomspotParser")

    async def sign_a_room(self, room: Room):
        pass

    async def fetch_listings(self) -> list[Room]:
        rooms = await RoomspotApi().get_all_rooms(self.session)

        return rooms

    async def close(self):
        print("Closing RoomspotParser")
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()



async def test_auth():
    async with RoomspotParser() as r:
        await r._authorize()
        rooms = await r.fetch_listings()

        print(f"Found {len(rooms)} rooms")

        for room in rooms:
            print(room)

if __name__ == "__main__":
    asyncio.run(test_auth())