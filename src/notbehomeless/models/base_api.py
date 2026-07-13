import logging
from abc import ABC, abstractmethod

import aiohttp

from notbehomeless.models.room import Room


class BaseApi(ABC):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def sign_room(self, session: aiohttp.ClientSession, room: Room):
        """
        Sign a room.
        :param session: The aiohttp session to use for the request.
        :param room: The room to sign.
        """
        pass

    @abstractmethod
    async def unsign_room(self, session: aiohttp.ClientSession, room: Room):
        """
        Unsign a room.
        :param session: The aiohttp session to use for the request.
        :param room: The room to unsign.
        """
        pass

    async def authorize(self, session, username, password):
        self.logger.info("Authorizing...")
        result = await self._authorize(session, username, password)
        self.logger.info("Authorization finished")
        return result

    @abstractmethod
    async def _authorize(self, session, username, password):
        """
                Authorize the user with the given username and password.
                :param session: The aiohttp session to use for the request.
                :param username: The username to authorize with.
                :param password: The password to authorize with.
                """

