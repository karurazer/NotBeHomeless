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

async def test_auto_signer():
    """
        Test the RoomAutoSigner functionality.
    """
    from notbehomeless.service.room_auto_signer import RoomAutoSigner
    from notbehomeless.service.room_filter import RoomFilter

    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()

        user_data = login_data(Website.ROOMSPOT)
        username = user_data.login
        password = user_data.password
        await api.authorize(session, username=username, password=password)

        room_filter = RoomFilter(max_price=-1, min_size=20, kitchen=True, bathroom=True, furnished=True)
        auto_signer = RoomAutoSigner(room_filter=room_filter, api=api, session=session, period=10_000)

        await auto_signer.start()

if __name__ == "__main__":
    import asyncio

    from notbehomeless.config.logging_config import setup_logging

    setup_logging(logging.DEBUG)
    try:
        asyncio.run(test_auto_signer())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user.")
