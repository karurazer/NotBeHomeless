from notbehomeless.models.Room import Room
from notbehomeless.models.WebSite import WebSite

class RoomspotRoomParser:
    @staticmethod
    def parse(item: dict) -> Room | None:
        room_id = int(item.get("id", ""))
        street = item.get("street", "")
        house = item.get("houseNumber", "")
        addition = item.get("houseNumberAddition", "")

        price = float(item.get("totalRent", ""))
        location = item.get("city", {}).get("name", "")
        size = float(item.get("areaDwelling", ""))

        title = f"{street} {house} {addition}".strip()

        url_key = item.get("urlKey")
        if not url_key:
            return None

        link = f"https://www.roomspot.nl/aanbod/te-huur/details/{url_key}"


        return Room(
            WebSite.ROOMSPOT,
            room_id,
            title,
            price,
            location,
            link,
            size
        )
