import asyncio
import logging

import aiohttp
from notbehomeless.models.base_api import BaseApi
from notbehomeless.models.room import Room
from notbehomeless.service.room_filter import RoomFilter

logger = logging.getLogger(__name__)

"""
@:param period: The period in milliseconds to check for new rooms to sign.
"""
class RoomAutoSigner:
    def __init__(self, room_filter: RoomFilter, api: BaseApi, session: aiohttp.ClientSession, period: int = 60_000):
        self.room_filter = room_filter
        self.period = period
        self.api = api
        self.session = session

    async def start(self):
        while True:
            await self._sign_rooms()
            logger.info("Waiting for %s milliseconds before next check.", self.period)
            await asyncio.sleep(self.period / 1000)

    async def _sign_rooms(self):
        rooms: list[Room] = await self.api.get_rooms(self.session)
        if not rooms:
            logger.info("No rooms found to auto sign.")
            return

        filtered_rooms = [r for r in rooms if self.room_filter.matches(r) and r.action != "remove"]
        if not filtered_rooms:
            logger.info("No rooms found to auto sign after filtering.")
            return

        logger.info("Found %s rooms to auto sign. Start signing", len(rooms))

        for room in filtered_rooms:
            try:
                await self.api.sign_room(self.session, room)
                logger.debug("Room details: %s", room)

            except Exception as e:
                logger.exception("Failed to sign room %s: %s", room.room_id, str(e))

        logger.info("Finished signing rooms.")



