import asyncio
import os
import re
import time
from pathlib import Path
import jwt

from notbehomeless.parsers.RoomspotApi import RoomspotApi
from notbehomeless.Utils import Config

from notbehomeless.models.Room import Room
from notbehomeless.parsers.Base_parser import BaseParser
from playwright.async_api import async_playwright, Browser


class RoomspotParser(BaseParser):
    source_name = "https://www.roomspot.nl/"
    rooms_url = "/aanbod/te-huur"
    login_data = Config.login_data().get("roomspot", None)
    STORAGE_PATH = Path(__file__).resolve().parent.parent / "storage" / "roomspot_state.json"

    def __init__(self):
        self.browser: Browser = None
        self.playwright = None
        self.context = None

        if self.login_data is None:
            raise ValueError("No login data for Roomspot")

    async def _start_browser(self, headless: bool = True):
        if self.playwright is None:
            self.playwright = await async_playwright().start()

        if self.browser is None:
            self.browser = await self.playwright.chromium.launch(headless=headless)

        if self.context is None:
            if os.path.exists(self.STORAGE_PATH):
                self.context = await self.browser.new_context(storage_state=self.STORAGE_PATH)
            else:
                self.context = await self.browser.new_context()

    async def sign_a_room(self, room: Room):
        await self._authorize()

        link = room.link
        page = await self.context.new_page()

    async def _reset_context(self):
        if self.context is not None:
            await self.context.close()
            self.context = None

        self.context = await self.browser.new_context()

    async def fetch_listings(self) -> list[Room]:
        rooms = await RoomspotApi().get_all_rooms()

        return rooms

    async def _authorize(self):
        await self._start_browser()
        if await self._is_session_valid():
            print("Session still valid, skipping auth")
            return

        await self._reset_context()


        page = await self.context.new_page()

        try:
            await page.goto(self.source_name)

            await page.locator("span").filter(has_text=re.compile(r"^Inloggen$")).click()
            await page.locator('#Login input[type="text"]').fill(self.login_data.login)
            await page.locator('input[type="password"]').fill(self.login_data.password)
            await page.locator('zds-button[type="submit"]').filter(has_text="InLoggen").click()

            print("Successful auth")
            await page.wait_for_timeout(1000)

            self.STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            await self.context.storage_state(path=self.STORAGE_PATH)
        finally:
            await page.close()

    def _ensure_browser_running(self):
        if self.browser is None or self.playwright is None or self.context is None:
            raise RuntimeError("Browser not running. Call start_browser() first.")

    async def _token_not_expired(self):
        cookies = await self.context.cookies()
        token = next((c["value"] for c in cookies if c["name"] == "backendToken"), None)

        if not token:
            return False

        payload = jwt.decode(token, options={"verify_signature": False})
        return time.time() < payload["exp"] - 300

    async def _is_session_valid(self):
        self._ensure_browser_running()
        response = await self.context.request.get(
            "https://studentenenschede-aanbodapi.zig365.nl/api/v1/actueel-aanbod"
        )

        if await self._token_not_expired():
            print("Token valid, session should be valid")

        if response.status == 200:
            print("Session valid")
            return True

        if response.status in [401, 403]:
            print("Session expired")
            return False
        return False

    async def close(self):
        if self.context is not None:
            await self.context.close()
            self.context = None

        if self.browser is not None:
            await self.browser.close()
            self.browser = None

        if self.playwright is not None:
            await self.playwright.stop()
            self.playwright = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("Closing RoomspotParser")
        await self.close()

async def main():
    parser = RoomspotParser()
    rooms = await parser.fetch_listings()

    print(f"Found {len(rooms)} rooms")

    for room in rooms:
        print(room)



async def test_auth():
    async with RoomspotParser() as r:
        await r._authorize()

if __name__ == "__main__":
    asyncio.run(test_auth())