import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AuthData:
    login: str
    password: str


def login_data() -> dict[str, AuthData]:
    return {'roomspot': AuthData(os.getenv("ROOMSPOT_LOGIN", None), os.getenv("ROOMSPOT_PASSWORD", None))}
