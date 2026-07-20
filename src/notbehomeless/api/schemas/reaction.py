"""Request DTOs for room reactions."""
from pydantic import BaseModel

from notbehomeless.websites.roomspot.room_reaction_action import RoomReactionAction


class ReactionRequest(BaseModel):
    """Desired reaction action for a room."""

    action: RoomReactionAction  # "add" | "remove", validated by FastAPI
