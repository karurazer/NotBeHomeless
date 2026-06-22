import os
from dataclasses import dataclass
from dotenv import load_dotenv
from notbehomeless.models.website import Website

load_dotenv()


@dataclass
class AuthData:
    login: str
    password: str


def login_data(name: Website) -> AuthData:
    match name:
        case Website.ROOMSPOT:
            return AuthData(os.getenv(f"{Website.ROOMSPOT.name}_LOGIN", ""),
                            os.getenv(f"{Website.ROOMSPOT.name}_PASSWORD", ""))

    raise ValueError(f"No login data for {name}")
