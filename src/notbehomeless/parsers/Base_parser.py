from abc import ABC, abstractmethod


class BaseParser(ABC):
    source_name: str

    @abstractmethod
    async def fetch_listings(self) -> list:
        pass