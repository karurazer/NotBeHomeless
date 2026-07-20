from notbehomeless.models.room import Room


class RoomFilter:
    def __init__(
            self,
            max_price: float = -1,
            min_size: float = -1,
            kitchen: bool = False,
            bathroom: bool = False,
            furnished: bool = False

    ):
        self.max_price = max_price
        self.min_size = min_size

        self.kitchen = kitchen
        self.bathroom = bathroom
        self.furnished = furnished

    def matches(self, room: Room) -> bool:
        if self.max_price != -1 and room.price > self.max_price:
            return False

        if self.min_size != -1 and room.size < self.min_size:
            return False

        if self.kitchen and not room.private_kitchen:
            return False

        if self.bathroom and not room.private_bathroom:
            return False

        if self.furnished and not room.furnished:
            return False

        return True
