"""
Application entry point: the FastAPI application factory, lifespan, and uvicorn runner.

The lifespan opens shared resources once at startup (logging, the aiohttp session,
the Roomspot client, an initial authorization) and closes them at shutdown.
"""
import logging
from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from fastapi import FastAPI

from notbehomeless.models.website import Website
from notbehomeless.roomspot.api import RoomspotApi
from notbehomeless.utils.config import login_data
from notbehomeless.config.logging_config import setup_logging
from notbehomeless.factory.exceptions_factory import init_exceptions_handler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    session = aiohttp.ClientSession()
    roomspot = RoomspotApi()

    creds = login_data(Website.ROOMSPOT)
    if creds.login and creds.password:
        await roomspot.authorize(session, creds.login, creds.password)
    else:
        logger.warning("Roomspot credentials are not set; requests will be unauthenticated")

    app.state.session = session
    app.state.roomspot = roomspot

    yield

    await session.close()



def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    fastapi = FastAPI(title="notBeHomeless", version="0.1.0", lifespan=lifespan)

    from notbehomeless.api.routers import health, rooms

    fastapi.include_router(health.router)
    fastapi.include_router(rooms.router)

    init_exceptions_handler(fastapi)

    return fastapi


if __name__ == "__main__":
    uvicorn.run(
        "notbehomeless.main:create_app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        factory=True,
    )
