import asyncio
import re

from notbehomeless.parsers.RoomspotApi import RoomspotApi
from notbehomeless.Utils import Config

from notbehomeless.models.Room import Room
from notbehomeless.parsers.Base_parser import BaseParser
from playwright.async_api import Page


class RoomspotParser(BaseParser):
    source_name = "https://www.roomspot.nl/"
    rooms_url = "/aanbod/te-huur"
    login_data = Config.login_data().get("roomspot", None)

    def __init__(self):
        if self.login_data is None:
            raise ValueError("No login data for Roomspot")

    async def fetch_listings(self) -> list[Room]:
        rooms = RoomspotApi().get_all_rooms()

        return rooms

    async def _authorize(self, page: Page):
        await page.locator("span").filter(has_text=re.compile(r"^Inloggen$")).click()
        await page.locator("#Login input[type=\"text\"]").fill(self.login_data.login)
        await page.locator("#zds-input-text-fb925346-7614-41d7-b7bf-2ae10faf7c4d-input").fill(self.login_data.password)
        await page.wait_for_timeout(1000)
        print("Successful auth")

async def main():
    parser = RoomspotParser()
    rooms = await parser.fetch_listings()

    print(f"Found {len(rooms)} rooms")

    for room in rooms:
        print(room)

if __name__ == "__main__":
    asyncio.run(main())