"""
Roomspot room reaction handling.
"""
from enum import StrEnum


class RoomReactionAction(StrEnum):
    """
       Available reaction actions for a Roomspot room.
       """
    ADD = "add"
    REMOVE = "remove"
