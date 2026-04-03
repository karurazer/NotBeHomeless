import aiohttp

from notbehomeless.models.WebSite import WebSite
from src.notbehomeless.models.Room import Room


class RoomspotApi:
    BASE_URL = "https://studentenenschede-aanbodapi.zig365.nl/api/v1/actueel-aanbod"

    def __init__(self):
        self.params = {
            "limit": 60,
            "locale": "nl_NL",
            "page": 0,
            "sort": "!reactionData.zoekprofielMatchOrder,-reactionData.zoekprofielMatchOrder,+reactionData.aangepasteTotaleHuurprijs"
        }

    async def _fetch(self, session: aiohttp.ClientSession):
        params = self.params.copy()

        async with session.get(self.BASE_URL, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_all_rooms(self):
        rooms = []
        seen_links = set()

        async with aiohttp.ClientSession() as session:
            data = await self._fetch(session)

            page_count = data.get("_metadata", {}).get("page_count", 0)

            for page in range(page_count):
                self.params["page"] = page

                if page != 0:
                    data = await self._fetch(session)

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


if __name__ == "__main__":
    import asyncio

    api = RoomspotApi()
    rooms = asyncio.run(api.get_all_rooms())
    for room in rooms:
        print(room)