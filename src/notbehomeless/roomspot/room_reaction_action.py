"""
Roomspot room reaction handling.
"""
from enum import Enum


class RoomReactionAction(Enum):
    """
       Available reaction actions for a Roomspot room.
       """
    ADD = "add"
    REMOVE = "remove"
