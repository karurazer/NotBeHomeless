"""
Room reaction handling for Roomspot.
"""
from urllib.parse import parse_qs
import aiohttp
from yarl import URL
from notbehomeless.models.Room import Room
from notbehomeless.roomspot.room_reaction_action import RoomReactionAction


class RoomReactor:
    """
       Handles reactions for Roomspot rooms.
    """
    REACT_ROOM_URL = URL("https://www.roomspot.nl/portal/object/frontend/react/format/json")
    ROOM_GET_FORM_SUBMIT_ONLY_CONFIG = URL(
        "https://www.roomspot.nl/portal/core/frontend/getformsubmitonlyconfiguration/format/json")
    payload_template = {
        "dwellingID": "",
        "__hash__": "",
        "__id__": ""
    }

    async def get_form_submit_only_config(self, session: aiohttp.ClientSession) -> dict:
        """
            Fetch submit-only form configuration from Roomspot.
        """
        async with session.get(self.ROOM_GET_FORM_SUBMIT_ONLY_CONFIG) as response:
            response.raise_for_status()
            return await response.json()

    async def react_to_room(self, session: aiohttp.ClientSession, reaction_data: dict, room: Room,
                            action_to_do: RoomReactionAction):
        """
            React to a room by adding or removing a reaction.
        """


        if not reaction_data:
            raise ValueError("No reaction data for room")

        can_react = reaction_data.get("kanReageren", False)

        if not can_react:
            raise ValueError("Cannot react to room")

        url = reaction_data.get("url", "")
        if not url:
            raise ValueError("No URL for signing up for room")

        params = parse_qs(url.lstrip("?"))
        payload = self.payload_template.copy()
        payload["dwellingID"] = str(params["dwellingID"][0])

        action_key = action_to_do.value

        if action_key not in params:
            raise ValueError(
                f"Reaction URL does not contain action {action_key}"
            )

        payload[action_key] = str(params[action_key][0])

        form_submit_only = await self.get_form_submit_only_config(session)
        form = form_submit_only.get("form", {})
        hash__ = form.get("elements", {}).get("__hash__", {}).get("initialData", "")
        id__ = form.get("id", "")

        payload["__hash__"] = str(hash__)
        payload["__id__"] = str(id__)

        async with session.post(self.REACT_ROOM_URL, data=payload) as response:
            response.raise_for_status()
            if response.status == 200:
                print(f"|Successfully react -|{action_to_do.name}|- for room:"
                      f"\n {room}\n===================")
            return await response.json()
