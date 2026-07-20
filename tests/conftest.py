"""Shared fixtures: room factory and a stub platform API."""
from datetime import datetime, timedelta, timezone

import aiohttp
import pytest

from notbehomeless.models.base_api import BaseApi
from notbehomeless.models.room import Room
from notbehomeless.models.website import Website
from notbehomeless.websites.roomspot.exception import ReactionFailedError


@pytest.fixture
def make_room():
    """Factory for Room objects with sensible defaults, overridable per test."""

    def _make(
        room_id: int = 1,
        price: float = 500.0,
        size: float = 20.0,
        can_react: bool = True,
        action: str = "add",
        **kwargs,
    ) -> Room:
        now = datetime.now(timezone.utc)
        room = Room(
            website=Website.ROOMSPOT,
            room_id=room_id,
            title=f"Room {room_id}",
            link=f"https://example.com/{room_id}",
            price=price,
            city="Enschede",
            size=size,
            publication_date=now - timedelta(days=1),
            closing_date=now + timedelta(days=1),
            **kwargs,
        )
        room.can_react = can_react
        room.action = action
        return room

    return _make


class SimApi(BaseApi):
    """Simulates the API for testing purposes."""

    def __init__(self, rooms=None, fail_sign: bool = False):
        super().__init__()
        self.rooms = rooms or []
        self.fail_sign = fail_sign
        self.signed: list[int] = []
        self.unsigned: list[int] = []
        self.get_rooms_calls = 0

    async def _authorize(self, session, username, password):
        pass

    async def _get_rooms(self, session):
        self.get_rooms_calls += 1
        return self.rooms

    async def _sign_room(self, session, room):
        if self.fail_sign:
            raise ReactionFailedError(room.room_id)
        self.signed.append(room.room_id)

    async def _unsign_room(self, session, room):
        self.unsigned.append(room.room_id)


@pytest.fixture
def sim_api():
    return SimApi
