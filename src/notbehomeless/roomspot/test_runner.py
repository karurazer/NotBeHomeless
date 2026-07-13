import aiohttp
import logging

from notbehomeless.models.website import Website
from src.notbehomeless.roomspot.api import RoomspotApi
from notbehomeless.utils.config import login_data

logger = logging.getLogger(__name__)

async def test_room_retrieval():
    """
       Test room retrieval from Roomspot.
    """
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(Website.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        rooms = await api.get_rooms(session)

        rooms_text = "\n".join(str(room) for room in rooms)
        rooms_text += "\n\n" + f"Total rooms: {len(rooms)}"
        logger.debug(rooms_text)


async def test_sign():
    """
        Test authorization and room reaction submission.
    """
    import asyncio

    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(Website.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        rooms = await api.get_rooms(session)
        if rooms:
            await api.sign_room(session, rooms[0])
            logger.info("Waiting for 5 seconds before removing reaction...")

            await asyncio.sleep(5)
            await api.unsign_room(session, rooms[0])


if __name__ == "__main__":
    import asyncio

    from notbehomeless.config.logging_config import setup_logging

    setup_logging(logging.DEBUG)
    asyncio.run(test_room_retrieval())
