from notbehomeless.models.WebSite import WebSite


class Room:
    def __init__(self, website: WebSite, title: str, price: float, location: str, link: str, size: int):
        self.website = website
        self.title = title
        self.price = price
        self.location = location
        self.link = link
        self.size = size

    def __str__(self):
        return (
            f"   From: {self.website}\n"
            f"🏠 Room: {self.title}\n"
            f"📍 Location: {self.location}\n"
            f"💰 Price: €{self.price}\n"
            f"📏 Size: {self.size} m²\n"
            f"🔗 Link: {self.link}\n"
            f"{'-' * 40}"
        )
