from notbehomeless.models.Room import Room
from notbehomeless.room_filter import RoomFilter


class RoomAutoSigner:
    def __init__(self, rooms: set[Room], room_filter: RoomFilter):
        self.rooms = rooms
        self.room_filter = room_filter

