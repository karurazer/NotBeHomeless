import os
from dataclasses import dataclass
from dotenv import load_dotenv
from notbehomeless.models.WebSite import WebSite

load_dotenv()


@dataclass
class AuthData:
    login: str
    password: str


def login_data(name: WebSite) -> AuthData:

    match name:
        case WebSite.ROOMSPOT:
            return AuthData(os.getenv(f"{WebSite.ROOMSPOT.name}_LOGIN", ""), os.getenv(f"{WebSite.ROOMSPOT.name}_PASSWORD", ""))

    raise ValueError(f"No login data for {name}")

