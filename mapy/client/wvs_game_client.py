from .client_base import ClientBase
from typing import Type

Character = Type["Character"]


class WvsGameClient(ClientBase):

    def __init__(self, parent, socket):
        super().__init__(parent, socket)

        self.channel_id = parent.channel_id
        self.character: Character | None = None
        self.npc_script = None
        self.sent_char_data = False

    async def broadcast(self, packet):
        if not self.character:
            return

        await self.character.field.broadcast(packet, self)

    def get_field(self):
        return self._parent.get_field(self.character.field_id)
