import time
import jwt
from pathlib import Path
import pickle
from yarl import URL

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
        print(f"Failed to load cookies for {name}: {e}")


def is_token_expired(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    return time.time() > payload["exp"] - 300  # Consider token expired if it's within 5 minutes of expiring
