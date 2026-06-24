"""
Room reaction handling for Roomspot.
"""
from urllib.parse import parse_qs
import aiohttp
from yarl import URL
from notbehomeless.models.room import Room
from notbehomeless.roomspot.room_reaction_action import RoomReactionAction


class RoomReactor:
    """
       Handles reactions for Roomspot rooms.
    """
    REACT_ROOM_URL = URL("https://www.roomspot.nl/portal/object/frontend/react/format/json")
    ROOM_GET_FORM_SUBMIT_ONLY_CONFIG = URL(
        "https://www.roomspot.nl/portal/core/frontend/getformsubmitonlyconfiguration/format/json")
    ROOMS_GET_REACTION_DATA_URL = URL("https://www.roomspot.nl/portal/object/frontend/getreagerendata/format/json")
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

    async def react_to_room(self, session: aiohttp.ClientSession, room: Room,
                            action_to_do: RoomReactionAction):
        """
            React to a room by adding or removing a reaction.
        """

        payload = self.payload_template.copy()
        payload["dwellingID"] = str(room.room_id)

        action_key = action_to_do.value

        if action_key != room.action:
            raise ValueError(
                f"Reaction URL does not contain action {action_key}"
            )

        payload[action_key] = room.action_value

        form_submit_only = await self.get_form_submit_only_config(session)
        form = form_submit_only.get("form", {})
        hash_value = form.get("elements", {}).get("__hash__", {}).get("initialData", "")
        form_id = form.get("id", "")

        payload["__hash__"] = str(hash_value)
        payload["__id__"] = str(form_id)

        async with session.post(self.REACT_ROOM_URL, data=payload) as response:
            response.raise_for_status()
            if response.status == 200:
                print(f"|Successfully react -|{action_to_do.name}|- for room:"
                      f"\n {room}\n===================")
            await self.add_room_reaction_data(session, [room])
            return await response.json()

    async def add_room_reaction_data(
            self,
            session: aiohttp.ClientSession,
            rooms: list[Room]
    ):
        params = [("objectId[]", str(room.room_id)) for room in rooms]

        data = {}
        async with session.get(self.ROOMS_GET_REACTION_DATA_URL, params=params) as response:
            response.raise_for_status()
            if response.status != 200:
                print(f"Failed to get room reaction data: {response.status}")
            data = await response.json()

        reaction_data = data.get("reagerenData", {})
        for room in rooms:
            room_reaction_data = reaction_data.get(str(room.room_id), {})
            room.can_react = room_reaction_data.get("kanReageren", False)
            room.action = room_reaction_data.get("action", "")

            url = room_reaction_data.get("url", "")

            query = parse_qs(url.lstrip("?"))
            room.action_value = str(query.get(room.action, [""])[0])
