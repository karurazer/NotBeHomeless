from enum import Enum


class AllocationType(Enum):
    """
    An enum for the different types of allocation.
    """

    COOPTATION = "cooptation"
    LOTTERY = "random"
    FIRST_COME_FIRST_SERVE = "inschrijfduur"

    @classmethod
    def from_code(cls, code: str) -> "AllocationType | None":
        try:
            return cls(code)
        except ValueError:
            return None