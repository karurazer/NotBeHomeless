from notbehomeless.models.room import Room
from notbehomeless.models.website import Website
from datetime import datetime

from notbehomeless.models.allocation_type import AllocationType


class RoomspotRoomParser:
    @staticmethod
    def parse(item: dict) -> Room | None:
        room_id = int(item.get("id", ""))
        street = item.get("street", "")
        house = item.get("houseNumber", "")
        addition = item.get("houseNumberAddition", "")

        price = float(item.get("totalRent", ""))
        city = item.get("city", {}).get("name", "")
        size = float(item.get("areaDwelling", ""))

        title = f"{street} {house} {addition}".strip()
        publication_date_raw = item.get("publicationDate", "")
        closing_date_raw = item.get("closingDate", "")

        model_category = item.get("toewijzingModelCategorie", {}).get("code", "")
        allocation = AllocationType.from_code(model_category)

        if not publication_date_raw or not closing_date_raw:
            return None

        publication_date = datetime.fromisoformat(publication_date_raw.replace("Z", "+00:00"))
        closing_date = datetime.fromisoformat(closing_date_raw.replace("Z", "+00:00"))

        url_key = item.get("urlKey")
        if not url_key:
            return None

        link = f"https://www.roomspot.nl/aanbod/te-huur/details/{url_key}"

        features = {
            f.get("localizedLabel")
            for f in item.get("specifiekeVoorzieningen", [])
        }

        return Room(
            Website.ROOMSPOT,
            room_id,
            title,
            link,
            price,
            city,
            size,
            publication_date,
            closing_date,
            allocation_type=allocation,
            private_kitchen="Eigen keuken" in features,
            private_bathroom="Eigen badkamer" in features,
            furnished="Gemeubileerd" in features,
            wifi="Incl. internet" in features
        )
