from .client_base import ClientBase


class WvsGameClient(ClientBase):
    def __init__(self, parent, socket):
        super().__init__(parent, socket)

        self.channel_id = parent.channel_id
        self.character = None
        self.npc_script = None
        self.sent_char_data = False

    def get_field(self):
        return self._parent.get_field(self.character.field_id)