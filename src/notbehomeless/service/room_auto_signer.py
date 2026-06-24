from notbehomeless.models.room import Room
from notbehomeless.service.room_filter import RoomFilter


class RoomAutoSigner:
    def __init__(self, rooms: set[Room], room_filter: RoomFilter):
        self.rooms = rooms
        self.room_filter = room_filter

