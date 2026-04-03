import requests

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

    def _fetch(self):
        response = requests.get(self.BASE_URL, params=self.params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_all_rooms(self):
        rooms = []
        seen_links = set()

        data = self._fetch()
        page_count = data.get("_metadata", {}).get("page_count", None)

        for page in range(page_count):
            self.params["page"] = page

            if page != 0:
                data = self._fetch()

            for item in data.get("data", []):

                street = item.get("street", "")
                house = item.get("houseNumber", "")
                addition = item.get("houseNumberAddition", "")

                price = item.get("totalRent")
                location = item.get("city", {}).get("name")
                size = item.get("areaDwelling")

                title = f"{street} {house} {addition} {price}".strip()

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