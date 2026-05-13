from dataclasses import dataclass
from notbehomeless.models.WebSite import WebSite
from notbehomeless.roomspot.allocation_type import AllocationType
from datetime import datetime

@dataclass(slots=True)
class Room:
    website: WebSite

    room_id: int

    title: str
    link: str

    price: float
    city: str
    size: float

    publication_date: datetime
    closing_date: datetime

    allocation_type: AllocationType | None = None

    private_kitchen: bool = False
    private_bathroom: bool = False
    furnished: bool = False
    shared: bool = False
    wifi: bool = False

    def __str__(self):
        details = [
                    "🍳 Kitchen" if self.private_kitchen else "❌ No kitchen",
                    "🛁 Private bathroom" if self.private_bathroom else "🚿 Shared bathroom",
                    "🪑 Furnished" if self.furnished else "📦 Unfurnished",
                    "👥 Shared housing" if self.shared else "🏡 Private housing",
                    "📶 Wi-Fi" if self.wifi else "📵 No Wi-Fi"
        ]

        details_text = "\n".join(f"   {detail}" for detail in details)

        return (
            f"\n"
            f"{'=' * 50}\n"
            f"🏠 {self.title}\n"
            f"{'-' * 50}\n"
            f"🌍 Website: {self.website}\n"
            f"🆔 Room ID: {self.room_id}\n"
            f"📍 City: {self.city}\n"
            f"💰 Price: €{self.price}\n"
            f"📏 Size: {self.size} m²\n"
            f"🔗 Link: {self.link}\n"
            f"{details_text + '\n' if details_text else ''}"
            f"{'=' * 50}"
        )
