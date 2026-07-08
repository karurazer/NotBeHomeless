"""
Reusable FastAPI dependencies.

Shared resources (the aiohttp session, platform clients) are created once in the
app lifespan and stored on ``app.state``; these helpers hand them to endpoints via
``Depends``.
"""
from typing import Annotated

import aiohttp
from fastapi import Depends, Query, Request

from notbehomeless.roomspot.api import RoomspotApi
from notbehomeless.roomspot.service import RoomspotService
from notbehomeless.service.room_filter import RoomFilter


def get_session(request: Request) -> aiohttp.ClientSession:
    """Return the application-wide aiohttp session."""
    return request.app.state.session


def get_roomspot(request: Request) -> RoomspotApi:
    """Return the shared Roomspot client."""
    return request.app.state.roomspot


def get_roomspot_service(request: Request) -> RoomspotService:
    """Wrap the shared Roomspot client in a high-level service."""
    return RoomspotService(request.app.state.roomspot)


def get_room_filter(
    max_price: float = Query(-1, description="Max total rent, -1 for no limit"),
    min_size: float = Query(-1, description="Min dwelling size in m², -1 for no limit"),
    kitchen: bool = Query(False, description="Require a private kitchen"),
    bathroom: bool = Query(False, description="Require a private bathroom"),
    furnished: bool = Query(False, description="Require the room to be furnished")
) -> RoomFilter:
    """Build a ``RoomFilter`` from query parameters."""
    return RoomFilter(
        max_price=max_price,
        min_size=min_size,
        kitchen=kitchen,
        bathroom=bathroom,
        furnished=furnished
    )


SessionDep = Annotated[aiohttp.ClientSession, Depends(get_session)]
RoomspotDep = Annotated[RoomspotApi, Depends(get_roomspot)]
RoomspotServiceDep = Annotated[RoomspotService, Depends(get_roomspot_service)]
RoomFilterDep = Annotated[RoomFilter, Depends(get_room_filter)]