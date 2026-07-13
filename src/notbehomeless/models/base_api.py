import logging
from abc import ABC, abstractmethod

import aiohttp

from notbehomeless.models.room import Room


class BaseApi(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def _sign_room(self, session: aiohttp.ClientSession, room: Room):
        """
        Sign a room.
        :param session: The aiohttp session to use for the request.
        :param room: The room to sign.
        """
        pass

    async def sign_room(self, session: aiohttp.ClientSession, room: Room):
        self.logger.info("Signing room %s...", room.room_id)
        result = await self._sign_room(session, room)
        self.logger.info("Sign action is finished for room %s", room.room_id)
        return result


    @abstractmethod
    async def _unsign_room(self, session: aiohttp.ClientSession, room: Room):
        """
                Unsign a room.
                :param session: The aiohttp session to use for the request.
                :param room: The room to unsign.
                """
        pass

    async def unsign_room(self, session: aiohttp.ClientSession, room: Room):
        self.logger.info("Unsigning room %s...", room.room_id)
        result = await self._unsign_room(session, room)
        self.logger.info("Unsign action is finished for room %s", room.room_id)
        return result


    @abstractmethod
    async def _authorize(self, session, username, password):
        """
        Authorize the user with the given username and password.
        :param session: The aiohttp session to use for the request.
        :param username: The username to authorize with.
        :param password: The password to authorize with.
        """

    async def authorize(self, session, username, password):
        self.logger.info("Authorizing...")
        result = await self._authorize(session, username, password)
        self.logger.info("Authorization finished")
        return result


    @abstractmethod
    async def _get_rooms(self, session: aiohttp.ClientSession) -> list[Room]:
        """
        Get a list of rooms.
        :param session: The aiohttp session to use for the request.
        :return: A list of Room objects.
        """

    async def get_rooms(self, session: aiohttp.ClientSession) -> list[Room]:
        self.logger.info("Fetching rooms...")
        rooms: list[Room] = await self._get_rooms(session)
        self.logger.info("Fetched %d rooms", len(rooms))
        return rooms

