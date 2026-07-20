import logging
import pickle
from pathlib import Path

from yarl import URL

logger = logging.getLogger(__name__)


def save_cookies(cookies, name: str):


    url = Path(__file__).resolve().parent.parent / "storage" / "cookies" / f"{name}.pkl"
    url.parent.mkdir(parents=True, exist_ok=True)

    with open(url, "wb") as f:
        pickle.dump(cookies, f)


def load_cookies(session, name: str):


    url = Path(__file__).resolve().parent.parent / "storage" / "cookies" / f"{name}.pkl"
    if not url.exists():
        return
    try:
        with open(url, "rb") as f:
            cookies = pickle.load(f)
        session.cookie_jar.update_cookies(cookies, response_url=URL("https://www.roomspot.nl"))
    except Exception as e:
        logger.exception("Failed to load cookies for %s: %s", name, e)