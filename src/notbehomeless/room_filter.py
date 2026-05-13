from notbehomeless.models.Room import Room


class RoomFilter:
    def __init__(
            self,
            max_price: float = -1,
            min_size: float = -1,
            kitchen: bool = False,
            bathroom: bool = False,
            furnished: bool = False,
            shared: bool = False

    ):
        self.max_price = max_price
        self.min_size = min_size

        self.kitchen = kitchen
        self.bathroom = bathroom
        self.furnished = furnished
        self.shared = shared

    def matches(self, room: Room) -> bool:
        if -1 <= self.max_price <= room.price:
            return False

        if -1 <= self.min_size >= room.size:
            return False

        if self.kitchen and not room.private_kitchen:
            return False

        if self.bathroom and not room.private_bathroom:
            return False

        if self.furnished and not room.furnished:
            return False

        if self.shared and not room.shared:
            return False

        return True
