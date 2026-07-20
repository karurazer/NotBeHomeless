import logging

import aiohttp
from yarl import URL

from notbehomeless.utils.cookies import save_cookies, load_cookies
from notbehomeless.utils.token import is_token_expired
from notbehomeless.models.website import Website

logger = logging.getLogger(__name__)


class Authorizer:
    LOGIN_URL = URL("https://www.roomspot.nl/portal/proxy/frontend/api/v1/oauth/token")
    MAIN_URL = URL("https://www.roomspot.nl/")
    REFRESH_TOKEN_URL = URL("https://www.roomspot.nl/portal/account/frontend/loginbyservice/format/json")

    login_payload_template = {
        "grant_type": "password",
        "client_id": "wzp",
        "username": "",
        "password": ""
    }

    async def authorize(self, session: aiohttp.ClientSession, username: str, password: str):
        """
            Authorize the user and store Roomspot session cookies.
        """
        load_cookies(session, Website.ROOMSPOT.name)
        if await self.is_valid_session(session):
            logger.info("Already logged in to Roomspot")
            return

        login_payload = self.login_payload_template.copy()
        login_payload["username"] = username
        login_payload["password"] = password

        async with session.post(self.LOGIN_URL, data=login_payload) as response:
            if response.status != 200:
                text = await response.text()

                logger.error("Roomspot login failed (%s): %s", response.status, text)
                raise ValueError(f"Failed to login to Roomspot: {response.status}")

            cookies = session.cookie_jar.filter_cookies(self.MAIN_URL)
            save_cookies(cookies, Website.ROOMSPOT.name)
            logger.info("Successfully updated Roomspot cookies")

    async def is_valid_session(self, session: aiohttp.ClientSession) -> bool:
        """
            Check whether the current Roomspot session is still valid.
        """
        try:
            cookies = session.cookie_jar.filter_cookies(self.MAIN_URL)
        except KeyError:
            return False

        token = cookies.get("backendToken")
        if token is None:
            return False

        if is_token_expired(token.value):
            return False

        async with session.post(self.REFRESH_TOKEN_URL) as response:
            return response.status == 200
